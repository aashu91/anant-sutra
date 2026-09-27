/*
 * SutraLang v3 Core - C-ABI Foreign Function Interface Header (SutraFFI)
 * ponytail: Dynamic library symbol lookup wrapper via dlopen/dlsym for zero-glue C interop.
 */

#ifndef SUTRA_FFI_H
#define SUTRA_FFI_H

#include <dlfcn.h>

typedef void* SutraLibHandle;

SutraLibHandle sutra_ffi_load_lib(const char *lib_path);
void *sutra_ffi_get_symbol(SutraLibHandle handle, const char *symbol_name);
void sutra_ffi_close_lib(SutraLibHandle handle);

#endif // SUTRA_FFI_H
