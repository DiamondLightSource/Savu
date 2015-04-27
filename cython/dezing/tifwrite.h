#ifndef TIFWRITE_H
#define TIFWRITE_H
#include <tiffio.h>
#define MAX_MESSAGE (1024)
#define D_STRIPBYTES (2097152)
typedef struct mytiff_str{

  u_int32_t wd;
  u_int32_t ht;
  u_int32_t bytes;
  u_int32_t bits;
  u_int32_t nbytes;
  u_int32_t ndata;
  u_int32_t stripnum;
  u_int32_t stripsize;
  tsize_t bytesperstrip;
  u_int32_t * offsets;
  u_int32_t * bytecounts;
  u_int16_t mypage,npages;
  int tiffno;

  char * data;
  char * buf;
  u_int8_t isalloc;
  TIFF * tiffp;
} Mytiff;

#ifndef TIFWRITE_C
extern int tifread(Mytiff * mytiff, const char * const filename);
extern int tifwrite(Mytiff * mytiff, const char * const filename);
extern int tifwritestrips(Mytiff * mytiff, const char * const filename);
extern int tifinit(Mytiff * mytiff, const char * const filename);
extern int tiffree(Mytiff * mytiff);
extern int tifgettags(Mytiff * mytiff);
extern int tifclose(Mytiff * mytiff);
int tifgetstripsdata(Mytiff * mytiff,char * buf);
#endif

#endif /*TIFWRITE_H*/

