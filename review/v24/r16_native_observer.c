#define _GNU_SOURCE
#include <Python.h>
#include <errno.h>
#include <fcntl.h>
#include <linux/audit.h>
#include <linux/filter.h>
#include <linux/landlock.h>
#include <linux/seccomp.h>
#include <openssl/evp.h>
#include <signal.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/prctl.h>
#include <sys/random.h>
#include <sys/syscall.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

#ifndef R16_PYTHON_HOME
#define R16_PYTHON_HOME "/usr"
#endif
#ifndef R16_PYTHON_PROGRAM
#define R16_PYTHON_PROGRAM "/usr/bin/python3"
#endif
#ifndef SYS_landlock_create_ruleset
#if defined(__x86_64__)
#define SYS_landlock_create_ruleset 444
#define SYS_landlock_add_rule 445
#define SYS_landlock_restrict_self 446
#else
#error "Landlock syscall numbers unavailable for this architecture"
#endif
#endif

#define MAX_REQUEST (8u * 1024u * 1024u)
#define MAX_FRAME (16u * 1024u * 1024u)
#define PREFIX "R16_NATIVE_OBSERVATION="
#define CHILD_FD 3

typedef struct { char *p; size_t n; size_t cap; } Buf;

static void die(const char *m) { fprintf(stderr, "%s\n", m); exit(2); }
static void best_effort_write(int fd, const char *p, size_t n) {
    while (n > 0) {
        ssize_t w = write(fd, p, n);
        if (w < 0) {
            if (errno == EINTR) continue;
            return;
        }
        p += (size_t)w;
        n -= (size_t)w;
    }
}
static void child_die(int fd, const char *m) {
    if (fd >= 0) {
        best_effort_write(fd, "R16E1\n", 6);
        best_effort_write(fd, m, strlen(m));
        best_effort_write(fd, "\n", 1);
    }
    _exit(111);
}

static void binit(Buf *b) { memset(b, 0, sizeof(*b)); }
static void bgrow(Buf *b, size_t add) {
    if (add > MAX_FRAME || b->n > MAX_FRAME - add) die("R16_NATIVE_BUFFER_LIMIT");
    size_t need = b->n + add + 1;
    if (need <= b->cap) return;
    size_t cap = b->cap ? b->cap : 1024;
    while (cap < need) {
        if (cap > MAX_FRAME / 2) cap = MAX_FRAME;
        else cap *= 2;
    }
    char *p = (char *)realloc(b->p, cap);
    if (!p) die("R16_NATIVE_OOM");
    b->p = p; b->cap = cap;
}
static void bputn(Buf *b, const char *s, size_t n) { bgrow(b,n); memcpy(b->p+b->n,s,n); b->n+=n; b->p[b->n]=0; }
static void bput(Buf *b, const char *s) { bputn(b,s,strlen(s)); }
static void bch(Buf *b, char c) { bgrow(b,1); b->p[b->n++]=c; b->p[b->n]=0; }

static void json_string(Buf *b, const char *s, size_t n) {
    static const char hex[]="0123456789abcdef"; bch(b,'"');
    for (size_t i=0;i<n;i++) {
        unsigned char c=(unsigned char)s[i];
        switch(c) {
            case '"': bput(b,"\\\""); break;
            case '\\': bput(b,"\\\\"); break;
            case '\b': bput(b,"\\b"); break;
            case '\f': bput(b,"\\f"); break;
            case '\n': bput(b,"\\n"); break;
            case '\r': bput(b,"\\r"); break;
            case '\t': bput(b,"\\t"); break;
            default:
                if (c < 0x20) { char u[7]={'\\','u','0','0',hex[c>>4],hex[c&15],0}; bput(b,u); }
                else bch(b,(char)c);
        }
    }
    bch(b,'"');
}

