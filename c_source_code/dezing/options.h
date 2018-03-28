#ifndef OPTIONS_H
#define OPTIONS_H ("options.h svn id:$Id: options.h 376 2015-04-27 14:08:37Z kny48981 $")

typedef struct Options_str {
   char * indir,*outdir,*jobname,*fname,*dname;
   char * settingsfolder;
   char * infmt,*outfmt;
   u_int8_t fftw_level;
   u_int8_t f_call_num;
   u_int8_t returnflag;
   u_int8_t errflag;
   u_int8_t warnflag;
   u_int16_t nthreadsreq;
   double uval;
   size_t image_size;
   size_t uncrop_image_size;
   size_t image_size_bytes;
   size_t outimage_size_bytes;

   size_t croptop;
   size_t cropbot;
   size_t cropleft;
   size_t cropright;
   size_t cropwd;
   size_t croplen;
   size_t inoffset;

   u_int32_t image_len;
   u_int32_t nlines;
   u_int32_t wd;
   u_int32_t bytes;
   u_int32_t obytes;
   int32_t nsegs;
   int32_t nperseg;
   int32_t npad;
   u_int32_t nproj;
   u_int32_t timeout;
   u_int32_t interval;
   u_int32_t batchnum;
   u_int32_t nchunks;
   u_int32_t mychunk;
   u_int8_t Dtype;
   float energy;
   float distance;
   float pixelsize;
   float beta;
   float delta;
   float deltaratio;
   float outlier_mu;
   unsigned char versionflag; // flag to just print versions and exit
}Options;



typedef struct Flags_str{
   unsigned char D;
   unsigned char Iflag;
   unsigned char J;
   unsigned char O;
   unsigned char T;
   unsigned char Z;
   unsigned char S;
   unsigned char a;
   unsigned char b;
   unsigned char d;
   unsigned char f;
   unsigned char h;
   unsigned char i;
   unsigned char l;
   unsigned char m;
   unsigned char o;
   unsigned char p;
   unsigned char s;
   unsigned char u;
   unsigned char v;
   unsigned char w;
   unsigned char z;
   unsigned char crop;
}Flags ;
#endif 
