/*
 * SutraLang v3 Core - Non-blocking Async Event Loop Header (SutraNet)
 * ponytail: Non-blocking epoll event loop wrapper for Linux/Termux; upgrade path is io_uring ring buffer submission.
 */

#ifndef SUTRA_NET_H
#define SUTRA_NET_H

#include <sys/epoll.h>

#define MAX_EPOLL_EVENTS 64

typedef struct {
    int epoll_fd;
    struct epoll_event events[MAX_EPOLL_EVENTS];
    int is_running;
} SutraEventLoop;

int sutra_event_loop_init(SutraEventLoop *loop);
int sutra_event_loop_add_fd(SutraEventLoop *loop, int fd, uint32_t events);
int sutra_event_loop_poll(SutraEventLoop *loop, int timeout_ms);
void sutra_event_loop_close(SutraEventLoop *loop);

#endif // SUTRA_NET_H