static int serialize_obj(Buf *b, PyObject *o, int depth) {
    if (depth > 64) return -1;
    if (o == Py_None) { bput(b,"null"); return 0; }
    if (o == Py_True) { bput(b,"true"); return 0; }
    if (o == Py_False) { bput(b,"false"); return 0; }
    if (PyLong_CheckExact(o) || PyFloat_CheckExact(o)) {
        PyObject *s=PyObject_Str(o); if(!s) return -1;
        Py_ssize_t n=0; const char *p=PyUnicode_AsUTF8AndSize(s,&n);
        if(!p){Py_DECREF(s);return -1;} bputn(b,p,(size_t)n); Py_DECREF(s); return 0;
    }
    if (PyUnicode_CheckExact(o)) {
        Py_ssize_t n=0; const char *p=PyUnicode_AsUTF8AndSize(o,&n); if(!p) return -1;
        json_string(b,p,(size_t)n); return 0;
    }
    if (PyList_CheckExact(o) || PyTuple_CheckExact(o)) {
        Py_ssize_t n=PySequence_Size(o); if(n<0) return -1; bch(b,'[');
        for(Py_ssize_t i=0;i<n;i++) { if(i)bch(b,','); PyObject *v=PySequence_GetItem(o,i); if(!v)return -1; int rc=serialize_obj(b,v,depth+1); Py_DECREF(v); if(rc)return rc; }
        bch(b,']'); return 0;
    }
    if (PyDict_CheckExact(o)) {
        bch(b,'{'); Py_ssize_t pos=0; PyObject *k,*v; int first=1;
        while(PyDict_Next(o,&pos,&k,&v)) {
            if(!PyUnicode_CheckExact(k)) return -1;
            if(!first) {
                bch(b,',');
            }
            first=0;
            Py_ssize_t n=0; const char *p=PyUnicode_AsUTF8AndSize(k,&n); if(!p)return -1;
            json_string(b,p,(size_t)n); bch(b,':'); if(serialize_obj(b,v,depth+1))return -1;
        }
        bch(b,'}'); return 0;
    }
    return -1;
}

static int starts(const char *s,const char *p){return s&&p&&strncmp(s,p,strlen(p))==0;}
static int banned_import(const char *n) {
    const char *bad[]={"ctypes","_ctypes","cffi","_cffi_backend","mmap","subprocess","multiprocessing","_multiprocessing","socket","_socket","resource","fcntl","pty","signal","_posixsubprocess","threading","_thread","concurrent","asyncio",NULL};
    for(int i=0;bad[i];i++) if(strcmp(n,bad[i])==0 || (starts(n,bad[i]) && n[strlen(bad[i])]=='.')) return 1;
    if(starts(n,"_test")||starts(n,"test.")) return 1;
    return 0;
}
static int audit_hook(const char *event, PyObject *args, void *ud) {
    (void)ud;
    const char *blocked[]={"sys._getframe","sys.settrace","sys.setprofile","os.system","os.exec","os.posix_spawn","os.fork","os.forkpty","os.kill","os.killpg","subprocess.Popen","socket.__new__","ctypes.dlopen",NULL};
    for(int i=0;blocked[i];i++) if(strcmp(event,blocked[i])==0){PyErr_Format(PyExc_PermissionError,"R16_AUDIT_BLOCK:%s",event);return -1;}
    if(strcmp(event,"import")==0 && PyTuple_Check(args) && PyTuple_GET_SIZE(args)>0) {
        PyObject *x=PyTuple_GET_ITEM(args,0);
        if(PyUnicode_Check(x)) { const char *n=PyUnicode_AsUTF8(x); if(n&&banned_import(n)){PyErr_Format(PyExc_PermissionError,"R16_AUDIT_IMPORT_BLOCK:%s",n);return -1;} }
    }
    return 0;
}

