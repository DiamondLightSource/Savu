#include <stdlib.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/time.h>
#include <sys/signal.h>
#include <setjmp.h>
#include <unistd.h>
#include <string.h>
#include <limits.h>
#include <math.h>
#include <errno.h>
#include <time.h>
#include <libgen.h>
#include "options.h"

#include "handlers.h"
#include "timestamp.h"
#include "dezing_functions.h"

#ifdef PCO_4000_FIX_BCD
#  ifndef PCO_CROPTOP
#    define PCO_CROPTOP (10)
#  endif
#endif

#ifndef NOPAUSE
#define NOPAUSE (10) /* microseconds */
#endif

#ifndef SHORTPAUSE
#define SHORTPAUSE (100000) /* microseconds */
#endif

#ifndef LONGPAUSE
#define LONGPAUSE (500000) /* microseconds */
#endif
#ifndef NOPAUSE
#define NOPAUSE (100) /* microseconds */
#endif

#ifndef DEFAULT_DARK
#define DEFAULT_DARK (400)
#endif

/* how many file numbers to look-ahead when running live */
#ifndef LOOKAHEAD
#define LOOKAHEAD (5)
#endif


int nfix=10;

extern char * optarg;
char * myhost;

// some globals 
extern unsigned char vflag;
const unsigned char True=1;
const unsigned char False=0;
static char * myname;
//extern int errno;

Flags flags;

static void svn_id_file(FILE * fp){
   fprintf(fp,"%s: SVN ID: $Id: test_main.c 347 2014-05-21 15:15:57Z kny48981 $\n",myname);
   fprintf(fp,"%s: SVN URL: $URL: file:///home/kny48981/SVN/progs/dezing_cython/test_main.c $\n",myname);
   fprintf(fp,"%s: SVN header ID: %s\n","options.h",OPTIONS_H);
}

static void usage(int argc, char **argv){
   // while (( o = getopt(argc,argv, "S:B:d:m:I:O:D:i:o:l:w:b:s:p:u:n:hZ:z:vJ:a:f:") ) != -1){
   printf("Usage:\n");
   printf("%s [options]\n",argv[0]);

   printf("-i input dir (REQUIRED)\n");
   printf ("-o output dir (REQUIRED)\n");
   printf("\n");

   printf("-I Input format string (default  p_%%05d.tif)\n"); 
   printf("-O c-style string format for output files\n");
   printf("\n");
   printf("-S Settings folder (for log files etc) \n"); 
   printf("\n");

   printf("-C  crop start (left)\n");
   printf("-c  crop width \n");
   printf("-T  crop start (top)\n");
   printf("-t  crop length (vertical)\n");
   printf("\n");

   printf("-u  outlier detection parameter \n");
   printf("\n");

   
   printf ("-s number of segments (default 1)\n");
   printf ("-p number of images per segment (default 100) \n");
   printf ("-n number of chunks (default 8)\n");
   printf ("-m my chunk number (default 0)\n");
   printf ("-a number of images in a batch (default 10 )\n");

   printf ("-b input data type;  bytes per pixel (default 2)\n");
   printf ("-Z timeout (default 3 seconds)\n" );
   printf ("-z check interval (default 1 second) \n");

   printf ("-J job name (used to decorate output file names) \n");
   printf ("-v verbose messages\n");
}


void zeroflags(Flags *f){
   memset(f,0,sizeof(Flags));
}


void print_opts(Options *o, FILE * fp){
   fprintf(fp,"image_size_bytes: %llu\n",o->image_size_bytes);
}

void free_opts(Options * o){
   free (o->indir);
   free (o->outdir);
   free (o->jobname);
}




