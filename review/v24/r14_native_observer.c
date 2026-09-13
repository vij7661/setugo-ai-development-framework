#define _GNU_SOURCE
#include <Python.h>
#include <openssl/evp.h>
#include <openssl/hmac.h>
#include <openssl/crypto.h>
#include <sys/random.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define KEY_BYTES 32
#define MAX_REQUEST (8u * 1024u * 1024u)
#define MAX_FRAME (16u * 1024u * 1024u)
#define PREFIX "R14_NATIVE_OBSERVATION="

typedef struct { char *p; size_t n; size_t cap; } Buf;

static void die(const char *m) { fprintf(stderr, "%s\n", m); exit(2); }
static void child_die(int fd, const char *m) { (void)fd; fprintf(stderr, "%s\n", m); _exit(111); }

static void binit(Buf *b) { memset(b, 0, sizeof(*b)); }
static void bgrow(Buf *b, size_t add) {
    if (add > MAX_FRAME || b->n > MAX_FRAME - add) die("R14_NATIVE_BUFFER_LIMIT");
    size_t need=b->n+add+1;
    if (need<=b->cap) return;
    size_t cap=b->cap?b->cap:1024;
    while (cap<need) { if (cap>MAX_FRAME/2) cap=MAX_FRAME; else cap*=2; }
    char *p=(char*)realloc(b->p,cap); if(!p) die("R14_NATIVE_OOM"); b->p=p; b->cap=cap;
}
static void bputn(Buf *b,const char *s,size_t n){bgrow(b,n);memcpy(b->p+b->n,s,n);b->n+=n;b->p[b->n]=0;}
static void bput(Buf *b,const char *s){bputn(b,s,strlen(s));}
static void bch(Buf *b,char c){bgrow(b,1);b->p[b->n++]=c;b->p[b->n]=0;}

static void json_string(Buf *b,const char *s,size_t n){
    static const char hex[]="0123456789abcdef"; bch(b,'"');
    for(size_t i=0;i<n;i++){ unsigned char c=(unsigned char)s[i];
        switch(c){case '"':bput(b,"\\\"");break;case '\\':bput(b,"\\\\");break;case '\b':bput(b,"\\b");break;case '\f':bput(b,"\\f");break;case '\n':bput(b,"\\n");break;case '\r':bput(b,"\\r");break;case '\t':bput(b,"\\t");break;
        default: if(c<0x20){char u[7]={'\\','u','0','0',hex[c>>4],hex[c&15],0};bput(b,u);} else bch(b,(char)c); }
    } bch(b,'"');
}

static int serialize_obj(Buf *b,PyObject *o,int depth){
    if(depth>64) return -1;
    if(o==Py_None){bput(b,"null");return 0;}
    if(o==Py_True){bput(b,"true");return 0;} if(o==Py_False){bput(b,"false");return 0;}
    if(PyLong_CheckExact(o)||PyFloat_CheckExact(o)){
        PyObject *s=PyObject_Str(o); if(!s) return -1; Py_ssize_t n=0; const char *p=PyUnicode_AsUTF8AndSize(s,&n); if(!p){Py_DECREF(s);return -1;} bputn(b,p,(size_t)n); Py_DECREF(s); return 0;
    }
    if(PyUnicode_CheckExact(o)){Py_ssize_t n=0;const char *p=PyUnicode_AsUTF8AndSize(o,&n);if(!p)return -1;json_string(b,p,(size_t)n);return 0;}
    if(PyList_CheckExact(o)||PyTuple_CheckExact(o)){
        Py_ssize_t n=PySequence_Size(o); if(n<0)return -1; bch(b,'[');
        for(Py_ssize_t i=0;i<n;i++){if(i)bch(b,',');PyObject *v=PySequence_GetItem(o,i);if(!v)return -1;int rc=serialize_obj(b,v,depth+1);Py_DECREF(v);if(rc)return rc;} bch(b,']');return 0;
    }
    if(PyDict_CheckExact(o)){
        bch(b,'{');Py_ssize_t pos=0;PyObject *k,*v;int first=1;
        while(PyDict_Next(o,&pos,&k,&v)){if(!PyUnicode_CheckExact(k))return -1;if(!first)bch(b,',');first=0;Py_ssize_t n=0;const char *p=PyUnicode_AsUTF8AndSize(k,&n);if(!p)return -1;json_string(b,p,(size_t)n);bch(b,':');if(serialize_obj(b,v,depth+1))return -1;} bch(b,'}');return 0;
    }
    return -1;
}