static unsigned char *read_file(const char *path,size_t *len) {
    int fd=open(path,O_RDONLY|O_CLOEXEC); if(fd<0) die("R16_REQUEST_OPEN_FAILED");
    size_t cap=4096,n=0; unsigned char *p=(unsigned char*)malloc(cap); if(!p)die("R16_OOM");
    for(;;) {
        if(n==cap){if(cap>=MAX_REQUEST)die("R16_REQUEST_TOO_LARGE");cap*=2;unsigned char*q=(unsigned char*)realloc(p,cap);if(!q)die("R16_OOM");p=q;}
        ssize_t r=read(fd,p+n,cap-n); if(r<0){if(errno==EINTR)continue;die("R16_REQUEST_READ_FAILED");} if(r==0)break;
        n+=(size_t)r; if(n>MAX_REQUEST)die("R16_REQUEST_TOO_LARGE");
    }
    close(fd); *len=n; return p;
}
static void sha256(const unsigned char *p,size_t n,unsigned char out[32]) {
    EVP_MD_CTX*c=EVP_MD_CTX_new(); if(!c)die("R16_SHA_CTX");
    if(EVP_DigestInit_ex(c,EVP_sha256(),NULL)!=1||EVP_DigestUpdate(c,p,n)!=1||EVP_DigestFinal_ex(c,out,NULL)!=1)die("R16_SHA_FAIL");
    EVP_MD_CTX_free(c);
}
static void sha256_2(const unsigned char *a,size_t an,const unsigned char *b,size_t bn,unsigned char out[32]) {
    EVP_MD_CTX*c=EVP_MD_CTX_new(); if(!c)die("R16_SHA_CTX");
    if(EVP_DigestInit_ex(c,EVP_sha256(),NULL)!=1||EVP_DigestUpdate(c,a,an)!=1||EVP_DigestUpdate(c,b,bn)!=1||EVP_DigestFinal_ex(c,out,NULL)!=1)die("R16_SHA_FAIL");
    EVP_MD_CTX_free(c);
}
static void hex32(const unsigned char in[32],char out[65]){static const char h[]="0123456789abcdef";for(int i=0;i<32;i++){out[i*2]=h[in[i]>>4];out[i*2+1]=h[in[i]&15];}out[64]=0;}
static int write_all(int fd,const void *vp,size_t n){const unsigned char*p=(const unsigned char*)vp;while(n){ssize_t w=write(fd,p,n);if(w<0){if(errno==EINTR)continue;return -1;}p+=w;n-=(size_t)w;}return 0;}

static int ll_create(const struct landlock_ruleset_attr *attr,size_t size,__u32 flags){return(int)syscall(SYS_landlock_create_ruleset,attr,size,flags);}
static int ll_add(int rs,const struct landlock_path_beneath_attr *rule,__u32 flags){return(int)syscall(SYS_landlock_add_rule,rs,LANDLOCK_RULE_PATH_BENEATH,rule,flags);}
static int ll_restrict(int rs,__u32 flags){return(int)syscall(SYS_landlock_restrict_self,rs,flags);}

static __u64 landlock_handled(int abi) {
    __u64 v=LANDLOCK_ACCESS_FS_EXECUTE|LANDLOCK_ACCESS_FS_WRITE_FILE|LANDLOCK_ACCESS_FS_READ_FILE|LANDLOCK_ACCESS_FS_READ_DIR|
        LANDLOCK_ACCESS_FS_REMOVE_DIR|LANDLOCK_ACCESS_FS_REMOVE_FILE|LANDLOCK_ACCESS_FS_MAKE_CHAR|LANDLOCK_ACCESS_FS_MAKE_DIR|
        LANDLOCK_ACCESS_FS_MAKE_REG|LANDLOCK_ACCESS_FS_MAKE_SOCK|LANDLOCK_ACCESS_FS_MAKE_FIFO|LANDLOCK_ACCESS_FS_MAKE_BLOCK|LANDLOCK_ACCESS_FS_MAKE_SYM;
#ifdef LANDLOCK_ACCESS_FS_REFER
    if(abi>=2)v|=LANDLOCK_ACCESS_FS_REFER;
#endif
#ifdef LANDLOCK_ACCESS_FS_TRUNCATE
    if(abi>=3)v|=LANDLOCK_ACCESS_FS_TRUNCATE;
#endif
#ifdef LANDLOCK_ACCESS_FS_IOCTL_DEV
    if(abi>=5)v|=LANDLOCK_ACCESS_FS_IOCTL_DEV;
#endif
    return v;
}

