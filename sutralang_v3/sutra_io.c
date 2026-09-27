/*
 * SutraLang v3 Core - Native I/O & String Implementation
 */

#include "sutra_io.h"

size_t sutra_strlen(const char *str) {
    const char *s = str;
    while (*s) s++;
    return (size_t)(s - str);
}

void sutra_print(const char *str) {
    sutra_sys_write(1, str, sutra_strlen(str));
}

void sutra_println(const char *str) {
    sutra_print(str);
    sutra_sys_write(1, "\n", 1);
}

int sutra_itoa(int val, char *buf) {
    if (val == 0) {
        buf[0] = '0';
        buf[1] = '\0';
        return 1;
    }
    int is_neg = 0;
    if (val < 0) {
        is_neg = 1;
        val = -val;
    }

    char temp[32];
    int i = 0;
    while (val > 0) {
        temp[i++] = '0' + (val % 10);
        val /= 10;
    }
    if (is_neg) temp[i++] = '-';

    int len = i;
    for (int j = 0; j < len; j++) {
        buf[j] = temp[len - 1 - j];
    }
    buf[len] = '\0';
    return len;
}