static int starts(const char *s,const char *p){return s&&p&&strncmp(s,p,strlen(p))==0;}
static int banned_import(const char *n){
    const char *bad[]={"ctypes","_ctypes","cffi","_cffi_backend","mmap","subprocess","multiprocessing","_multiprocessing","socket","_socket","resource","fcntl","pty","signal","_posixsubprocess","threading","_thread","concurrent","asyncio",NULL};
    for(int i=0;bad[i];i++) if(strcmp(n,bad[i])==0||starts(n,bad[i])&&n[strlen(bad[i])]=='.') return 1;
    if(starts(n,"_test")||starts(n,"test.")) return 1; return 0;
}
static int audit_hook(const char *event,PyObject *args,void *ud){
    (void)ud;
    const char *blocked[]={"sys._getframe","sys.settrace","sys.setprofile","os.system","os.exec","os.posix_spawn","os.fork","os.forkpty","os.kill","os.killpg","subprocess.Popen","socket.__new__","ctypes.dlopen",NULL};
    for(int i=0;blocked[i];i++) if(strcmp(event,blocked[i])==0){PyErr_Format(PyExc_PermissionError,"R14_AUDIT_BLOCK:%s",event);return -1;}
    if(strcmp(event,"import")==0&&PyTuple_Check(args)&&PyTuple_GET_SIZE(args)>0){PyObject *x=PyTuple_GET_ITEM(args,0);if(PyUnicode_Check(x)){const char *n=PyUnicode_AsUTF8(x);if(n&&banned_import(n)){PyErr_Format(PyExc_PermissionError,"R14_AUDIT_IMPORT_BLOCK:%s",n);return -1;}}}
    if(strcmp(event,"open")==0&&PyTuple_Check(args)&&PyTuple_GET_SIZE(args)>0){PyObject *x=PyTuple_GET_ITEM(args,0);if(PyUnicode_Check(x)){const char *p=PyUnicode_AsUTF8(x);if(p&&(starts(p,"/proc/")||starts(p,"/sys/")||strcmp(p,"/dev/mem")==0||strcmp(p,"/dev/kmem")==0)){PyErr_Format(PyExc_PermissionError,"R14_AUDIT_PATH_BLOCK:%s",p);return -1;}}}
    return 0;
}

static unsigned char *read_file(const char *path,size_t *len){
    int fd=open(path,O_RDONLY|O_CLOEXEC);if(fd<0)die("R14_REQUEST_OPEN_FAILED");
    size_t cap=4096,n=0;unsigned char *p=(unsigned char*)malloc(cap);if(!p)die("R14_OOM");
    for(;;){if(n==cap){if(cap>=MAX_REQUEST)die("R14_REQUEST_TOO_LARGE");cap*=2;unsigned char*q=(unsigned char*)realloc(p,cap);if(!q)die("R14_OOM");p=q;}ssize_t r=read(fd,p+n,cap-n);if(r<0){if(errno==EINTR)continue;die("R14_REQUEST_READ_FAILED");}if(r==0)break;n+=(size_t)r;if(n>MAX_REQUEST)die("R14_REQUEST_TOO_LARGE");}
    close(fd);*len=n;return p;
}
static void sha256(const unsigned char *p,size_t n,unsigned char out[32]){EVP_MD_CTX*c=EVP_MD_CTX_new();if(!c)die("R14_SHA_CTX");if(EVP_DigestInit_ex(c,EVP_sha256(),NULL)!=1||EVP_DigestUpdate(c,p,n)!=1||EVP_DigestFinal_ex(c,out,NULL)!=1)die("R14_SHA_FAIL");EVP_MD_CTX_free(c);}
static void hex32(const unsigned char in[32],char out[65]){static const char h[]="0123456789abcdef";for(int i=0;i<32;i++){out[i*2]=h[in[i]>>4];out[i*2+1]=h[in[i]&15];}out[64]=0;}
static int ct_eq(const unsigned char*a,const unsigned char*b,size_t n){unsigned char x=0;for(size_t i=0;i<n;i++)x|=a[i]^b[i];return x==0;}
static int write_all(int fd,const void *vp,size_t n){const unsigned char*p=(const unsigned char*)vp;while(n){ssize_t w=write(fd,p,n);if(w<0){if(errno==EINTR)continue;return -1;}p+=w;n-=(size_t)w;}return 0;}

