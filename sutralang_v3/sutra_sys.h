/*
 * SutraLang v3 Core - Direct Linux Syscall Abstraction (SutraSys)
 * ponytail: Uses C syscall() bridge for cross-architecture portability; upgrade path is raw inline assembly asm("svc #0").
 */

#ifndef SUTRA_SYS_H
#define SUTRA_SYS_H

#include <stddef.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <sys/mman.h>

void *sutra_sys_mmap(size_t length);
int sutra_sys_munmap(void *addr, size_t length);
long sutra_sys_write(int fd, const void *buf, size_t count);
long sutra_sys_read(int fd, void *buf, size_t count);
void sutra_sys_exit(int status);

#endif // SUTRA_SYS_H