static void landlock_allow(int rs,const char *path,__u64 access) {
    int fd=open(path,O_PATH|O_CLOEXEC); if(fd<0) return;
    struct landlock_path_beneath_attr rule={.allowed_access=access,.parent_fd=fd};
    if(ll_add(rs,&rule,0)!=0){close(fd);child_die(CHILD_FD,"R16_LANDLOCK_ADD_RULE_FAILED");}
    close(fd);
}

static int apply_landlock(const char *sandbox) {
    int abi=ll_create(NULL,0,LANDLOCK_CREATE_RULESET_VERSION); if(abi<1)child_die(CHILD_FD,"R16_LANDLOCK_ABI_UNAVAILABLE");
    __u64 handled=landlock_handled(abi);
    struct landlock_ruleset_attr attr={.handled_access_fs=handled};
    int rs=ll_create(&attr,sizeof(attr),0); if(rs<0)child_die(CHILD_FD,"R16_LANDLOCK_RULESET_CREATE_FAILED");
    __u64 ro=LANDLOCK_ACCESS_FS_EXECUTE|LANDLOCK_ACCESS_FS_READ_FILE|LANDLOCK_ACCESS_FS_READ_DIR;
    landlock_allow(rs,sandbox,ro);
    landlock_allow(rs,R16_PYTHON_HOME,ro);
    landlock_allow(rs,"/usr/lib",ro);
    landlock_allow(rs,"/usr/lib64",ro);
    landlock_allow(rs,"/lib",ro);
    landlock_allow(rs,"/lib64",ro);
    landlock_allow(rs,"/etc",LANDLOCK_ACCESS_FS_READ_FILE|LANDLOCK_ACCESS_FS_READ_DIR);
    if(prctl(PR_SET_NO_NEW_PRIVS,1,0,0,0)!=0)child_die(CHILD_FD,"R16_NO_NEW_PRIVS_FAILED");
    if(ll_restrict(rs,0)!=0)child_die(CHILD_FD,"R16_LANDLOCK_RESTRICT_FAILED");
    close(rs); return abi;
}

#define DENY_SYSCALL(nr) \
    BPF_JUMP(BPF_JMP|BPF_JEQ|BPF_K,(nr),0,1), \
    BPF_STMT(BPF_RET|BPF_K,SECCOMP_RET_ERRNO | (EPERM & SECCOMP_RET_DATA))