int parseopts (int argc, char **argv,Options * options){
   int o;
   unsigned char flagerr = 0;
   char defaultjob[32];
   pid_t mypid;
   mypid=getpid();
   snprintf(defaultjob,32,"p%u",(unsigned int)mypid);

   zeroflags (&flags);
   options->bytes=2; /* default */
   options->obytes=2; /* default */
   options->batchnum=1;
   options->nsegs=1;
   options->wd=4008;
   options->image_len=2672;
   options->nchunks=16;
   options->mychunk=0;
   options->fname=strdup("flat.tif");
   options->infmt=strdup("p_%05d.tif");
   options->outfmt=strdup("p_%05d.tif");
   options->uval=0.01;
   options->beta=1.0e-9;
   options->energy=53.0;
   options->distance=500;
   options->pixelsize=10.0;
   options->deltaratio=1e-3;
   options->croptop=0;
   options->cropbot=0;
   options->cropleft=0;
   options->cropright=0;
   options->cropwd=0;
   options->croplen=0;
   options->fftw_level=0;
   options->outlier_mu=2.5;
   options->delta=options->deltaratio*options->beta;
   options->versionflag=0;
   flags.d=False;
   flags.crop=False;
   if (argc <= 1){
      usage(argc,argv);
      exit(0);
   }

   while (( o = getopt(argc,argv, "a:x:B:b:C:c:D:d:E:W:f:hI:i:J:l:m:n:O:o:p:s:S:T:t:u:vVw:X:Z:z:K:") ) != -1){



      switch(o) {
      case 'B':
          options->beta=atof(optarg);
      break;
      case 'D':
          options->delta=atof(optarg);
      break;
      case 'W':
          options->fftw_level=(u_int8_t)(atoi(optarg));
      break;

      case 'K':
          nfix=atoi(optarg);
      break;
      case 'V':
          options->versionflag=1;
      break;

      case 'C':
          options->cropleft=atoi(optarg);
          flags.crop=True;
      break;
      case 'c':
          options->cropwd=atoi(optarg);
          flags.crop=True;
      break;
      case 'T':
          options->croptop=atoi(optarg);
          flags.crop=True;
      break;
      case 't':
          options->croplen=atoi(optarg);
          flags.crop=True;
      break;

      case 'E':
          options->energy=atof(optarg);
      break;
      case 'x':
          options->pixelsize=atof(optarg);
      break;
      case 'X':
          options->distance=atof(optarg);
      break;
      case 'u':
          options->outlier_mu=atof(optarg);
      break;

      case 'S':
          options->settingsfolder=strdup(optarg);
          flags.S=True;
      break;

      case 'i':
          options->indir=strdup(optarg);
          flags.i=True;
      break;
      case 'I':
          options->infmt=strdup(optarg);
          printf("Using infmt option\n");
          flags.Iflag=True;
      break;
      case 'O':
          options->outfmt=strdup(optarg);
          printf("Using outfmt option with %s\n",options->outfmt);
          flags.O=True;
      break;
      case 'd':
          options->dname=strdup(optarg);
          flags.d=True;
          if (strcasecmp(options->dname,"NONE") == 0){
             flags.d=False;
          }
      break;
      case 'f':
          options->fname=strdup(optarg);
          flags.f=True;
      break;
      case 'o':
           options->outdir=strdup(optarg);
           flags.o=True;
      break;
      case 'J':
           options->jobname=strdup(optarg);
           flags.J=True;
      break;
      case 'a':
           options->batchnum=atoi(optarg);
           flags.a=True;
      break;
      case 'l':
           options->image_len=atoi(optarg);
           flags.h=True;
      break;
      case 'w':
           options->wd=atoi(optarg);
           flags.w=True;
      break;
      case 'b':
           options->bytes=atoi(optarg);
           flags.b=True;
      break;
      case 's':
           options->nsegs=atoi(optarg);
           flags.s=True;
      break;
      case 'p':
           options->nperseg=atoi(optarg);
           flags.p=True;
      break;
      case 'n':
          options-> nchunks=atoi(optarg);
      break;
      case 'm':
          options-> mychunk=atoi(optarg);
          flags.m=True;
      break;
      case 'h':
           usage(argc,argv);
           exit(0);
      break;
      case 'Z':
          options->timeout=atoi(optarg);
          flags.Z=True;
      break;
      case 'z':
          options->interval=atoi(optarg);
          flags.z=True;
      break;
      case 'v':
          flags.v=True;
      break;
      case '?':
           printf( "Unhandled option\n");
           printf ("option %i (%c) value %s\n" , optopt,optopt,optarg);
           usage(argc,argv);
           //return(2);
           break;
      default:
           printf( "Problem in parsing options\n");
           printf ("option %i value %s\n" , o,optarg);
           usage(argc,argv);
           return(2);
           break;
      }
   }

   flagerr=False;



   if ( !(flags.h && flags.w)){
      errprint("Default values used for width or chunk length");
   }


   if (flags.s == 0 ){
      errprint ("number of segments default used: 1");
      options->nsegs=1;
   }

   if (flags.S == 0  ){
      /* default folder */
      options->settingsfolder=strdup("./");
   }

   if (flags.p == 0){
      errprint ("number of projections per segment default used: 100");
      options->nperseg=100;
   }
      
   if ( !(flags.z)){
      errprint("time-out check interval default used");
      options->interval=1;

   }
   if ( !(flags.Z)){
      errprint("time-out interval default used");
      options->timeout=3;
   }

   if ( !(flags.i && flags.o)){
      errprint("FATAL: Input and Output directories must be specified");
      flagerr=True;
   }
   if ( !(flags.a )){
      options->batchnum=10;
      errprint(" Number of images for a batch  not specified using default 10");
   }else{
      if(options->batchnum < 1 ){
         errprint("FATAL: Cannot specify zero or negative number of images for averaging");
         flagerr=True;
      }
   }

   if (flagerr != False){
      errprint("Not all options were correctly specified");
      usage(argc,argv);
      return(3);
   }

   options->deltaratio=options->beta/options->delta;

   /* check for unsupported data types */
   if (flags.b == True) {
      if (options->bytes != 2 ){
         errprint(" Only 2-byte data supported at present " );
         return(12);
      }
   }
   /* check for too many files */
   if (options->image_len >= 3000){
      errprint("Processing not feasible with > 3000 rows");
      return(13);
   }
   /* put verbosity in global flag*/
   vflag=flags.v;
   /* default job name */
   if (flags.J == False){
      options->jobname=strdup(defaultjob);
   }
   return(0);
}/* end of parseopts */



