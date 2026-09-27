/*
 * SutraLang v3 Core - Zero-GC Arena Memory Allocator Implementation
 */

#include "sutra_mem.h"

int sutra_arena_init(SutraArena *arena, size_t capacity) {
    arena->buffer = (char *)sutra_sys_mmap(capacity);
    if (arena->buffer == MAP_FAILED) return -1;
    arena->capacity = capacity;
    arena->offset = 0;
    return 0;
}

void *sutra_arena_alloc(SutraArena *arena, size_t size) {
    // 8-byte alignment
    size_t aligned_size = (size + 7) & ~7;
    if (arena->offset + aligned_size > arena->capacity) {
        return NULL; // Out of arena memory
    }
    void *ptr = &arena->buffer[arena->offset];
    arena->offset += aligned_size;
    return ptr;
}

void sutra_arena_reset(SutraArena *arena) {
    arena->offset = 0;
}

void sutra_arena_free(SutraArena *arena) {
    if (arena->buffer && arena->buffer != MAP_FAILED) {
        sutra_sys_munmap(arena->buffer, arena->capacity);
        arena->buffer = NULL;
        arena->capacity = 0;
        arena->offset = 0;
    }
}
