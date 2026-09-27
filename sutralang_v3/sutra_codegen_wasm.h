/*
 * SutraLang v3 Core - WebAssembly Code Generator Header (SutraWasm)
 * ponytail: Emits standard WebAssembly binary magic header (0x00 61 73 6d 01 00 00 00) for in-browser execution.
 */

#ifndef SUTRA_CODEGEN_WASM_H
#define SUTRA_CODEGEN_WASM_H

#include "sutra_ir.h"

int sutra_codegen_wasm_emit(const SutraIrStream *ir_stream, const char *output_wasm_path);

#endif // SUTRA_CODEGEN_WASM_H
