/* Minimal <string.h> for the freestanding lab build (implementations are in libc_min.c). */
#ifndef LAB_STRING_H
#define LAB_STRING_H
#include <stddef.h>
void *memcpy(void *, const void *, size_t);
void *memmove(void *, const void *, size_t);
void *memset(void *, int, size_t);
int memcmp(const void *, const void *, size_t);
size_t strlen(const char *);
int strcmp(const char *, const char *);
char *strncpy(char *, const char *, size_t);
#endif
