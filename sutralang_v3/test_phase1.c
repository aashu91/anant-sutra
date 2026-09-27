/*
 * SutraLang v3 Core - Phase 1 Verification Test
 * ponytail: Assert-based single-file check; no test framework or external fixtures needed.
 */

#include <stdio.h>
#include <assert.h>
#include <string.h>
#include "sutra_lexer.h"
#include "sutra_ast.h"
#include "sutra_ir.h"

int main() {
    printf("=== Running SutraLang v3 Phase 1 Verification ===\n");

    const char *test_code = "ek Karta msg maan \"Hello SutraLang v3\"\nKarma msg Karana Print\n";

    // 1. Verify Lexer
    SutraLexer lexer;
    sutra_lexer_init(&lexer, test_code);

    SutraToken tok1 = sutra_lexer_next(&lexer);
    assert(tok1.type == TOKEN_EK);

    SutraToken tok2 = sutra_lexer_next(&lexer);
    assert(tok2.type == TOKEN_KARTA);

    SutraToken tok3 = sutra_lexer_next(&lexer);
    assert(tok3.type == TOKEN_IDENT);
    assert(strncmp(tok3.start, "msg", 3) == 0);

    SutraToken tok4 = sutra_lexer_next(&lexer);
    assert(tok4.type == TOKEN_MAAN);

    SutraToken tok5 = sutra_lexer_next(&lexer);
    assert(tok5.type == TOKEN_STRING);
    assert(strncmp(tok5.start, "Hello SutraLang v3", 18) == 0);

    SutraToken tok6 = sutra_lexer_next(&lexer);
    assert(tok6.type == TOKEN_KARMA);

    printf("[✓] Lexer Verification Passed\n");

    // 2. Verify AST Construction
    SutraAst ast;
    sutra_ast_init(&ast);
    sutra_ast_add_decl(&ast, "msg", "Hello SutraLang v3");
    sutra_ast_add_action(&ast, "msg", "Print");

    assert(ast.count == 2);
    assert(ast.nodes[0].type == AST_DECLARATION);
    assert(strcmp(ast.nodes[0].name, "msg") == 0);
    assert(strcmp(ast.nodes[0].value, "Hello SutraLang v3") == 0);

    assert(ast.nodes[1].type == AST_ACTION);
    assert(strcmp(ast.nodes[1].action, "Print") == 0);

    printf("[✓] AST Specification Passed\n");

    // 3. Verify IR Lowering
    SutraIrStream ir_stream;
    sutra_ir_init(&ir_stream);
    int ir_count = sutra_ir_lower_ast(&ir_stream, &ast);

    assert(ir_count == 4); // IR_ALLOC, IR_STORE, IR_CALL, IR_RET
    assert(ir_stream.instructions[0].opcode == IR_ALLOC);
    assert(ir_stream.instructions[1].opcode == IR_STORE);
    assert(ir_stream.instructions[2].opcode == IR_CALL);
    assert(ir_stream.instructions[3].opcode == IR_RET);

    printf("[✓] IR Lowering & Opcode Stream Passed\n");
    printf("=== PHASE 1 COMPLETE & VERIFIED SUCCESSFUL ===\n");

    return 0;
}
