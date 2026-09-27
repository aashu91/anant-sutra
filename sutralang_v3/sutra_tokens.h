/*
 * SutraLang v3 Core - Isolated Architecture
 * Token Definitions & Paninian Grammar Constants
 */

#ifndef SUTRA_TOKENS_H
#define SUTRA_TOKENS_H

typedef enum {
    TOKEN_EOF = 0,
    TOKEN_EK,        // 'ek'
    TOKEN_KARTA,     // 'Karta' (Subject / Owner)
    TOKEN_KARMA,     // 'Karma' (Target / Object)
    TOKEN_KARANA,    // 'Karana' (Instrument / Function)
    TOKEN_MAAN,      // 'maan' (Value / State)
    TOKEN_SMRITI,    // 'smriti' (Memory Vault Query)
    TOKEN_SRUJ,      // 'Sruj' (Allocate / Create)
    TOKEN_PRAVAH,    // 'Pravah' (Stream / Event Loop)
    TOKEN_IDENT,     // Identifier (variable or function name)
    TOKEN_NUMBER,    // Numeric literal
    TOKEN_STRING,    // String literal
    TOKEN_UNKNOWN
} SutraTokenType;

typedef struct {
    SutraTokenType type;
    const char *start;
    int length;
    int line;
} SutraToken;

#endif // SUTRA_TOKENS_H
