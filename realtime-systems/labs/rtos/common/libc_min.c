/* libc_min.c -- the handful of libc routines the compiler and FreeRTOS may call (no libc is linked). */
#include <stddef.h>
void *memcpy(void *d, const void *s, size_t n) { unsigned char *dd = d; const unsigned char *ss = s; while (n--) *dd++ = *ss++; return d; }
void *memmove(void *d, const void *s, size_t n) { unsigned char *dd = d; const unsigned char *ss = s; if (dd < ss) { while (n--) *dd++ = *ss++; } else { dd += n; ss += n; while (n--) *--dd = *--ss; } return d; }
void *memset(void *d, int c, size_t n) { unsigned char *dd = d; while (n--) *dd++ = (unsigned char)c; return d; }
int memcmp(const void *a, const void *b, size_t n) { const unsigned char *x = a, *y = b; while (n--) { if (*x != *y) return *x - *y; x++; y++; } return 0; }
size_t strlen(const char *s) { size_t n = 0; while (s[n]) n++; return n; }
int strcmp(const char *a, const char *b) { while (*a && *a == *b) { a++; b++; } return (unsigned char)*a - (unsigned char)*b; }
char *strncpy(char *d, const char *s, size_t n) { size_t i = 0; for (; i < n && s[i]; i++) d[i] = s[i]; for (; i < n; i++) d[i] = 0; return d; }
