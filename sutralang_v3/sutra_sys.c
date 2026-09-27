/*
 * SutraLang v3 Core - Direct Linux Syscall Implementation
 */

#include "sutra_sys.h"

void *sutra_sys_mmap(size_t length) {
    return (void *)syscall(SYS_mmap, NULL, length, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
}

int sutra_sys_munmap(void *addr, size_t length) {
    return (int)syscall(SYS_munmap, addr, length);
}

long sutra_sys_write(int fd, const void *buf, size_t count) {
    return syscall(SYS_write, fd, buf, count);
}

long sutra_sys_read(int fd, void *buf, size_t count) {
    return syscall(SYS_read, fd, buf, count);
}

void sutra_sys_exit(int status) {
    syscall(SYS_exit, status);
}
