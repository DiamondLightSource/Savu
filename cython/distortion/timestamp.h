#ifndef TIMESTAMP_H
#define TIMESTAMP_H
#ifdef __cplusplus
extern "C" {
#endif

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include "machine.h"
extern FILE * logfp;
//extern struct timeval mystime;
extern double oldtime;
extern unsigned char vflag;
extern int logprint(const char *const message);
extern void timestamp_open(const char * const logname);
extern void timestamp_init(void);
extern void timestamp_close(void);
extern void timestamp(const char *const stampmsg);
extern int errprint(const char * const message);
extern int vprint(const char * const message);

#ifdef __cplusplus
}
#endif
#endif /*TIMESAMP_H*/ 
