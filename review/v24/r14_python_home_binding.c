#include <Python.h>
#include <stdio.h>
#include <stdlib.h>

#ifndef R14_PYTHON_HOME
#error "R14_PYTHON_HOME must be bound at compile time"
#endif

#ifndef R14_PYTHON_PROGRAM
#error "R14_PYTHON_PROGRAM must be bound at compile time"
#endif

/*
 * This function is linked into the R14 native observer while the observer
 * source is compiled with:
 *
 *   -DPyConfig_InitIsolatedConfig=R14_PyConfig_InitIsolatedConfig
 *
 * The shim itself is compiled without that macro, so this call reaches the
 * real CPython initializer.  Parent-side code still never initializes Python;
 * the call occurs only in the already-forked candidate child.
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