static void child_main(int outfd,const unsigned char key[KEY_BYTES],const unsigned char *req,size_t req_n,const char req_hex[65],const char *sandbox){
    PyConfig cfg;PyConfig_InitIsolatedConfig(&cfg);cfg.site_import=0;cfg.use_environment=0;cfg.user_site_directory=0;cfg.safe_path=1;cfg.write_bytecode=0;cfg.parse_argv=0;
    PyStatus st=Py_InitializeFromConfig(&cfg);PyConfig_Clear(&cfg);if(PyStatus_Exception(st))child_die(outfd,"R14_CHILD_PY_INIT_FAILED");
    if(PySys_AddAuditHook(audit_hook,NULL)<0)child_die(outfd,"R14_CHILD_AUDIT_HOOK_FAILED");

    PyObject *json=PyImport_ImportModule("json");if(!json)child_die(outfd,"R14_CHILD_JSON_IMPORT_FAILED");PyObject*loads=PyObject_GetAttrString(json,"loads");Py_DECREF(json);if(!loads)child_die(outfd,"R14_CHILD_JSON_LOADS_MISSING");
    PyObject *txt=PyUnicode_DecodeUTF8((const char*)req,(Py_ssize_t)req_n,"strict");if(!txt)child_die(outfd,"R14_CHILD_REQUEST_UTF8_INVALID");PyObject*request=PyObject_CallOneArg(loads,txt);Py_DECREF(loads);Py_DECREF(txt);if(!request||!PyDict_CheckExact(request))child_die(outfd,"R14_CHILD_REQUEST_JSON_INVALID");
    PyObject *m=PyDict_GetItemString(request,"module"),*f=PyDict_GetItemString(request,"function"),*a=PyDict_GetItemString(request,"args"),*k=PyDict_GetItemString(request,"kwargs");
    if(!m||!f||!a||!k||!PyUnicode_CheckExact(m)||!PyUnicode_CheckExact(f)||!PyList_CheckExact(a)||!PyDict_CheckExact(k))child_die(outfd,"R14_CHILD_REQUEST_SHAPE_INVALID");
    const char *mod=PyUnicode_AsUTF8(m),*fun=PyUnicode_AsUTF8(f);if(!mod||!fun)child_die(outfd,"R14_CHILD_REQUEST_NAME_INVALID");

    char subject[4096];if(snprintf(subject,sizeof(subject),"%s/governance-runtime",sandbox)<=0||(size_t)snprintf(NULL,0,"%s/governance-runtime",sandbox)>=sizeof(subject))child_die(outfd,"R14_CHILD_SANDBOX_PATH_TOO_LONG");
    PyObject *path=PySys_GetObject("path");PyObject *sp=PyUnicode_FromString(subject);if(!path||!sp||PyList_Insert(path,0,sp)<0)child_die(outfd,"R14_CHILD_PATH_INSERT_FAILED");Py_DECREF(sp);

    PyObject *module=PyImport_ImportModule(mod);if(!module)child_die(outfd,"R14_CHILD_CANDIDATE_IMPORT_FAILED");PyObject *call=PyObject_GetAttrString(module,fun);Py_DECREF(module);if(!call||!PyCallable_Check(call))child_die(outfd,"R14_CHILD_TARGET_NOT_CALLABLE");PyObject *args=PyList_AsTuple(a);if(!args)child_die(outfd,"R14_CHILD_ARGS_INVALID");
    PyObject *result=PyObject_Call(call,args,k);Py_DECREF(args);Py_DECREF(call);

    Buf payload;binit(&payload);bput(&payload,"{\"schema_version\":1,\"request_digest\":");json_string(&payload,req_hex,64);bput(&payload,",\"module\":");json_string(&payload,mod,strlen(mod));bput(&payload,",\"function\":");json_string(&payload,fun,strlen(fun));
    if(result){bput(&payload,",\"outcome_kind\":\"RETURN\",\"payload\":");if(serialize_obj(&payload,result,0))child_die(outfd,"R14_CHILD_RESULT_NOT_PLAIN_DATA");Py_DECREF(result);}else{
        PyObject *type=NULL,*value=NULL,*tb=NULL;PyErr_Fetch(&type,&value,&tb);PyErr_NormalizeException(&type,&value,&tb);const char *tn="Exception";if(type){PyObject*n=PyObject_GetAttrString(type,"__name__");if(n&&PyUnicode_Check(n)){const char*x=PyUnicode_AsUTF8(n);if(x)tn=x;}Py_XDECREF(n);}PyObject*vs=value?PyObject_Str(value):NULL;const char*msg=vs&&PyUnicode_Check(vs)?PyUnicode_AsUTF8(vs):"";
        bput(&payload,",\"outcome_kind\":\"EXCEPTION\",\"payload\":{\"exception_type\":");json_string(&payload,tn,strlen(tn));bput(&payload,",\"message\":");json_string(&payload,msg?msg:"",msg?strlen(msg):0);bch(&payload,'}');Py_XDECREF(vs);Py_XDECREF(type);Py_XDECREF(value);Py_XDECREF(tb);
    }
    bput(&payload,",\"candidate_process_role\":\"UNTRUSTED_EXECUTION_ONLY\",\"authority_effect\":\"NONE_EVIDENCE_ONLY\",\"observation_transport\":\"NATIVE_PARENT_AUTHENTICATED_FRAME\",\"native_parent_initializes_python\":false}");

    unsigned char mac[EVP_MAX_MD_SIZE];unsigned int mac_n=0;if(!HMAC(EVP_sha256(),key,KEY_BYTES,(unsigned char*)payload.p,payload.n,mac,&mac_n)||mac_n!=32)child_die(outfd,"R14_CHILD_HMAC_FAILED");char mh[65];hex32(mac,mh);char head[128];int hn=snprintf(head,sizeof(head),"R14F1\n%s\n%zu\n",mh,payload.n);if(hn<=0||(size_t)hn>=sizeof(head))child_die(outfd,"R14_CHILD_FRAME_HEADER_FAILED");
    if(write_all(outfd,head,(size_t)hn)||write_all(outfd,payload.p,payload.n))child_die(outfd,"R14_CHILD_FRAME_WRITE_FAILED");
    OPENSSL_cleanse(mac,sizeof(mac));free(payload.p);Py_DECREF(request);OPENSSL_cleanse((void*)key,KEY_BYTES);_exit(0);
}

