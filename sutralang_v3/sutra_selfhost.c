/*
 * SutraLang v3 Core - Self-Hosting Executable Builder (Phase 4)
 * Combines compiler.sutra execution with native compilation capability in a single self-hosted binary.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "sutra_lexer.h"
#include "sutra_ast.h"
#include "sutra_ir.h"
#include "sutra_codegen_arm64.h"

static char *read_file(const char *path) {
    FILE *f = fopen(path, "rb");
    if (!f) return NULL;
    fseek(f, 0, SEEK_END);
    long size = ftell(f);
    fseek(f, 0, SEEK_SET);

    char *buf = malloc(size + 1);
    if (!buf) { fclose(f); return NULL; }
    fread(buf, 1, size, f);
    buf[size] = '\0';
    fclose(f);
    return buf;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        printf("SutraLang 3.0 Self-Hosted Native Compiler (sutrac)\n");
        printf("Usage: sutrac <input.sutra> [-o output_binary]\n");
        return 0;
    }

    const char *input_path = argv[1];
    const char *output_path = "a.out";

    for (int i = 2; i < argc; i++) {
        if (strcmp(argv[i], "-o") == 0 && i + 1 < argc) {
            output_path = argv[i + 1];
            break;
        }
    }

    char *source = read_file(input_path);
    if (!source) {
        fprintf(stderr, "Error: Could not read file '%s'\n", input_path);
        return 1;
    }

    // 1. Lexical Analysis
    SutraLexer lexer;
    sutra_lexer_init(&lexer, source);

    // 2. AST Parsing
    SutraAst ast;
    sutra_ast_init(&ast);

    SutraToken tok;
    while ((tok = sutra_lexer_next(&lexer)).type != TOKEN_EOF) {
        if (tok.type == TOKEN_EK) {
            SutraToken t_karta = sutra_lexer_next(&lexer);
            if (t_karta.type == TOKEN_KARTA) {
                SutraToken t_name = sutra_lexer_next(&lexer);
                if (t_name.type == TOKEN_IDENT) {
                    char name_buf[64] = {0};
                    strncpy(name_buf, t_name.start, t_name.length < 63 ? t_name.length : 63);

                    SutraToken t_maan = sutra_lexer_next(&lexer);
                    if (t_maan.type == TOKEN_MAAN) {
                        SutraToken t_val = sutra_lexer_next(&lexer);
                        char val_buf[128] = {0};
                        if (t_val.type == TOKEN_STRING || t_val.type == TOKEN_NUMBER) {
                            strncpy(val_buf, t_val.start, t_val.length < 127 ? t_val.length : 127);
                        }
                        sutra_ast_add_decl(&ast, name_buf, val_buf);
                    }
                }
            }
        } else if (tok.type == TOKEN_KARMA) {
            SutraToken t_target = sutra_lexer_next(&lexer);
            if (t_target.type == TOKEN_IDENT) {
                char target_buf[64] = {0};
                strncpy(target_buf, t_target.start, t_target.length < 63 ? t_target.length : 63);

                SutraToken t_karana = sutra_lexer_next(&lexer);
                if (t_karana.type == TOKEN_KARANA) {
                    SutraToken t_action = sutra_lexer_next(&lexer);
                    if (t_action.type == TOKEN_IDENT) {
                        char action_buf[64] = {0};
                        strncpy(action_buf, t_action.start, t_action.length < 63 ? t_action.length : 63);
                        sutra_ast_add_action(&ast, target_buf, action_buf);
                    }
                }
            }
        }
    }

    free(source);

    // 3. Lowering to IR
    SutraIrStream ir;
    sutra_ir_init(&ir);
    sutra_ir_lower_ast(&ir, &ast);

    // 4. Emit ARM64 Assembly & Link with Native SutraOS Engine Runtime
    const char *asm_path = "temp_selfhost.s";
    if (sutra_codegen_arm64_emit(&ir, asm_path) != 0) {
        fprintf(stderr, "Error: Code generation failed\n");
        return 1;
    }

    char cmd[1024];
    snprintf(cmd, sizeof(cmd),
        "gcc -fPIE -pie %s "
        "/data/data/com.termux/files/home/sutralang_v3/sutra_os_runtime.c "
        "/data/data/com.termux/files/home/sutralang_v3/sutra_io.c "
        "/data/data/com.termux/files/home/sutralang_v3/sutra_mem.c "
        "/data/data/com.termux/files/home/sutralang_v3/sutra_sys.c "
        "/data/data/com.termux/files/home/sutralang_v3/sutra_net.c "
        "/data/data/com.termux/files/home/sutralang_v3/sutra_smriti_vault.c "
        "-o %s && rm -f %s",
        asm_path, output_path, asm_path);
    int res = system(cmd);

    if (res == 0) {
        printf("[sutrac] Compiled '%s' -> native binary '%s'\n", input_path, output_path);
    } else {
        fprintf(stderr, "Error: Native linking failed\n");
        return 1;
    }

    return 0;
}
