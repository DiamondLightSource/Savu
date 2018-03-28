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

#include "tifwrite.h"
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

#ifndef NPAD
#define NPAD (2)
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


void calc_chunks(int64_t * cproj,int nchunksint,int nprojint,u_int32_t npad){
   float nchunks;
   float nperchunk;
   float nproj;
   float pad;
   int32_t chunkint;
   int32_t totalint;
   int32_t totalpad;
   int rem;
   int ochunk;
   int tpad;
   int pstart,thisp,thise,thisp_prime,thise_prime;
   int i;

   nchunks=(float)(nchunksint);
   nproj=(float)(nprojint);
   pad=(float)(npad);

   nperchunk=((nproj)/(nchunks));
   chunkint=(int)(ceilf(nperchunk));
   totalint=chunkint*(int)(nchunks);
   rem=totalint - (int)(nproj);

   ochunk=chunkint+2*npad;

   tpad=rem+2*npad;
   totalpad=nchunksint+tpad;


#ifdef DEBUG_CALC_CHUNKS
   printf("nchunks = %i\n",nchunksint);
   printf("nproj = %li\n",(nprojint));
   printf("npad = %u\n",(npad));
   printf(".........\n\n");
   printf("nperchunk float = %.5g\n",nperchunk);
   printf("nperchunk int = %u\n",chunkint);
   printf("total int = %u\n",totalint);
   printf("rem = %i\n",rem);
   printf("overlapping chunk size = %i\n",ochunk);
   printf("total padding required = %i\n",tpad);
#endif /*DEBUG_CALC_CHUNKS*/

   pstart=-npad;
   thisp=pstart;
   for (i=0;i<nchunksint;i++){
      thise=thisp+ochunk;

      thisp_prime=thisp+npad;
      thise_prime=thise-npad;
      printf("%i,%i,%i,%i,%i\n",i,thisp,thise,thisp_prime,thise_prime);
      cproj[2*i]=thisp;
      cproj[2*i+1]=thise;
      thisp+=chunkint;
   }
   return;
}









static void svn_id_file(FILE * fp){
   fprintf(fp,"%s: SVN ID: $Id: dezing_main.c 378 2015-04-27 14:18:19Z kny48981 $\n",myname);
   fprintf(fp,"%s: SVN URL: $URL: file:///home/kny48981/SVN/progs/dezing_cython/dezing_main.c $\n",myname);
   fprintf(fp,"%s: SVN header ID: %s\n","options.h",OPTIONS_H);
}

