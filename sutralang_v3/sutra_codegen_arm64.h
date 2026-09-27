/*
 * SutraLang v3 Core - ARM64 Assembly Code Generator Header
 * ponytail: Emits GNU ARM64 assembly with direct Linux syscalls (sys_write=64, sys_exit=93).
 */

#ifndef SUTRA_CODEGEN_ARM64_H
#define SUTRA_CODEGEN_ARM64_H

#include "sutra_ir.h"

int sutra_codegen_arm64_emit(const SutraIrStream *ir_stream, const char *output_assembly_path);

#endif // SUTRA_CODEGEN_ARM64_H
