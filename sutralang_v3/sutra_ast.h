/*
 * SutraLang v3 Core - Paninian Karaka AST Specifications
 * ponytail: Fixed-size arena array node storage; upgrade path is dynamic page-backed AST arena pool.
 */

#ifndef SUTRA_AST_H
#define SUTRA_AST_H

#include "sutra_tokens.h"

typedef enum {
    AST_DECLARATION, // ek Karta <name> maan <val>
    AST_ACTION,      // Karma <target> Karana <action>
    AST_VAULT_QUERY  // <res> ko <query> se smriti
} SutraAstNodeType;

typedef struct {
    SutraAstNodeType type;
    char name[64];
    char value[128];
    char action[64];
} SutraAstNode;

#define MAX_AST_NODES 256

typedef struct {
    SutraAstNode nodes[MAX_AST_NODES];
    int count;
} SutraAst;

void sutra_ast_init(SutraAst *ast);
int sutra_ast_add_decl(SutraAst *ast, const char *name, const char *value);
int sutra_ast_add_action(SutraAst *ast, const char *target, const char *action);
int sutra_ast_add_smriti(SutraAst *ast, const char *target, const char *query);

#endif // SUTRA_AST_H
