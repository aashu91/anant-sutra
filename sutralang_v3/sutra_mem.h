/*
 * SutraLang v3 Core - Zero-GC Arena Memory Allocator (SutraMem)
 * ponytail: Single-threaded linear page arena; upgrade path is thread-local multi-arena pools.
 */

#ifndef SUTRA_MEM_H
#define SUTRA_MEM_H

#include <stddef.h>
#include "sutra_sys.h"

typedef struct {
    char *buffer;
    size_t capacity;
    size_t offset;
} SutraArena;

int sutra_arena_init(SutraArena *arena, size_t capacity);
void *sutra_arena_alloc(SutraArena *arena, size_t size);
void sutra_arena_reset(SutraArena *arena);
void sutra_arena_free(SutraArena *arena);

#endif // SUTRA_MEM_H
