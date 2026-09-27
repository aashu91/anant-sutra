/*
 * SutraLang v3 Core - Intermediate Representation (IR) Spec
 * ponytail: Linear instruction array IR; upgrade path is SSA-form control flow graph.
 */

#ifndef SUTRA_IR_H
#define SUTRA_IR_H

#include "sutra_ast.h"

typedef enum {
    IR_ALLOC,   // Bind Karta scope
    IR_STORE,   // Store Maan state
    IR_CALL,    // Execute Karana operation
    IR_SMRITI,  // Query Smriti vault
    IR_RET      // End block
} SutraIrOpcode;

typedef struct {
    SutraIrOpcode opcode;
    char arg1[64];
    char arg2[128];
} SutraIrInstruction;

#define MAX_IR_INSTRUCTIONS 256

typedef struct {
    SutraIrInstruction instructions[MAX_IR_INSTRUCTIONS];
    int count;
} SutraIrStream;

void sutra_ir_init(SutraIrStream *stream);
int sutra_ir_lower_ast(SutraIrStream *stream, const SutraAst *ast);

#endif // SUTRA_IR_H
