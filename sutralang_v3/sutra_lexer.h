/*
 * SutraLang v3 Core - Isolated Architecture
 * Single-Pass Zero-Copy Lexer
 */

#ifndef SUTRA_LEXER_H
#define SUTRA_LEXER_H

#include "sutra_tokens.h"

typedef struct {
    const char *source;
    const char *cursor;
    int line;
} SutraLexer;

void sutra_lexer_init(SutraLexer *lexer, const char *source);
SutraToken sutra_lexer_next(SutraLexer *lexer);

#endif // SUTRA_LEXER_H