static void apply_seccomp(void) {
    struct sock_filter filter[] = {
        BPF_STMT(BPF_LD|BPF_W|BPF_ABS,(offsetof(struct seccomp_data,arch))),
        BPF_JUMP(BPF_JMP|BPF_JEQ|BPF_K,AUDIT_ARCH_X86_64,1,0),
        BPF_STMT(BPF_RET|BPF_K,SECCOMP_RET_KILL_PROCESS),
        BPF_STMT(BPF_LD|BPF_W|BPF_ABS,(offsetof(struct seccomp_data,nr))),
#ifdef __NR_ptrace
        DENY_SYSCALL(__NR_ptrace),
#endif
#ifdef __NR_process_vm_readv
        DENY_SYSCALL(__NR_process_vm_readv),
#endif
#ifdef __NR_process_vm_writev
        DENY_SYSCALL(__NR_process_vm_writev),
#endif
#ifdef __NR_pidfd_open
        DENY_SYSCALL(__NR_pidfd_open),
#endif
#ifdef __NR_pidfd_getfd
        DENY_SYSCALL(__NR_pidfd_getfd),
#endif
#ifdef __NR_pidfd_send_signal
        DENY_SYSCALL(__NR_pidfd_send_signal),
#endif
#ifdef __NR_open_by_handle_at
        DENY_SYSCALL(__NR_open_by_handle_at),
#endif
#ifdef __NR_name_to_handle_at
        DENY_SYSCALL(__NR_name_to_handle_at),
#endif
#ifdef __NR_mount
        DENY_SYSCALL(__NR_mount),
#endif
#ifdef __NR_umount2
        DENY_SYSCALL(__NR_umount2),
#endif
#ifdef __NR_pivot_root
        DENY_SYSCALL(__NR_pivot_root),
#endif
#ifdef __NR_unshare
        DENY_SYSCALL(__NR_unshare),
#endif
#ifdef __NR_setns
        DENY_SYSCALL(__NR_setns),
#endif
#ifdef __NR_bpf
        DENY_SYSCALL(__NR_bpf),
#endif
#ifdef __NR_perf_event_open
        DENY_SYSCALL(__NR_perf_event_open),
#endif
#ifdef __NR_userfaultfd
        DENY_SYSCALL(__NR_userfaultfd),
#endif
#ifdef __NR_io_uring_setup
        DENY_SYSCALL(__NR_io_uring_setup),
#endif
#ifdef __NR_execve
        DENY_SYSCALL(__NR_execve),
#endif
#ifdef __NR_execveat
        DENY_SYSCALL(__NR_execveat),
#endif
#ifdef __NR_fork
        DENY_SYSCALL(__NR_fork),
#endif
#ifdef __NR_vfork
        DENY_SYSCALL(__NR_vfork),
#endif
#ifdef __NR_clone
        DENY_SYSCALL(__NR_clone),
#endif
#ifdef __NR_clone3
        DENY_SYSCALL(__NR_clone3),
#endif
#ifdef __NR_socket
        DENY_SYSCALL(__NR_socket),
#endif
#ifdef __NR_socketpair
        DENY_SYSCALL(__NR_socketpair),
#endif
#ifdef __NR_kill
        DENY_SYSCALL(__NR_kill),
#endif
#ifdef __NR_tkill
        DENY_SYSCALL(__NR_tkill),
#endif
#ifdef __NR_tgkill
        DENY_SYSCALL(__NR_tgkill),
#endif
        BPF_STMT(BPF_RET|BPF_K,SECCOMP_RET_ALLOW),
    };
    struct sock_fprog prog={.len=(unsigned short)(sizeof(filter)/sizeof(filter[0])),.filter=filter};
    if(prctl(PR_SET_NO_NEW_PRIVS,1,0,0,0)!=0)child_die(CHILD_FD,"R16_SECCOMP_NO_NEW_PRIVS_FAILED");
    if(prctl(PR_SET_SECCOMP,SECCOMP_MODE_FILTER,&prog)!=0)child_die(CHILD_FD,"R16_SECCOMP_INSTALL_FAILED");
}

static void close_child_fds(int writefd) {
    if(writefd!=CHILD_FD){if(dup2(writefd,CHILD_FD)<0)_exit(112);close(writefd);}
    close(STDIN_FILENO); close(STDOUT_FILENO); close(STDERR_FILENO);
#ifdef __NR_close_range
    (void)syscall(__NR_close_range,4u,~0u,0u);
#else
    for(int fd=4;fd<1024;fd++)close(fd);
#endif
}

