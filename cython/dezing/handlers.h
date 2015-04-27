/* Prototypes for the signal handler functions */
/* Define GNU_TRAP_FPE if using GCC in order to catch floating point exceptions */
/* This impacts the performance so don't do it all the time */
#ifndef HANDLERS_H
#   define HANDLERS_H

#   ifdef GNU_TRAP_FPE
#      include <fenv.h>
void enable_fpe_traps ();
#   endif
       /* GNU_TRAP_FPE */

extern void float_error (int signo);    /* signal handler for sigfpe */
extern void catchit (int signo);        /* signal handler -- jump to finish_bb */
#endif
