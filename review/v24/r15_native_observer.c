#define _GNU_SOURCE
#include <Python.h>

/*
 * R15 deliberately reuses the frozen R14 native transport implementation but
 * intercepts audit-hook installation with a stronger, representation-complete
 * path policy.  The historical R14 source remains unchanged and separately
 * addressable on its rejected branch.
 */
static int R15_PySys_AddAuditHook_intercept(Py_AuditHookFunction hook, void *userData);

#define main r14_embedded_main
#define PySys_AddAuditHook R15_PySys_AddAuditHook_intercept
#include "r14_native_observer.c"
#undef PySys_AddAuditHook
#undef main

static int r15_bytes_prefix(const char *p, Py_ssize_t n, const char *prefix) {
    size_t pn = strlen(prefix);
    return p && n >= 0 && (size_t)n >= pn && memcmp(p, prefix, pn) == 0;
}

static int r15_bytes_equal(const char *p, Py_ssize_t n, const char *value) {
    size_t vn = strlen(value);
    return p && n >= 0 && (size_t)n == vn && memcmp(p, value, vn) == 0;
}

static int r15_forbidden_normalized_path(const char *p, Py_ssize_t n) {
    if (!p || n < 0) return 1;
    if (r15_bytes_equal(p,n,"/proc") || r15_bytes_prefix(p,n,"/proc/")) return 1;
    if (r15_bytes_equal(p,n,"/sys") || r15_bytes_prefix(p,n,"/sys/")) return 1;
    if (r15_bytes_equal(p,n,"/dev/mem") || r15_bytes_equal(p,n,"/dev/kmem")) return 1;

    /* Resolve alternate lexical spellings and symlinked aliases when the path
       exists. Failure to resolve does not grant access to an already-forbidden
       lexical path because those cases were rejected above. */
    if ((size_t)n < 4096) {
        char raw[4096];
        memcpy(raw,p,(size_t)n); raw[n] = 0;
        char resolved[4096];
        if (realpath(raw,resolved) != NULL) {
            size_t rn = strlen(resolved);
            if (r15_bytes_equal(resolved,(Py_ssize_t)rn,"/proc") || r15_bytes_prefix(resolved,(Py_ssize_t)rn,"/proc/")) return 1;
            if (r15_bytes_equal(resolved,(Py_ssize_t)rn,"/sys") || r15_bytes_prefix(resolved,(Py_ssize_t)rn,"/sys/")) return 1;
            if (r15_bytes_equal(resolved,(Py_ssize_t)rn,"/dev/mem") || r15_bytes_equal(resolved,(Py_ssize_t)rn,"/dev/kmem")) return 1;
        }
    }
    return 0;
}

static int r15_extract_path(PyObject *x, const char **p, Py_ssize_t *n) {
    *p = NULL; *n = -1;
    if (PyUnicode_Check(x)) {
        *p = PyUnicode_AsUTF8AndSize(x,n);
        return *p ? 0 : -1;
    }
    if (PyBytes_Check(x)) {
        char *bp = NULL;
        if (PyBytes_AsStringAndSize(x,&bp,n) < 0) return -1;
        *p = bp;
        return 0;
    }
    /* Integer-fd and any unrecognized path representation are fail-closed for
       candidate execution. The governed subject does not require opening raw
       inherited descriptors to satisfy the V6 checks. */
    return 1;
}

static int r15_audit_hook(const char *event, PyObject *args, void *ud) {
    if (strcmp(event,"open") == 0 && PyTuple_Check(args) && PyTuple_GET_SIZE(args) > 0) {
        PyObject *x = PyTuple_GET_ITEM(args,0);
        const char *p = NULL; Py_ssize_t n = -1;
        int kind = r15_extract_path(x,&p,&n);
        if (kind != 0) {
            if (kind > 0) PyErr_SetString(PyExc_PermissionError,"R15_AUDIT_PATH_REPRESENTATION_FORBIDDEN");
            return -1;
        }
        if (r15_forbidden_normalized_path(p,n)) {
            PyErr_SetString(PyExc_PermissionError,"R15_AUDIT_FORBIDDEN_NORMALIZED_PATH");
            return -1;
        }
    }
    /* Preserve every R14 event/import restriction in addition to R15 path
       normalization. */
    return audit_hook(event,args,ud);
}

static int R15_PySys_AddAuditHook_intercept(Py_AuditHookFunction hook, void *userData) {
    (void)hook;
    return PySys_AddAuditHook(r15_audit_hook,userData);
}

int main(int argc, char **argv) {
    return r14_embedded_main(argc,argv);
}