static void child_main(int outfd,const unsigned char *req,size_t req_n,const char req_hex[65],const char *sandbox) {
    close_child_fds(outfd);
    if(chdir(sandbox)!=0)child_die(CHILD_FD,"R16_CHILD_CHDIR_FAILED");
    int abi=apply_landlock(sandbox);
    apply_seccomp();

    PyConfig cfg; PyConfig_InitIsolatedConfig(&cfg);
    cfg.site_import=0; cfg.use_environment=0; cfg.user_site_directory=0; cfg.safe_path=1; cfg.write_bytecode=0; cfg.parse_argv=0;
    PyStatus ps=PyConfig_SetBytesString(&cfg,&cfg.home,R16_PYTHON_HOME); if(PyStatus_Exception(ps))child_die(CHILD_FD,"R16_CHILD_PY_HOME_FAILED");
    ps=PyConfig_SetBytesString(&cfg,&cfg.program_name,R16_PYTHON_PROGRAM); if(PyStatus_Exception(ps))child_die(CHILD_FD,"R16_CHILD_PY_PROGRAM_FAILED");
    ps=Py_InitializeFromConfig(&cfg); PyConfig_Clear(&cfg); if(PyStatus_Exception(ps))child_die(CHILD_FD,"R16_CHILD_PY_INIT_FAILED");
    if(PySys_AddAuditHook(audit_hook,NULL)<0)child_die(CHILD_FD,"R16_CHILD_AUDIT_HOOK_FAILED");

    PyObject *json=PyImport_ImportModule("json"); if(!json)child_die(CHILD_FD,"R16_CHILD_JSON_IMPORT_FAILED");
    PyObject *loads=PyObject_GetAttrString(json,"loads"); Py_DECREF(json); if(!loads)child_die(CHILD_FD,"R16_CHILD_JSON_LOADS_MISSING");
    PyObject *txt=PyUnicode_DecodeUTF8((const char*)req,(Py_ssize_t)req_n,"strict"); if(!txt)child_die(CHILD_FD,"R16_CHILD_REQUEST_UTF8_INVALID");
    PyObject *request=PyObject_CallOneArg(loads,txt); Py_DECREF(loads); Py_DECREF(txt); if(!request||!PyDict_CheckExact(request))child_die(CHILD_FD,"R16_CHILD_REQUEST_JSON_INVALID");
    PyObject *m=PyDict_GetItemString(request,"module"),*f=PyDict_GetItemString(request,"function"),*a=PyDict_GetItemString(request,"args"),*k=PyDict_GetItemString(request,"kwargs");
    if(!m||!f||!a||!k||!PyUnicode_CheckExact(m)||!PyUnicode_CheckExact(f)||!PyList_CheckExact(a)||!PyDict_CheckExact(k))child_die(CHILD_FD,"R16_CHILD_REQUEST_SHAPE_INVALID");
    const char *mod=PyUnicode_AsUTF8(m),*fun=PyUnicode_AsUTF8(f); if(!mod||!fun)child_die(CHILD_FD,"R16_CHILD_REQUEST_NAME_INVALID");

    char subject[4096]; int sn=snprintf(subject,sizeof(subject),"%s/governance-runtime",sandbox); if(sn<=0||(size_t)sn>=sizeof(subject))child_die(CHILD_FD,"R16_CHILD_SANDBOX_PATH_TOO_LONG");
    PyObject *path=PySys_GetObject("path"),*sp=PyUnicode_FromString(subject); if(!path||!sp||PyList_Insert(path,0,sp)<0)child_die(CHILD_FD,"R16_CHILD_PATH_INSERT_FAILED"); Py_DECREF(sp);

    PyObject *module=PyImport_ImportModule(mod); if(!module)child_die(CHILD_FD,"R16_CHILD_CANDIDATE_IMPORT_FAILED");
    PyObject *call=PyObject_GetAttrString(module,fun); Py_DECREF(module); if(!call||!PyCallable_Check(call))child_die(CHILD_FD,"R16_CHILD_TARGET_NOT_CALLABLE");
    PyObject *args=PyList_AsTuple(a); if(!args)child_die(CHILD_FD,"R16_CHILD_ARGS_INVALID");
    PyObject *result=PyObject_Call(call,args,k); Py_DECREF(args); Py_DECREF(call);

    Buf payload; binit(&payload);
    bput(&payload,"{\"schema_version\":1,\"request_digest\":"); json_string(&payload,req_hex,64);
    bput(&payload,",\"module\":"); json_string(&payload,mod,strlen(mod));
    bput(&payload,",\"function\":"); json_string(&payload,fun,strlen(fun));
    if(result) {
        bput(&payload,",\"outcome_kind\":\"RETURN\",\"payload\":");
        if(serialize_obj(&payload,result,0))child_die(CHILD_FD,"R16_CHILD_RESULT_NOT_PLAIN_DATA");
        Py_DECREF(result);
    } else {
        PyObject *type=NULL,*value=NULL,*tb=NULL; PyErr_Fetch(&type,&value,&tb); PyErr_NormalizeException(&type,&value,&tb);
        const char *tn="Exception"; PyObject *name=NULL;
        if(type){name=PyObject_GetAttrString(type,"__name__");if(name&&PyUnicode_Check(name)){const char*x=PyUnicode_AsUTF8(name);if(x)tn=x;}}
        PyObject *vs=value?PyObject_Str(value):NULL; const char *msg=vs&&PyUnicode_Check(vs)?PyUnicode_AsUTF8(vs):"";
        bput(&payload,",\"outcome_kind\":\"EXCEPTION\",\"payload\":{\"exception_type\":"); json_string(&payload,tn,strlen(tn));
        bput(&payload,",\"message\":"); json_string(&payload,msg?msg:"",msg?strlen(msg):0); bch(&payload,'}');
        Py_XDECREF(name); Py_XDECREF(vs); Py_XDECREF(type); Py_XDECREF(value); Py_XDECREF(tb);
    }
    char abi_buf[64]; snprintf(abi_buf,sizeof(abi_buf),",\"landlock_abi\":%d",abi);
    bput(&payload,abi_buf);
    bput(&payload,",\"candidate_process_role\":\"UNTRUSTED_OBSERVATION_ONLY\",\"candidate_frame_authenticated\":false,\"authority_secret_present\":false,\"kernel_confinement\":\"LANDLOCK_PLUS_SECCOMP\",\"authority_effect\":\"NONE_EVIDENCE_ONLY\"}");

    char head[64]; int hn=snprintf(head,sizeof(head),"R16U1\n%zu\n",payload.n); if(hn<=0||(size_t)hn>=sizeof(head))child_die(CHILD_FD,"R16_CHILD_FRAME_HEADER_FAILED");
    if(write_all(CHILD_FD,head,(size_t)hn)||write_all(CHILD_FD,payload.p,payload.n))child_die(CHILD_FD,"R16_CHILD_FRAME_WRITE_FAILED");
    free(payload.p); Py_DECREF(request); _exit(0);
}

