/*
 * SutraLang v3 Core - Native I/O & String Utilities Header (SutraIO)
 */

#ifndef SUTRA_IO_H
#define SUTRA_IO_H

#include <stddef.h>
#include "sutra_sys.h"

size_t sutra_strlen(const char *str);
void sutra_print(const char *str);
void sutra_println(const char *str);
int sutra_itoa(int val, char *buf);

#endif // SUTRA_IO_H