int main (int argc, char ** argv) {
   Options ctrl;
   u_int16_t * inarray;
   u_int16_t * outarray;
   u_int16_t width,length,batch;
   u_int32_t allsize;
   u_int32_t idx;
   int i,j,k;
   width=100;
   length=100;
   batch=50;
   allsize=width*length*batch;

   ctrl.versionflag=0;
   ctrl.versionflag=0;
   ctrl.outlier_mu=0.7;
   ctrl.cropwd=width;
   ctrl.nlines=length;

   timestamp_open("test_main.log");
   timestamp_init();
   timestamp("allocating the main buffers");
   inarray=(u_int16_t *)calloc(allsize,sizeof(u_int16_t));
   outarray=(u_int16_t *)calloc(allsize,sizeof(u_int16_t));
   timestamp("finished allocating the main buffers");

//   for (k=0;k<batch;k++){
 ////     for (j=0;j<length;j++){
   //      for(i=0;i<width;i++){
    //        idx=k*width*length+j*width+i;
     //       inarray[idx]=idx;
//         }
 //     }
  // }

   for (i=0;i<allsize;i++){
      inarray[i]=i;
   }



   timestamp("Calling setup");
   ctrl.f_call_num=0;
   runDezing(&ctrl,batch,(u_int8_t *)(inarray),(u_int8_t *)(outarray));

   timestamp("Calling run");
   ctrl.f_call_num=1;
   runDezing(&ctrl,batch,(u_int8_t *)(inarray),(u_int8_t *)(outarray));

   for(i=0;i<10;i++){
      timestamp("Calling run again");
      ctrl.f_call_num=1;
      runDezing(&ctrl,batch,(u_int8_t *)(inarray),(u_int8_t *)(outarray));
   }

   timestamp("Calling cleanup");
   ctrl.f_call_num=2;
   runDezing(&ctrl,batch,(u_int8_t *)(inarray),(u_int8_t *)(outarray));
   {
      FILE * outfp;
      outfp=fopen("raw.out","w");
      fwrite(outarray,sizeof(u_int16_t),allsize,outfp);
      fclose(outfp);
   }

      timestamp("Calling run again after cleanup");
      ctrl.f_call_num=1;
      runDezing(&ctrl,batch,(u_int8_t *)(inarray),(u_int8_t *)(outarray));
      printf("ctrl return flag:%hhu\n",ctrl.returnflag);
      

   timestamp("freeing the main buffers");
   free(inarray);
   free(outarray);
   timestamp("finished freeing the main buffers");
   timestamp_close();

   return(0);
}