static unsigned char *read_pipe_all(int fd,size_t *n) {
    size_t cap=4096,used=0; unsigned char*p=(unsigned char*)malloc(cap); if(!p)die("R16_OOM");
    for(;;) {
        if(used==cap){if(cap>=MAX_FRAME)die("R16_FRAME_TOO_LARGE");cap*=2;unsigned char*q=(unsigned char*)realloc(p,cap);if(!q)die("R16_OOM");p=q;}
        ssize_t r=read(fd,p+used,cap-used); if(r<0){if(errno==EINTR)continue;die("R16_PIPE_READ_FAILED");} if(r==0)break;
        used+=(size_t)r; if(used>MAX_FRAME)die("R16_FRAME_TOO_LARGE");
    }
    *n=used; return p;
}

static int parse_child_frame(unsigned char *frame,size_t frame_n,unsigned char **payload,size_t *payload_n) {
    const char *magic="R16U1\n"; size_t ml=strlen(magic);
    if(frame_n<ml||memcmp(frame,magic,ml)!=0)return -1;
    unsigned char *nl=memchr(frame+ml,'\n',frame_n-ml); if(!nl)return -1;
    size_t digits=(size_t)(nl-(frame+ml)); if(digits==0||digits>20)return -1;
    char num[32]; memcpy(num,frame+ml,digits); num[digits]=0; char *end=NULL; unsigned long long declared=strtoull(num,&end,10); if(!end||*end)return -1;
    unsigned char *p=nl+1; size_t available=frame_n-(size_t)(p-frame); if(declared!=available||declared>MAX_FRAME)return -1;
    if(available<2||p[0]!='{'||p[available-1]!='}')return -1;
    *payload=p; *payload_n=available; return 0;
}

