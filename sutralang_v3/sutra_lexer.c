/*
 * SutraLang v3 Core - Single-Pass Lexer Implementation
 * ponytail: ASCII keyword scanner for zero-copy speed; upgrade path is full UTF-8 Devanagari lookup tables.
 */

#include <string.h>
#include <ctype.h>
#include "sutra_lexer.h"

void sutra_lexer_init(SutraLexer *lexer, const char *source) {
    lexer->source = source;
    lexer->cursor = source;
    lexer->line = 1;
}

static int is_alpha(char c) {
    return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || c == '_';
}

static int is_digit(char c) {
    return (c >= '0' && c <= '9');
}

static SutraTokenType check_keyword(const char *start, int length) {
    if (length == 2 && strncmp(start, "ek", 2) == 0) return TOKEN_EK;
    if (length == 5 && strncmp(start, "Karta", 5) == 0) return TOKEN_KARTA;
    if (length == 5 && strncmp(start, "Karma", 5) == 0) return TOKEN_KARMA;
    if (length == 6 && strncmp(start, "Karana", 6) == 0) return TOKEN_KARANA;
    if (length == 4 && strncmp(start, "maan", 4) == 0) return TOKEN_MAAN;
    if (length == 6 && strncmp(start, "smriti", 6) == 0) return TOKEN_SMRITI;
    if (length == 4 && strncmp(start, "Sruj", 4) == 0) return TOKEN_SRUJ;
    if (length == 6 && strncmp(start, "Pravah", 6) == 0) return TOKEN_PRAVAH;
    return TOKEN_IDENT;
}

SutraToken sutra_lexer_next(SutraLexer *lexer) {
    while (*lexer->cursor != '\0') {
        char c = *lexer->cursor;

        // Skip whitespace
        if (c == ' ' || c == '\t' || c == '\r') {
            lexer->cursor++;
            continue;
        }
        if (c == '\n') {
            lexer->line++;
            lexer->cursor++;
            continue;
        }
        // Skip comments (//)
        if (c == '/' && *(lexer->cursor + 1) == '/') {
            while (*lexer->cursor != '\0' && *lexer->cursor != '\n') {
                lexer->cursor++;
            }
            continue;
        }

        const char *start = lexer->cursor;

        // Identifiers & Keywords
        if (is_alpha(c)) {
            while (is_alpha(*lexer->cursor) || is_digit(*lexer->cursor)) {
                lexer->cursor++;
            }
            int length = (int)(lexer->cursor - start);
            SutraTokenType type = check_keyword(start, length);
            return (SutraToken){ .type = type, .start = start, .length = length, .line = lexer->line };
        }

        // Number literals
        if (is_digit(c)) {
            while (is_digit(*lexer->cursor)) {
                lexer->cursor++;
            }
            int length = (int)(lexer->cursor - start);
            return (SutraToken){ .type = TOKEN_NUMBER, .start = start, .length = length, .line = lexer->line };
        }

        // String literals
        if (c == '"') {
            lexer->cursor++; // skip opening quote
            start = lexer->cursor;
            while (*lexer->cursor != '\0' && *lexer->cursor != '"') {
                if (*lexer->cursor == '\n') lexer->line++;
                lexer->cursor++;
            }
            int length = (int)(lexer->cursor - start);
            if (*lexer->cursor == '"') lexer->cursor++; // skip closing quote
            return (SutraToken){ .type = TOKEN_STRING, .start = start, .length = length, .line = lexer->line };
        }

        // Unknown single character
        lexer->cursor++;
        return (SutraToken){ .type = TOKEN_UNKNOWN, .start = start, .length = 1, .line = lexer->line };
    }

    return (SutraToken){ .type = TOKEN_EOF, .start = lexer->cursor, .length = 0, .line = lexer->line };
}
