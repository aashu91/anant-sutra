/*
 * SutraLang v3 Core - Paninian Karaka AST Implementation
 */

#include <string.h>
#include "sutra_ast.h"

void sutra_ast_init(SutraAst *ast) {
    ast->count = 0;
}

int sutra_ast_add_decl(SutraAst *ast, const char *name, const char *value) {
    if (ast->count >= MAX_AST_NODES) return -1;
    SutraAstNode *node = &ast->nodes[ast->count++];
    node->type = AST_DECLARATION;
    strncpy(node->name, name, 63); node->name[63] = '\0';
    strncpy(node->value, value, 127); node->value[127] = '\0';
    node->action[0] = '\0';
    return ast->count - 1;
}

int sutra_ast_add_action(SutraAst *ast, const char *target, const char *action) {
    if (ast->count >= MAX_AST_NODES) return -1;
    SutraAstNode *node = &ast->nodes[ast->count++];
    node->type = AST_ACTION;
    strncpy(node->name, target, 63); node->name[63] = '\0';
    node->value[0] = '\0';
    strncpy(node->action, action, 63); node->action[63] = '\0';
    return ast->count - 1;
}

int sutra_ast_add_smriti(SutraAst *ast, const char *target, const char *query) {
    if (ast->count >= MAX_AST_NODES) return -1;
    SutraAstNode *node = &ast->nodes[ast->count++];
    node->type = AST_VAULT_QUERY;
    strncpy(node->name, target, 63); node->name[63] = '\0';
    strncpy(node->value, query, 127); node->value[127] = '\0';
    node->action[0] = '\0';
    return ast->count - 1;
}
