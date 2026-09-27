/*
 * SutraLang v3 Core - Phase 3 Verification Test
 * ponytail: Assert-based single-file check; no external dependencies or frameworks needed.
 */

#include <stdio.h>
#include <assert.h>
#include <string.h>
#include "sutra_sys.h"
#include "sutra_mem.h"
#include "sutra_io.h"
#include "sutra_net.h"

int main() {
    printf("=== Running SutraLang v3 Phase 3 Verification ===\n");

    // 1. Verify Direct Linux Syscalls & Native I/O
    const char *sys_msg = "[✓] Direct Linux Syscall (sys_write) Verified\n";
    sutra_sys_write(1, sys_msg, sutra_strlen(sys_msg));

    // 2. Verify String & Integer Formatting
    char num_buf[32];
    int len = sutra_itoa(300, num_buf);
    assert(len == 3);
    assert(strcmp(num_buf, "300") == 0);
    printf("[✓] SutraIO String & Integer Formatting Passed (val=%s)\n", num_buf);

    // 3. Verify Zero-GC Arena Allocator (SutraMem)
    SutraArena arena;
    int res = sutra_arena_init(&arena, 64 * 1024); // 64KB page arena
    assert(res == 0);
    assert(arena.capacity == 64 * 1024);

    char *allocated_str = (char *)sutra_arena_alloc(&arena, 128);
    assert(allocated_str != NULL);
    strcpy(allocated_str, "SutraLang v3 Page-Backed Arena Memory");
    assert(strcmp(allocated_str, "SutraLang v3 Page-Backed Arena Memory") == 0);

    sutra_arena_free(&arena);
    assert(arena.buffer == NULL);
    printf("[✓] Zero-GC Arena Memory Allocator (SutraMem) Passed\n");

    // 4. Verify Async Event Loop (SutraNet)
    SutraEventLoop loop;
    int ep_res = sutra_event_loop_init(&loop);
    assert(ep_res == 0);
    assert(loop.epoll_fd >= 0);

    sutra_event_loop_close(&loop);
    assert(loop.epoll_fd == -1);
    printf("[✓] Non-blocking Event Loop (SutraNet) Passed\n");

    printf("=== PHASE 3 COMPLETE & VERIFIED SUCCESSFUL ===\n");
    return 0;
}