static void usage(int argc, char **argv){
   // while (( o = getopt(argc,argv, "S:B:d:m:I:O:D:i:o:l:w:b:s:p:u:n:hZ:z:v:J:a:f:") ) != -1){
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

static void getcropdata(Mytiff * mytiff,Options * options,u_int16_t * uncropbuf16,u_int16_t * inbuf16){
    size_t  inoffset,outoffset;
    int lct;
        /* reset the offsets */
             inoffset=options->inoffset;
             outoffset=0;

             tifgetstripsdata(mytiff,(char *)(uncropbuf16));
             for (lct=options->croptop;lct< options->cropbot;lct++){
                memcpy(inbuf16+outoffset,uncropbuf16+inoffset,options->cropwd*options->bytes);
                outoffset+=options->cropwd;
                inoffset+=options->wd;
             }
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

int checkahead(const Options * const ctrlp, const u_int32_t readahead,const char * const inpath){
          /* cheack for the file status to be good */
          /* look ahead a few files and check if that file has arrived yet */

         static char * aheadpath;
         static char * aheadfile;
         static char * message;
         static int allocflag=0;

         struct stat fstatus;
         int pausetime=(NOPAUSE);
         int wtime=0,found=0;
         int statret=0;

         if (!allocflag){
            aheadpath=   (char *)     calloc(PATH_MAX,sizeof(char));
            aheadfile=   (char *)     calloc(FILENAME_MAX,sizeof(char));
            message=     (char *)     calloc(MAX_MESSAGE,sizeof(char));
            allocflag=1;
         }

          snprintf (aheadfile, FILENAME_MAX, ctrlp->infmt, readahead);
          snprintf (aheadpath, PATH_MAX, "%s/%s", ctrlp->indir, aheadfile);
          snprintf (message, MAX_MESSAGE, "looking for %s ", aheadpath);
          timestamp (message);
          while (wtime <= ctrlp->timeout && found == False) {
            statret = stat (aheadpath, &fstatus);
            if (statret != 0) {
              snprintf (message, MAX_MESSAGE, "waiting for %s ", aheadpath);
              timestamp (message);
              wtime += ctrlp->interval;
              sleep (ctrlp->interval);
            } else {
              snprintf (message, MAX_MESSAGE, "found file  %s ", aheadpath);
              timestamp (message);
              found = True;
              timestamp ("Pausing ");
              usleep(pausetime);
              timestamp ("Finished Pausing ");
            }
          }
          timestamp ("Stopped looking for file");

          /* if it's still not found, time out */
          if (found == False) {
            snprintf (message, MAX_MESSAGE, "projection %s is not found after %i seconds!", aheadpath, wtime);
            errprint (message);
            return (7);
          }

          /* if it's still not good, time out */
          if (vflag) {
            snprintf (message, MAX_MESSAGE, "checking projection %s ", inpath);
            vprint (message);
          }
          timestamp ("Checking file status");
          statret = stat (inpath, &fstatus);
          if (statret != 0) {
            int myerror = errno;

            snprintf (message, MAX_MESSAGE, "status of projection %s is not good after %i seconds!", inpath, wtime);
            errprint (message);
            snprintf (message, MAX_MESSAGE, "Error: %s", strerror (myerror));
            errprint (message);
            return (27);
          }
          return(0);
}


int create_next_filename(char * outpath,Options * ctrlp,unsigned int i){
   static char * outfile;
   static char * message;
   static int allocflag=0;
   int retval=0;

   if (allocflag == 0 ){
      outfile=  (char *)    calloc(FILENAME_MAX,sizeof(char));
      message=  (char *)    calloc(MAX_MESSAGE,sizeof(char));
      allocflag = 1;
   }

  //create output filename
   snprintf(outfile,FILENAME_MAX,ctrlp->outfmt,i);
   snprintf(outpath,PATH_MAX,"%s/%s",ctrlp->outdir,outfile);

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

   while (( o = getopt(argc,argv, "a:x:B:b:C:c:D:d:E:W:f:hI:i:J:l:m:n:O:o:p:s:S:T:t:u:v:Vw:X:Z:z:K:") ) != -1){



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
          flags.v=atoi(optarg);
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
   options->npad=NPAD;
   return(0);
}/* end of parseopts */

/* test version , jsut copy the files */
void multiframe(const Options ctrl,const u_int32_t thisbatch, u_int8_t * imagebuf, u_int8_t * outbuf){
   int i;
   for (i=0;i<thisbatch;i++){
      memcpy(outbuf+i*ctrl.outimage_size_bytes,imagebuf+i*ctrl.image_size_bytes,ctrl.image_size_bytes);
   }
}/* end of multiframe function */

int closeall(const Options ctrl,Mytiff * outfp) {
   int j;
   int fcval=0;
   char message[MAX_MESSAGE];

       /* close all the sinogram files */
       vprint("Synchronizing and closing all the sinogram files");
       timestamp("Closing the sinogram files ");
          int tifffd;
          tifffd=TIFFFileno(outfp->tiffp);
          fsync(tifffd);
          TIFFClose(outfp->tiffp);
          tiffree(outfp);
         vprint("Done closing the  files");
         timestamp("Done closing the files ");
        snprintf(message,MAX_MESSAGE,"%s closing files  done ... ",myhost);
        return(0);
}

int main (int argc, char ** argv) {
   Options ctrl;
   struct timeval now;
   time_t etimes;
   double nowtime,etime;
   suseconds_t etimeu;
   int retval,statret;
   int oldpct,newpct;
   int wtime;
   int ssig;
   int npauses=0;


   size_t total_bytes_read=0,total_bytes_written=0;

   Mytiff  outfp;
   Mytiff firstfp;
   Mytiff darkfp;

   Mytiff * projfp;
   u_int8_t **linebuf;
   u_int8_t * imagebuf;
   u_int8_t * uncropbuf;
   u_int8_t *outbuf,*outstart;
   u_int8_t * flatbuf, *darkbuf;
   u_int16_t * flatbuf16, *darkbuf16;
   u_int16_t * uncropbuf16;
   off_t tiffoffset;
   u_int64_t image_size,linebytes,mystartrow;
   int32_t nproj;
   int32_t chunkstart,chunkend,chunk_data_start,chunk_data_end;
   u_int64_t startproj,endproj,cboundary,chunkproj,extraproj;

   int64_t *cproj;
   int32_t i,j,found,thisbatch;
   int32_t projcount,batchstart;
   int32_t anum=1;
   char message[MAX_MESSAGE];
   char * outpath;
   char * outfile;
   char * inpath;
   char * logfile;
   char * infile;
   struct stat fstatus;
   size_t nread,nwrite;
   int readahead;

   int pausetime=0;

   /* store the (global) starting time-of-day */
   gettimeofday(&mystime,NULL);

   myname=basename(strdup(argv[0]));
   myhost=getenv("HOSTNAME");

   /* output to standard out  before the logfile is created */

   svn_id_file(stdout);
   nowtime=(double)(mystime.tv_sec) + ((double)(mystime.tv_usec) / 1.0e6);
   printf("hostname amount %% done ... elapsed absolute\n");
   printf("%s ",myhost);
   printf("none %% done ... %f %f\n",nowtime,nowtime);

/* Set up the signal handler to use SIGTERM */
signal (SIGTERM, catchit);
/* set up a signal handler to use SIGUSR1 (writeblock and exit) */
signal (SIGUSR1, catchit);
/* set up a signal handler to use SIGUSR2 (writeblock and continue) */
signal (SIGUSR2, catchit);

#ifdef ALLSIGS
for (ssig=1;ssig<32;ssig++){
  signal(ssig,catchit);
}
#endif

/* set up a signal handler to use SIGFPE (doesn't do anything, but you can s */
/* also requires linking with libfpe on the SGI , not sure how to do this on */
/* using gcc >=2.2 : use fenv.h functions , feenableexcepts() (in handlers.c */

#ifdef GNU_TRAP_FPE
enable_fpe_traps ();
signal (SIGFPE, float_error);
#endif

/* Parse the command line options */
   retval=0;
   retval=parseopts(argc,argv,&ctrl);

/* request only the version strings from subroutine files if that option is selected */
   if (ctrl.versionflag != 0){
      svn_id_file(stdout);
      runDezing(&ctrl,0,NULL,NULL);
      return(0);
   }

  /* stop here if there's any problem */
   if (retval != 0 ){
      fprintf(stderr,"%s: Problem parsing options\n",argv[0]);
      return(retval);
   }



   /* allocate strings for path and filenames */
   outfile = (char *) calloc(FILENAME_MAX,sizeof(char));
   outpath = (char *) calloc(PATH_MAX,sizeof(char));
   inpath  = (char *) calloc(PATH_MAX,sizeof(char));
   infile  = (char *) calloc(FILENAME_MAX,sizeof(char));
   logfile = (char *) calloc(FILENAME_MAX,sizeof(char));

   /*  */
   /* calculate subsidiary values */

   nproj=ctrl.nsegs*ctrl.nperseg;

   mystartrow=0;

   if (nproj < ctrl.nchunks){

      /*
      printf("ERROR: we don't like fewer projections %lu than parallel chunks %lu ... %lu  \n",nproj,ctrl.nchunks,ctrl.nchunks);
      fprintf(stderr,"Error; fewer projections than parallel chunks: nproj %lu nchunks %lu \n",nproj,ctrl.nchunks);
      */
   
      fprintf(stderr,"Error; fewer projections than parallel chunks:\n");
      fprintf(stderr," nproj %lu ...  \n",nproj);
      fprintf(stderr," nchunks %lu ...  \n",ctrl.nchunks);
      exit(0);
   }

   if (ctrl.mychunk >= ctrl.nchunks){
      fprintf(stderr,"ERROR: selected chunk number too great\n");
      fprintf(stderr," mychunk %lu ...  \n",ctrl.mychunk);
      fprintf(stderr," nchunks %lu ...  \n",ctrl.nchunks);
      exit(0);
   }

   if (ctrl.mychunk == ctrl.nchunks) {
   }

   if (ctrl.mychunk == 0) {
   }


   cproj=(int64_t * ) calloc(2*(ctrl.nchunks+1),sizeof(int64_t));

   /* Calculate the chunk boundaries */

   calc_chunks(cproj,ctrl.nchunks,nproj,ctrl.npad);




   /* set up the i/o handles */
   snprintf(logfile,FILENAME_MAX,"%s/%s.log",ctrl.settingsfolder,ctrl.jobname);
   logfp=fopen(logfile,"w");
   if (logfp == NULL){
      int myerror=errno;
      snprintf(message,MAX_MESSAGE,"log file open failed\n%s",strerror(myerror));
      errprint(message);
      return(21);
   }

   timestamp_init();
   snprintf(message,MAX_MESSAGE,"%s log file %s open",myhost,logfile);
   timestamp(message);


  nwrite=0;
  nwrite+=sprintf(message,"Command line: ");
  for (i=0;i<argc;i++){
     nwrite+=sprintf(message,"%s  %s ",message,argv[i]);
     if (nwrite >= MAX_MESSAGE) break;
  }
  timestamp(message);

  for (i=0;i<ctrl.nchunks;i++){
      snprintf(message,MAX_MESSAGE,"chunk boundary cproj  %i: start %li end %li datastart %li dataend %li",i,cproj[2*i] , cproj[2*i+1],cproj[2*i]+ctrl.npad,cproj[2*i+1]-ctrl.npad);
      timestamp(message);
   }
//exit(0);


   snprintf(message,MAX_MESSAGE,"Starting row using %u chunks ",ctrl.nchunks);
   timestamp(message);
      

   timestamp ("output folder check");
   {
     int myerror;
     mode_t mymask;
     mymask=umask(0000);
     timestamp ("stat output folder ");
     statret = stat (ctrl.outdir, &fstatus);
     myerror = errno;
     timestamp ("statret output folder ");
     //fprintf(stderr,"before: mode of %s is %04o\n",ctrl.outdir,fstatus.st_mode);
     if (statret != 0) {
       if (myerror == ENOENT) {
         snprintf (message, MAX_MESSAGE, "creating %s ", ctrl.outdir);
         timestamp (message);;
         mkdir (ctrl.outdir, 0777);
         chmod (ctrl.outdir,0777);
         snprintf (message, MAX_MESSAGE, "outfolder created %s ", ctrl.outdir);
         timestamp (message);;
       } else {
         snprintf (message, MAX_MESSAGE, "ERROR: %s line %i", strerror (errno),__LINE__);
         timestamp (message);
         fprintf (stderr, "%s\n", message);
       }
     } else {
       timestamp ("Found output folder ");
     }

   }
   timestamp ("end output folder check");

   /* get the name of the first file */


   printf("Calculating first file number\n");
   printf("my chunk is %i \n ",ctrl.mychunk);
          i=cproj[2*ctrl.mychunk];
   printf("start number is %i\n",i);
          if (i <=0){
   printf("start number %i is less than zero \n",i);
             projcount=0;
          }else if (i >= nproj){
   printf("start number %i is greater than %i \n",i,nproj);
             projcount=nproj;
          }else{
   printf("start number %i is ok \n",i);
             projcount =  i ;
          }
   printf("start number %i set to %i \n",i,projcount);
          snprintf (infile, FILENAME_MAX, ctrl.infmt, projcount);
          snprintf (inpath, PATH_MAX, "%s/%s", ctrl.indir, infile);
   printf("first file name set to %s \n",inpath);

     /* if the height or width are not specified, get from the first file which should match all inputs */
     if (flags.w == 0 ){
         firstfp.wd=0;
     }

     if (flags.h == 0 ){
         firstfp.ht=0;
     }

         firstfp.bytes=ctrl.bytes;
         firstfp.bits=8*ctrl.bytes;

          retval = tifread (&firstfp, inpath);
          timestamp ("Finished tiff open of first file");
          if (retval != 0) {
            snprintf (message, MAX_MESSAGE, "problem reading first file ");
            errprint (message);
            fprintf (stderr, "%s: Problem reading first file \n", argv[0]);
            fprintf (stderr, "%s: %s: %i:  returning %i\n", myname, __func__, __LINE__, retval);
            return (retval);
          }
          if (flags.w == 0){
             snprintf(message,MAX_MESSAGE,"getting width from first file: %i", firstfp.wd);
             timestamp(message);
             ctrl.wd=firstfp.wd;
          }
          if (flags.l == 0){
             snprintf(message,MAX_MESSAGE,"getting length from first file: %i", firstfp.ht);
             timestamp(message);
             ctrl.image_len=firstfp.ht;
          }


   if (ctrl.cropwd == 0 ){
      ctrl.cropwd = ctrl.wd - ctrl.cropleft;
      printf("default -- cropping full width %u\n", ctrl.cropwd);
   }

   if (ctrl.croplen == 0 ){
      printf("default --  cropping full length %u\n",ctrl.croplen);
      ctrl.croplen = ctrl.image_len-ctrl.croptop;
   }

   if (flags.crop){
      /* check cropping is sensible */
      if (ctrl.cropleft > ctrl.wd){
         fprintf(stderr,"%s: bad cropping: left value %lu exceeds width %lu\n",argv[0],ctrl.cropleft,ctrl.wd);
         return(8);
      }
      if (ctrl.cropleft + ctrl.cropwd > ctrl.wd){
         fprintf(stderr,"%s: bad cropping: region end %lu exceeds width %lu\n",argv[0],ctrl.cropwd+ctrl.cropleft,ctrl.wd);
         return(8);
      }
      if (ctrl.croptop > ctrl.image_len){
         fprintf(stderr,"%s: bad cropping: top value %lu exceeds length %lu\n",argv[0],ctrl.croptop,ctrl.image_len);
         return(8);
      }
      if (ctrl.croptop + ctrl.croplen > ctrl.image_len){
         fprintf(stderr,"%s: bad cropping: region bottom %lu exceeds length %lu\n",argv[0],ctrl.croplen+ctrl.croptop,ctrl.image_len);
         return(8);
      }

   ctrl.inoffset=ctrl.croptop*ctrl.wd + ctrl.cropleft;
   ctrl.cropbot=ctrl.croptop+ctrl.croplen;
   }

   /* calculate derived sizes of image parameters */
   ctrl.nlines=ctrl.croplen;
   ctrl.uncrop_image_size=ctrl.wd*ctrl.image_len;
   image_size=ctrl.cropwd*ctrl.croplen;
   ctrl.image_size_bytes=image_size * ctrl.bytes;
   ctrl.outimage_size_bytes=image_size * ctrl.obytes;
   ctrl.image_size=image_size;

   linebytes=ctrl.cropwd*ctrl.obytes;
   

   /* allocate for all image buffers */

   snprintf(message,MAX_MESSAGE,"allocating memory");
   timestamp(message);
   projfp = (Mytiff *) calloc(ctrl.batchnum,sizeof(Mytiff));
   uncropbuf = (u_int8_t *) calloc(ctrl.uncrop_image_size * ctrl.bytes,sizeof(u_int8_t *));

   imagebuf = (u_int8_t *) calloc(ctrl.batchnum*ctrl.image_size_bytes,sizeof(u_int8_t *));
   linebuf = (u_int8_t **) calloc(ctrl.batchnum,sizeof(u_int8_t *));

   outbuf = (u_int8_t * ) calloc(ctrl.batchnum * ctrl.outimage_size_bytes,sizeof(u_int8_t));
   flatbuf = (u_int8_t * ) calloc(ctrl.image_size_bytes,sizeof(u_int8_t));
   darkbuf = (u_int8_t * ) calloc(ctrl.image_size_bytes,sizeof(u_int8_t));

   darkbuf16=(u_int16_t *)(darkbuf);
   flatbuf16=(u_int16_t *)(flatbuf);
   uncropbuf16=(u_int16_t *)(uncropbuf);

   outstart=outbuf;

   snprintf(message,MAX_MESSAGE,"done allocating memory");
   timestamp(message);

/* set up the array of tiff pointers for the images in a batch*/

   for (anum=0;anum<ctrl.batchnum;anum++){
      projfp[anum].wd=ctrl.wd;
      projfp[anum].ht=ctrl.image_len;
      projfp[anum].bytes=ctrl.bytes;
      projfp[anum].bits=8*ctrl.bytes;
      linebuf[anum]=imagebuf+anum*ctrl.image_size_bytes;
   }

      outfp.wd=ctrl.cropwd;
      outfp.ht=ctrl.nlines;
      outfp.bytes=ctrl.obytes;

       oldpct=0;
       newpct=0;

     snprintf(message,MAX_MESSAGE,"%s %i %% done ...  ",myhost,newpct);
     timestamp(message);

          TIFFClose(firstfp.tiffp);
          snprintf (message, MAX_MESSAGE,"Finished closing first file");
          timestamp(message);

          /* buffers are allocated, call function to allocate buffers in the subroutine */

          ctrl.f_call_num=0;

          runDezing(&ctrl,0,imagebuf,outbuf); /* DEBUG: Why is the second arg equal to zero? This crashes the runDezing routine */

        chunkstart=cproj[2*ctrl.mychunk];
        chunkend=cproj[2*ctrl.mychunk + 1 ];
        chunk_data_start=chunkstart+ctrl.npad;
        chunk_data_end=chunkend-ctrl.npad;

     i = chunkstart;

     snprintf(message,MAX_MESSAGE,"starting chunk loop:  mychunk: %i starting (i):  %i ending: %i",ctrl.mychunk, i,chunkend);
     timestamp(message);
     printf("starting chunk loop\n %s\n",message);


     ctrl.f_call_num=1;

     /*****************************/
     /*                           */
     /* loop over the projections */
     /*                           */
     /*****************************/

     while (i<=chunkend) {
     /* i is the counter of the projection number */

        thisbatch=0;
        batchstart=0;

        /* loop over one processing batch */
        /* assemble the batch of images into a single memory location */

        for (anum = 0,thisbatch=0,batchstart=i; anum < ctrl.batchnum && i <= chunkend; anum++,i++,thisbatch++) {

           /* the complex counter loop is to cycle through batches until the chunk is finished, */
           /* even if there is not an integer number of batches in a chunk */
           /* In that case the final batch is a different size */


#ifdef MOREMESSAGES
          snprintf(message,MAX_MESSAGE,"batch loop: anum %i thisbatch %i i %i",anum,thisbatch, i);
          timestamp(message);
#endif

   snprintf(message,MAX_MESSAGE,"Calculating the file number");
   vprint(message);
   snprintf(message,MAX_MESSAGE,"loop number is %i",i);
   vprint(message);
          if (i <=0){
   snprintf(message,MAX_MESSAGE,"loop number %i is less than zero",i);
   vprint(message);
             projcount=0;
          }else if (i >= nproj){
   snprintf(message,MAX_MESSAGE,"loop number %i is greater than %i",i,nproj);
   vprint(message);
             projcount=nproj;
          }else{
   snprintf(message,MAX_MESSAGE,"loop number %i is ok",i);
   vprint(message);
             projcount =  i ;
          }
   snprintf(message,MAX_MESSAGE,"loop number %i set to %i",i,projcount);
   vprint(message);



          // try to look ahead 'LOOKAHEAD' files so that processing may continue while
          // frames are being acquired

          readahead = projcount + (LOOKAHEAD);
   snprintf(message,MAX_MESSAGE,"readahead number set to %i ",readahead);
   vprint(message);

          /* sort out some zero index/ one index/ issues */
          /* manage the last few files */

          if (readahead >=  chunkend){
   snprintf(message,MAX_MESSAGE,"readahead number  %i greater than boundary %i ",readahead,chunkend);
   vprint(message);
              readahead = chunkend - 1 ;
   snprintf(message,MAX_MESSAGE,"readahead number set to %i ",readahead);
   vprint(message);
          }

          if (readahead >=  nproj){
   snprintf(message,MAX_MESSAGE,"readahead number  %i greater than nproj %i \n Using padding algorithm",readahead,nproj);
   vprint(message);
              readahead = nproj ;
   snprintf(message,MAX_MESSAGE,"readahead number set to %i ",readahead);
   vprint(message);
          }

          snprintf(message,MAX_MESSAGE,"looking ahead to file number %lu",readahead);
          timestamp(message);
          pausetime = NOPAUSE;
          snprintf (infile, FILENAME_MAX, ctrl.infmt, projcount);
          snprintf (inpath, PATH_MAX, "%s/%s", ctrl.indir, infile);


          wtime = 0;
          found = 0;
          retval = 0;

          /* check for file having been written by another program*/
          retval=checkahead(&ctrl,readahead,inpath);

          /* returns something bad if it reaches the specified timeout */
          if (retval != 0 ){
             snprintf(message,MAX_MESSAGE,"ERROR: checking ahead returned %i\n",retval);
             errprint (message);
             return(retval);
          }

          /***************************/
          /*  the file is available  */
          /*    and ready to open    */
          /***************************/

          if (vflag >= 3){
          printf("CHECKLOOP: anum %i thisbatch %i batchstart %i i %i projcount %i\n",anum,thisbatch,batchstart,i,projcount);
          }

          if (vflag) {
            snprintf (message, MAX_MESSAGE, "Opening projection file %i/%i %s\n", i,anum, inpath);
            vprint (message);
          }
          snprintf (message, MAX_MESSAGE, "Opening projection file %i/%i %s", i,anum, inpath);
          timestamp (message);

          /* Open the tiff for reading using helper functions */
          retval = tifread ((projfp+anum), inpath);
          timestamp ("Finished tiff open");
          if (retval != 0) {
            snprintf (message, MAX_MESSAGE, "problem reading projection file %i/%i", i,anum);
            errprint (message);
            fprintf (stderr, "%s: Problem reading projection file %i/%i\n", argv[0], i,anum);
            fprintf (stderr, "%s: %s: %i:  returning %i\n", myname, __func__, __LINE__, retval);
            return (retval);
          }

          /* percent progress output */
          newpct = (int) floor ((100 * i) / nproj);
          if (newpct > oldpct) {
            oldpct = newpct;
            snprintf (message, MAX_MESSAGE, "%s %i %% done ... ", myhost, newpct);
            timestamp (message);
          }

          /* load the file data into the memory location */
               if (flags.crop) {
                 getcropdata((projfp+anum),&ctrl,uncropbuf16,(u_int16_t *)(linebuf[anum]));
               } else {
                 tifgetstripsdata ((projfp+anum), linebuf[anum]); 
               }

               snprintf (message, MAX_MESSAGE,"Finished reading frame %i",anum);
               timestamp (message);
               timestamp ("Closing projection file ");
               TIFFClose (projfp[anum].tiffp);
               timestamp ("Done closing projection file ");

               if (vflag >=3){
        printf("ENDOFLOOP: anum %i  < ctrl.batchnum  %i && i %i  < chunkend %i \n",anum,ctrl.batchnum,i,chunkend);
               }
        } /* end of loop (anum) for reading  one batch */
               if (vflag >=3){
        printf("AFTERLOOP: anum %i  < ctrl.batchnum  %i && i %i  < chunkend %i \n",anum,ctrl.batchnum,i,chunkend);
               }



        /* processs a batch */
#ifdef MOREMESSAGES
          snprintf(message,MAX_MESSAGE,"processing batch: thisbatch %i i %i anum %i",thisbatch, i,anum);
          timestamp(message);
#endif
        if (ctrl.batchnum > 1){
           /* set the pointer to the beginnign of the output batch */
           outbuf=outstart;
           snprintf(message,MAX_MESSAGE,"applying batch processing ");
           timestamp(message);
           printf("*** %i\n",i);


           print_opts(&ctrl,stdout);

           /* call the desired process algorithm for the batch */
           runDezing(&ctrl,thisbatch,imagebuf,outbuf);

           snprintf(message,MAX_MESSAGE,"finished batch processing");
           timestamp(message);
        }else{
           outbuf=outstart;
           memcpy(outstart,imagebuf,ctrl.image_size_bytes);
        }

#ifdef TESTRAW
        {
           static int batchno=0;
           char * taskstring;
           char  rawname[255];
           int taskno;
           static testraw=0;
           taskstring=getenv("SGE_TASK_ID");
           if (taskstring == NULL){
              taskno=0;
           }else{
              taskno=atoi(taskstring);
           }

           snprintf(rawname,255,"in_%i_%i.raw",taskno,batchno);
           if (testraw == 0 ){
              FILE * trfp;
              trfp=fopen(rawname,"wb");
              fwrite(imagebuf,sizeof(u_int8_t),thisbatch*ctrl.image_size_bytes,trfp);
              fclose(trfp);
           }
           //testraw = 1 ;
           batchno++;
        }
#endif
#ifdef TESTRAW
        {
           static int batchno=0;
           char * taskstring;
           char  rawname[255];
           int taskno;
           static testraw=0;
           taskstring=getenv("SGE_TASK_ID");
           if (taskstring == NULL){
              taskno=0;
           }else{
              taskno=atoi(taskstring);
           }
           snprintf(rawname,255,"out_%i_%i.raw",taskno,batchno);
           if (testraw == 0 ){
              FILE * trfp;
              trfp=fopen(rawname,"wb");
              fwrite(outbuf,sizeof(u_int8_t),thisbatch*ctrl.outimage_size_bytes,trfp);
              fclose(trfp);
           }
           //testraw = 1 ;
           batchno++;
        }
#endif
        /* */

           // output batch of  'anum' frames per batch
           // now the counter i contains the end index of the current batch
           // even if the last batch of a chunk is unequal to the rest
           //
        outbuf=outstart+ctrl.npad*ctrl.outimage_size_bytes;
        for (anum = batchstart+ctrl.npad;
             anum < i-ctrl.npad && anum < chunk_data_end ;
             anum++) {
               // create the output file

           //skip the padding at the beginning of the chunk
               if (anum < chunk_data_start) {
                  outbuf += ctrl.outimage_size_bytes;
                  continue;
               }

               create_next_filename(outpath,&ctrl,anum);

               retval=tifinit((&outfp),outpath);
#ifdef MOREMESSAGES
          snprintf(message,MAX_MESSAGE,"output loop: batchstart: %i anum: %i i: %i outpath: %s",batchstart,anum, i,outpath);
          timestamp(message);
          printf("%s\n",message);
#endif

               if (retval != 0){
                  snprintf(message,MAX_MESSAGE,"tiff init failed, filename is '%s'",outpath);
                  errprint(message);
                  fprintf(stderr,"%s: problem with tiff file init\n",argv[0]);
                  fprintf(stderr,"%s: %s: %i:  returning %i\n",myname,__func__,__LINE__,retval);
                  return(retval);
               }
               snprintf(message,MAX_MESSAGE,"donetifinit  output file -- %s",outpath);
               timestamp(message);
                 for (j = 0; j < ctrl.nlines; j++) {
                   nwrite = TIFFWriteScanline (outfp.tiffp, outbuf, j, 0);
                   total_bytes_written += linebytes;
                   if (nwrite != 1) {
                     snprintf (message, MAX_MESSAGE, "tiff line write failed for projection %i line %i", i, j);
                     errprint (message);
                     return (14);
                   }
                   outbuf += linebytes;
                 }

                 timestamp("Closing the output files ");

                 {
                 int tifffd;
                     tifffd=TIFFFileno(outfp.tiffp);
                     fsync(tifffd);
                     TIFFClose(outfp.tiffp);
                     tiffree(&outfp);
                     vprint("Done closing the output files");
                     timestamp("Done closing the output files ");
                 }

        } /* end of loop for output of one batch [anum] */

        if (i<=chunkend){
           i-=2*ctrl.npad;
        }
               if (vflag >=3){
        printf("PADLOOP: anum %i  < ctrl.batchnum  %i && i %i  < chunkend %i \n",anum,ctrl.batchnum,i,chunkend);
               }
        /* done with this batch */
        timestamp ("Done with this batch  ");
     }/* end of loop over a chunk [i] */




        snprintf(message,MAX_MESSAGE,"%s chunk done ...",myhost);
        timestamp(message);

        timestamp("running cleanup  ...");
        /* clean up */
           ctrl.f_call_num=2;
           runDezing(&ctrl,thisbatch,imagebuf,outbuf);

        timestamp("... finished running cleanup");
        /* clean up memory */

        vprint("Cleaning up the memory...");
        free(outpath);
        free(outfile);
        free(inpath);
        free(infile);
        free(imagebuf);
        free_opts(&ctrl);

         free(cproj);
         free(projfp);
         free(uncropbuf);
         free(linebuf);
         free(outstart);
         free(flatbuf);
         free(darkbuf);

        vprint("..Done");
        vprint("All Done");
        printf("%s closing log file ... \n",myhost);

        fclose(logfp);
        logfp=NULL;
        gettimeofday(&now,NULL);
        etimes = now.tv_sec - mystime.tv_sec;
        etimeu = now.tv_usec - mystime.tv_usec;
        etime = (double)(etimes)+((double)(etimeu))/(1e6);
        nowtime=(double)(now.tv_sec) + ((double)(now.tv_usec) / 1.0e6);

        printf("%s ... log file %s closed %f %f \n",myhost,logfile,etime,nowtime);
        free(logfile);

     return(0);
}

