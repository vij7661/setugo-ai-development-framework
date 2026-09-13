#include <Python.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifndef R14_PYTHON_HOME
#error "R14_PYTHON_HOME must be bound at compile time"
#endif

#ifndef R14_PYTHON_PROGRAM
#error "R14_PYTHON_PROGRAM must be bound at compile time"
#endif

/*
 * The observer core is compiled with both mappings:
 *
 *   -DPyConfig_InitIsolatedConfig=R14_PyConfig_InitIsolatedConfig
 *   -DPy_InitializeFromConfig=R14_Py_InitializeFromConfig
 *
 * This shim is compiled without either macro.  The first wrapper binds the
 * embedded runtime to the exact trusted CPython installation.  The second
 * wrapper calls the real CPython initializer and then verifies the *actual*
 * child sys.flags/home/program state before control returns to the observer
 * core and before candidate paths are inserted or candidate Python is imported.
 * Parent-side code still never initializes Python.
 */
void R14_PyConfig_InitIsolatedConfig(PyConfig *config) {
    PyConfig_InitIsolatedConfig(config);

    PyStatus status = PyConfig_SetBytesString(
        config,
        &config->home,
        R14_PYTHON_HOME
    );
    if (PyStatus_Exception(status)) {
        fprintf(stderr, "R14_CHILD_PYTHON_HOME_BINDING_FAILED:%s\n",
                status.err_msg ? status.err_msg : "unknown");
        _Exit(112);
    }

    status = PyConfig_SetBytesString(
        config,
        &config->program_name,
        R14_PYTHON_PROGRAM
    );
    if (PyStatus_Exception(status)) {
        fprintf(stderr, "R14_CHILD_PYTHON_PROGRAM_BINDING_FAILED:%s\n",
                status.err_msg ? status.err_msg : "unknown");
        _Exit(113);
    }
}

static long flag_value(PyObject *flags, const char *name) {
    PyObject *value = PyObject_GetAttrString(flags, name);
    if (value == NULL) {
        fprintf(stderr, "R14_CHILD_RUNTIME_FLAG_MISSING:%s\n", name);
        _Exit(114);
    }
    long out = PyLong_AsLong(value);
    Py_DECREF(value);
    if (out == -1 && PyErr_Occurred()) {
        fprintf(stderr, "R14_CHILD_RUNTIME_FLAG_INVALID:%s\n", name);
        _Exit(115);
    }
    return out;
}

static const char *sys_utf8(const char *name) {
    PyObject *value = PySys_GetObject(name);
    if (value == NULL || !PyUnicode_Check(value)) {
        fprintf(stderr, "R14_CHILD_RUNTIME_SYS_FIELD_INVALID:%s\n", name);
        _Exit(116);
    }
    const char *out = PyUnicode_AsUTF8(value);
    if (out == NULL) {
        fprintf(stderr, "R14_CHILD_RUNTIME_SYS_FIELD_UTF8_INVALID:%s\n", name);
        _Exit(117);
    }
    return out;
}

PyStatus R14_Py_InitializeFromConfig(const PyConfig *config) {
    PyStatus status = Py_InitializeFromConfig(config);
    if (PyStatus_Exception(status)) {
        return status;
    }

    PyObject *flags = PySys_GetObject("flags");
    if (flags == NULL) {
        fprintf(stderr, "R14_CHILD_RUNTIME_FLAGS_MISSING\n");
        _Exit(118);
    }

    if (flag_value(flags, "isolated") != 1) {
        fprintf(stderr, "R14_CHILD_RUNTIME_ISOLATED_NOT_TRUE\n");
        _Exit(119);
    }
    if (flag_value(flags, "no_site") != 1) {
        fprintf(stderr, "R14_CHILD_RUNTIME_NO_SITE_NOT_TRUE\n");
        _Exit(120);
    }
    if (flag_value(flags, "ignore_environment") != 1) {
        fprintf(stderr, "R14_CHILD_RUNTIME_IGNORE_ENVIRONMENT_NOT_TRUE\n");
        _Exit(121);
    }
    if (flag_value(flags, "safe_path") != 1) {
        fprintf(stderr, "R14_CHILD_RUNTIME_SAFE_PATH_NOT_TRUE\n");
        _Exit(122);
    }
    if (flag_value(flags, "optimize") != 0) {
        fprintf(stderr, "R14_CHILD_RUNTIME_OPTIMIZATION_FORBIDDEN\n");
        _Exit(123);
    }
    if (flag_value(flags, "dont_write_bytecode") != 1) {
        fprintf(stderr, "R14_CHILD_RUNTIME_BYTECODE_WRITES_NOT_DISABLED\n");
        _Exit(124);
    }

    const char *prefix = sys_utf8("prefix");
    const char *base_prefix = sys_utf8("base_prefix");
    const char *executable = sys_utf8("executable");
    if (strcmp(prefix, R14_PYTHON_HOME) != 0 || strcmp(base_prefix, R14_PYTHON_HOME) != 0) {
        fprintf(stderr, "R14_CHILD_RUNTIME_HOME_MISMATCH:%s:%s\n", prefix, base_prefix);
        _Exit(125);
    }
    if (strcmp(executable, R14_PYTHON_PROGRAM) != 0) {
        fprintf(stderr, "R14_CHILD_RUNTIME_PROGRAM_MISMATCH:%s\n", executable);
        _Exit(126);
    }

    return status;
}