int main(int argc,char **argv) {
    const char *sandbox=NULL,*request_path=NULL;
    for(int i=1;i<argc;i++) {
        if(strcmp(argv[i],"--sandbox")==0&&i+1<argc)sandbox=argv[++i];
        else if(strcmp(argv[i],"--request")==0&&i+1<argc)request_path=argv[++i];
        else die("R16_NATIVE_ARGS_INVALID");
    }
    if(!sandbox||!request_path)die("R16_NATIVE_REQUIRED_ARGS_MISSING");

    size_t req_n=0; unsigned char *req=read_file(request_path,&req_n); unsigned char req_hash[32]; char req_hex[65]; sha256(req,req_n,req_hash); hex32(req_hash,req_hex);
    int pfd[2]; if(pipe2(pfd,O_CLOEXEC)!=0)die("R16_NATIVE_PIPE_FAILED");
    pid_t pid=fork(); if(pid<0)die("R16_NATIVE_FORK_FAILED");
    if(pid==0) { close(pfd[0]); child_main(pfd[1],req,req_n,req_hex,sandbox); }

    close(pfd[1]);
    unsigned char nonce[32]; if(getrandom(nonce,sizeof(nonce),0)!=(ssize_t)sizeof(nonce))die("R16_PARENT_NONCE_FAILED");
    size_t frame_n=0; unsigned char *frame=read_pipe_all(pfd[0],&frame_n); close(pfd[0]);
    int status=0; if(waitpid(pid,&status,0)<0)die("R16_NATIVE_WAIT_FAILED");
    if(!WIFEXITED(status)||WEXITSTATUS(status)!=0)die("R16_NATIVE_CHILD_NOT_CLEAN_EXIT");

    unsigned char *payload=NULL; size_t payload_n=0; if(parse_child_frame(frame,frame_n,&payload,&payload_n)!=0)die("R16_NATIVE_CHILD_FRAME_INVALID");
    unsigned char obs_hash[32]; char obs_hex[65]; sha256(payload,payload_n,obs_hash); hex32(obs_hash,obs_hex);
    unsigned char env_hash[32]; char env_hex[65]; sha256_2(nonce,sizeof(nonce),obs_hash,sizeof(obs_hash),env_hash); hex32(env_hash,env_hex);
    char nonce_hex[65]; hex32(nonce,nonce_hex);

    Buf out; binit(&out);
    bput(&out,"{\"schema_version\":1,\"candidate_observation\":"); bputn(&out,(const char*)payload,payload_n);
    bput(&out,",\"candidate_observation_sha256\":"); json_string(&out,obs_hex,64);
    bput(&out,",\"parent_nonce\":"); json_string(&out,nonce_hex,64);
    bput(&out,",\"parent_envelope_digest\":"); json_string(&out,env_hex,64);
    bput(&out,",\"candidate_process_role\":\"UNTRUSTED_OBSERVATION_ONLY\",\"candidate_frame_authenticated\":false,\"authority_secret_in_candidate_address_space\":false,\"parent_authentication_material_origin\":\"PARENT_ONLY_POST_FORK\",\"native_parent_initializes_python\":false,\"authority_effect\":\"NONE_EVIDENCE_ONLY\"}");
    fwrite(PREFIX,1,strlen(PREFIX),stdout); fwrite(out.p,1,out.n,stdout); fputc('\n',stdout); fflush(stdout);

    free(out.p); free(frame); free(req); return 0;
}
