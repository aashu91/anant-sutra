/*
 * SutraLang v3 Core - IR Lowering Implementation
 */

#include <string.h>
#include "sutra_ir.h"

void sutra_ir_init(SutraIrStream *stream) {
    stream->count = 0;
}

int sutra_ir_lower_ast(SutraIrStream *stream, const SutraAst *ast) {
    stream->count = 0;
    for (int i = 0; i < ast->count; i++) {
        const SutraAstNode *node = &ast->nodes[i];
        if (stream->count >= MAX_IR_INSTRUCTIONS) break;

        switch (node->type) {
            case AST_DECLARATION: {
                // Lower to IR_ALLOC + IR_STORE
                SutraIrInstruction *inst1 = &stream->instructions[stream->count++];
                inst1->opcode = IR_ALLOC;
                strncpy(inst1->arg1, node->name, 63);
                inst1->arg2[0] = '\0';

                SutraIrInstruction *inst2 = &stream->instructions[stream->count++];
                inst2->opcode = IR_STORE;
                strncpy(inst2->arg1, node->name, 63);
                strncpy(inst2->arg2, node->value, 127);
                break;
            }
            case AST_ACTION: {
                SutraIrInstruction *inst = &stream->instructions[stream->count++];
                inst->opcode = IR_CALL;
                strncpy(inst->arg1, node->name, 63);
                strncpy(inst->arg2, node->action, 127);
                break;
            }
            case AST_VAULT_QUERY: {
                SutraIrInstruction *inst = &stream->instructions[stream->count++];
                inst->opcode = IR_SMRITI;
                strncpy(inst->arg1, node->name, 63);
                strncpy(inst->arg2, node->value, 127);
                break;
            }
        }
    }

    // Add IR_RET
    if (stream->count < MAX_IR_INSTRUCTIONS) {
        SutraIrInstruction *ret = &stream->instructions[stream->count++];
        ret->opcode = IR_RET;
        ret->arg1[0] = '\0';
        ret->arg2[0] = '\0';
    }

    return stream->count;
}
