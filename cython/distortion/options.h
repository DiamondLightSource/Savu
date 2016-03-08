#ifndef OPTIONS_H
#define OPTIONS_H
#include "stdio.h"
#define SVN_ID_OPTIONS_H "$Id: options.h 444 2015-12-15 11:56:04Z kny48981 $"
#define SVN_URL_OPTIONS_H "$URL: file:///home/kny48981/SVN/progs/unwarp_cython/options.h $"
typedef struct Options_str {
  char *indir, *outdir, *jobname, *fname;
  char *infmt, *outfmt;
  unsigned int ht;
  unsigned int wd;
  unsigned int firstslice;
  unsigned int lastslice;
  float xcentre;
  float ycentre;
  u_int32_t nlines;
  u_int32_t bytes;
  u_int32_t nperseg;
  u_int32_t nproj;
  u_int32_t timeout;
  u_int32_t interval;
  u_int32_t avnum;
  u_int32_t nchunks;
  u_int32_t mychunk;
  u_int8_t Dtype;
  u_int8_t Usegpu;
  unsigned char f_call_num;
  unsigned char versionflag;
  unsigned char pixelflag;
  float dcoeff,acoeff,bcoeff,ccoeff,ecoeff;

} Options;

#endif /*OPTIONS_H*/