static unsigned char *read_pipe_all(int fd,size_t *n){size_t cap=4096,used=0;unsigned char*p=(unsigned char*)malloc(cap);if(!p)die("R14_OOM");for(;;){if(used==cap){if(cap>=MAX_FRAME)die("R14_FRAME_TOO_LARGE");cap*=2;unsigned char*q=(unsigned char*)realloc(p,cap);if(!q)die("R14_OOM");p=q;}ssize_t r=read(fd,p+used,cap-used);if(r<0){if(errno==EINTR)continue;die("R14_PIPE_READ_FAILED");}if(r==0)break;used+=(size_t)r;if(used>MAX_FRAME)die("R14_FRAME_TOO_LARGE");}*n=used;return p;}

int main(int argc,char **argv){
    const char *sandbox=NULL,*request_path=NULL;for(int i=1;i<argc;i++){if(strcmp(argv[i],"--sandbox")==0&&i+1<argc)sandbox=argv[++i];else if(strcmp(argv[i],"--request")==0&&i+1<argc)request_path=argv[++i];else die("R14_NATIVE_ARGS_INVALID");}if(!sandbox||!request_path)die("R14_NATIVE_REQUIRED_ARGS_MISSING");
    size_t req_n=0;unsigned char*req=read_file(request_path,&req_n);unsigned char rd[32];sha256(req,req_n,rd);char req_hex[65];hex32(rd,req_hex);
    unsigned char key[KEY_BYTES];ssize_t gr=getrandom(key,sizeof(key),0);if(gr!=(ssize_t)sizeof(key))die("R14_NATIVE_GETRANDOM_FAILED");int pfd[2];if(pipe2(pfd,O_CLOEXEC)<0)die("R14_NATIVE_PIPE_FAILED");pid_t pid=fork();if(pid<0)die("R14_NATIVE_FORK_FAILED");
    if(pid==0){close(pfd[0]);child_main(pfd[1],key,req,req_n,req_hex,sandbox);}
    close(pfd[1]);OPENSSL_cleanse(req,req_n);free(req);size_t frame_n=0;unsigned char*frame=read_pipe_all(pfd[0],&frame_n);close(pfd[0]);int status=0;if(waitpid(pid,&status,0)!=pid)die("R14_NATIVE_WAIT_FAILED");if(!WIFEXITED(status)||WEXITSTATUS(status)!=0){free(frame);OPENSSL_cleanse(key,sizeof(key));die("R14_NATIVE_CHILD_NOT_CLEAN_EXIT");}
    const char *magic="R14F1\n";size_t ml=strlen(magic);if(frame_n<ml+64+1+2||memcmp(frame,magic,ml)!=0)die("R14_NATIVE_FRAME_MAGIC_INVALID");size_t off=ml;if(off+64>=frame_n||frame[off+64]!='\n')die("R14_NATIVE_FRAME_MAC_INVALID");char mh[65];memcpy(mh,frame+off,64);mh[64]=0;off+=65;size_t len_start=off;while(off<frame_n&&frame[off]!='\n'){if(frame[off]<'0'||frame[off]>'9')die("R14_NATIVE_FRAME_LENGTH_INVALID");off++;}if(off==frame_n||off-len_start>20)die("R14_NATIVE_FRAME_LENGTH_INVALID");char ls[32];memcpy(ls,frame+len_start,off-len_start);ls[off-len_start]=0;off++;char*end=NULL;unsigned long long want=strtoull(ls,&end,10);if(!end||*end)die("R14_NATIVE_FRAME_LENGTH_INVALID");if(want>MAX_FRAME||off+(size_t)want!=frame_n)die("R14_NATIVE_FRAME_EXACT_LENGTH_REQUIRED");
    unsigned char expected[EVP_MAX_MD_SIZE];unsigned int en=0;if(!HMAC(EVP_sha256(),key,KEY_BYTES,frame+off,(size_t)want,expected,&en)||en!=32)die("R14_NATIVE_PARENT_HMAC_FAILED");char eh[65];hex32(expected,eh);unsigned char mhb[32];for(int i=0;i<32;i++){char tmp[3]={mh[i*2],mh[i*2+1],0};char*e2=NULL;long v=strtol(tmp,&e2,16);if(!e2||*e2)die("R14_NATIVE_FRAME_MAC_HEX_INVALID");mhb[i]=(unsigned char)v;}if(!ct_eq(expected,mhb,32))die("R14_NATIVE_FRAME_AUTH_FAILED");
    OPENSSL_cleanse(key,sizeof(key));OPENSSL_cleanse(expected,sizeof(expected));if(write_all(STDOUT_FILENO,PREFIX,strlen(PREFIX))||write_all(STDOUT_FILENO,frame+off,(size_t)want)||write_all(STDOUT_FILENO,"\n",1))die("R14_NATIVE_STDOUT_FAILED");free(frame);return 0;
}
