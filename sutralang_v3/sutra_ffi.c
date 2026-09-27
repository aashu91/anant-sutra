/*
 * SutraLang v3 Core - C-ABI FFI Implementation
 */

#include "sutra_ffi.h"

SutraLibHandle sutra_ffi_load_lib(const char *lib_path) {
    return dlopen(lib_path, RTLD_LAZY | RTLD_GLOBAL);
}

void *sutra_ffi_get_symbol(SutraLibHandle handle, const char *symbol_name) {
    if (!handle) return NULL;
    return dlsym(handle, symbol_name);
}

void sutra_ffi_close_lib(SutraLibHandle handle) {
    if (handle) {
        dlclose(handle);
    }
}
