

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include "machine.h"
extern FILE * logfp;
extern struct timeval mystime;
extern double oldtime;
extern unsigned char vflag;
extern int logprint(const char *const message,const int level);
extern void timestamp_init(void);
extern void timestamp_open(const char * const logname);
extern void timestamp_close(void);
extern void timestamp(const char *const stampmsg,const int level);
extern int errprint(const char * const message,const int level);
extern int vprint(const char * const message);
extern void pydebug(char * message);
extern void pyinfo(char * message);
extern void pyuser(char * message);
extern void pywarn(char * message);
extern void pyerr(char * message);

#define LEVEL_DEBUG (0)
#define LEVEL_INFO (1)
#define LEVEL_USER (2)
#define LEVEL_WARN (3)
#define LEVEL_ERR (4)
