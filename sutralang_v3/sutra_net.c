/*
 * SutraLang v3 Core - Non-blocking Async Event Loop Implementation
 */

#include <unistd.h>
#include "sutra_net.h"

int sutra_event_loop_init(SutraEventLoop *loop) {
    loop->epoll_fd = epoll_create1(0);
    if (loop->epoll_fd < 0) return -1;
    loop->is_running = 1;
    return 0;
}

int sutra_event_loop_add_fd(SutraEventLoop *loop, int fd, uint32_t events) {
    struct epoll_event ev;
    ev.events = events;
    ev.data.fd = fd;
    return epoll_ctl(loop->epoll_fd, EPOLL_CTL_ADD, fd, &ev);
}

int sutra_event_loop_poll(SutraEventLoop *loop, int timeout_ms) {
    int nfds = epoll_wait(loop->epoll_fd, loop->events, MAX_EPOLL_EVENTS, timeout_ms);
    return nfds;
}

void sutra_event_loop_close(SutraEventLoop *loop) {
    if (loop->epoll_fd >= 0) {
        close(loop->epoll_fd);
        loop->epoll_fd = -1;
    }
    loop->is_running = 0;
}
