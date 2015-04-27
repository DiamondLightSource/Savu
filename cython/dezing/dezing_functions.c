#ifndef _REENTRANT
#define _REENTRANT
#endif

#include <stdlib.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <errno.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <complex.h>
#include <math.h>
#include <time.h>
#include <pthread.h>
#include "timestamp.h"
#include "options.h"

#ifndef PI
#define PI (3.14159265)
#endif /*  */

#ifndef PLANCK 
#define PLANCK (1240.0e-6)
#endif
static pthread_mutex_t count_mutex=PTHREAD_MUTEX_INITIALIZER; 
unsigned char vflag=0;

static void svn_id_file(FILE * fp){
   fprintf(fp,"%s: SVN ID: $Id: dezing_functions.c 380 2015-04-27 15:42:37Z kny48981 $\n",__FILE__);
   fprintf(fp,"%s: SVN URL: $URL: file:///home/kny48981/SVN/progs/dezing_cython/dezing_functions.c $\n",__FILE__);
   fprintf(fp,"%s: SVN header ID: %s\n","options.h",OPTIONS_H);
}

// Real data type
typedef float Real;




typedef struct filtdata_struct{

   u_int16_t * input16;
   u_int16_t * flat16;
   u_int16_t * dark16;
   u_int16_t * result16;

   Real * result;
   size_t * tsizes;
   int * origsizes;

   double outlier_mu;
} Filtdata;

typedef struct threadlimit_struct{
   u_int16_t mynum;
   int start;
   int end;
}Threadlimit;


static void * threaddezing (void * datap) ;
void timestamp(const char *const stampmsg);

static Filtdata g_filtdata;


void write_raw_16(const u_int16_t * const datap, const u_int32_t filenum,const size_t tsize,const u_int32_t batch,const char * const prefix) {
    FILE *ofp;
    char  fname[1024];
    size_t nw = 0;
    snprintf(fname,1024,"%s_%03d.raw",prefix,filenum);
    timestamp ("writing ...");
    ofp = fopen (fname, "w");
    nw = fwrite (datap, sizeof (u_int16_t), tsize * batch, ofp);
    printf ("wrote %i uint16 values to %s\n",nw,  fname);
    fclose(ofp);
}

void write_raw_real(const Real * const datap, const u_int32_t filenum,const size_t tsize,const u_int32_t batch,const char * const prefix) {
    FILE *ofp;
    char  fname[1024];
    size_t nw = 0;
    snprintf(fname,1024,"%s_%03d.raw",prefix,filenum);
    timestamp ("writing ...");
    ofp = fopen (fname, "w");
    nw = fwrite (datap, sizeof (float), tsize * batch, ofp);
    printf ("wrote %i float values to %s\n",nw,  fname);
    fclose(ofp);
}



void runDezing( Options *  ctrlp, u_int32_t  thisbatch,u_int8_t * inbuf, u_int8_t * outbuf){
/*
  const Options * const ctrlp: Pointer to the structure that contains all the options required
  u_int32_t  thisbatch: The number of image frames to process in this batch
  u_int8_t * inbuf: Pointer to a memory location containing the image frame data 
  u_int8_t * outbuf: Pointer to a memory location ALREADY allocated to contain the required output size
*/
  int retval=0;
  unsigned int i;
  long int numproc;
  char * envstring;
  unsigned short int nthreads=16;
  unsigned short int nthreadsmax=16;
  unsigned int chunksize,extra,istart=0;

  size_t batchsize, imagesize, sizex, sizey, batch ;
  int32_t batch_nopad;

  int  sizes[2];

  static char * logmessage;
  static char * fname;
  //static char * wfname;

  static pthread_t * thread;
  static Threadlimit * threadlimit;
  pthread_attr_t attr;
  void * status;

  /* handles to the buffer in uint16 type: NOT allocated in this fucntion , DON'T free these */
  u_int16_t * inbuf16 ;
  u_int16_t * outbuf16 ;
  u_int16_t * result16;



  static int alloc=0;
  static u_int32_t oldbatch=0;


  svn_id_file(stdout);
  printf("versionflag: %hhu\n",ctrlp->versionflag);
  printf("f_call_num: %hhu\n",ctrlp->f_call_num);
  printf("outlier_mu: %f\n",ctrlp->outlier_mu);

  if (ctrlp->versionflag != 0 ){
     if (ctrlp->versionflag == 2 ){
          // 2 -- test mode 
           inbuf16=(u_int16_t *)(inbuf);
           outbuf16=(u_int16_t *)(outbuf);
           printf("inbuf element 0 is %hu\n",inbuf16[0]);
           printf("outbuf element 0 is %hu\n",outbuf16[0]);
           outbuf16[0]=55;
           printf("set outbuf element 0 to %hu\n",outbuf16[0]);
     printf("quitting test mode\n");
     return;
     }

     if (ctrlp->versionflag == 5 ){
        /* set output mode to 5, store the test value instead of corrected value */
        vflag=5;
     }
  }

  envstring=getenv("NSLOTS");
  if (envstring == NULL){
     /* not running in the queue */
     /* use all the processors */
   numproc = sysconf( _SC_NPROCESSORS_ONLN );
  }else{
     /* running in the queue,*/
     /* get number of processors from the queue environment */
     numproc=atol(envstring);

     if (numproc < 1 ){
        fprintf(stderr,"WARNING: no processors detected! Something is wrong with the environment variable NSLOTS\n");
        numproc=2;
     }
  }


  nthreadsmax=numproc;
  inbuf16=(u_int16_t *)(inbuf);
  outbuf16=(u_int16_t *)(outbuf);


  /* get parameters from the options control structure */
    sizex = ctrlp->cropwd;
    sizey = ctrlp->nlines;
    batch = thisbatch;



  //calcuate derived sizes 
  /* sizes of the image */
  sizes[1] = sizey;
  sizes[0] = sizex;
  imagesize = sizex * sizey;
  batchsize = (imagesize * batch);
  printf("Image size to read : sizex %lu sizey %lu imagesize %lu batchsize %lu\n",sizex,sizey,imagesize,batchsize);

  /* number of slices in this batch */
  printf("thisbatch %i\n",thisbatch);

  /* how many threads will actually be used this time ? */
  if (thisbatch < nthreadsmax){
     nthreads=thisbatch;
  }else{
     nthreads=nthreadsmax;
  }

  switch (ctrlp->f_call_num){
     case(0):
        if (!alloc){
           alloc=1;
           //**************************
           timestamp("allocating the memory in dezing functions");
           printf("batchsize %i allocating the memory in dezing functions\n",batchsize);
           logmessage=(char *) calloc(MAX_MESSAGE , sizeof (char));
           fname=(char *) calloc(1024 , sizeof (char));
           printf("logmessage addr: %x\n",logmessage);

        /* array of threadspecific data , one for each thread */ 
        /* hmm..   when to free this array??*/
           thread=(pthread_t *)calloc(nthreadsmax,sizeof(pthread_t));
           threadlimit=(Threadlimit *)calloc(nthreadsmax,sizeof(Threadlimit));

           snprintf (logmessage, MAX_MESSAGE,"Threads available: %u \n", nthreadsmax);
           timestamp(logmessage);
           snprintf (logmessage, MAX_MESSAGE,"Threads used: %u \n", nthreads);
           timestamp(logmessage);

           timestamp("finished allocating the memory in dezing functions");
           ctrlp->returnflag=0;
           return;
        }else{
           fprintf(stderr,"ERROR: %s: attempted to double-allocate !\n",__func__);
           ctrlp->returnflag=5;
           return;
        }
     break;

     case(1):
        if (!alloc){
           fprintf(stderr,"ERROR: %s: attempted to run without allocating !\n",__func__);
           ctrlp->returnflag=5;
           return;
        }
        if(nthreads ==0){
           fprintf(stderr,"ERROR: %s: attempted to run with zero threads!\n",__func__);
           ctrlp->returnflag=5;
           return;
        }
       printf("logmessage addr: %x\n",logmessage);
     break;

     case(2):
     if(alloc){
        alloc=0;
        timestamp("freeing the memory in dezing functions");
        free(thread);
        free(threadlimit);
        free(logmessage);
        free(fname);
        timestamp("finished freeing the memory in dezing functions");
           ctrlp->returnflag=0;
        return;
     }else{
           fprintf(stderr,"ERROR: %s: attempted to double-free !\n",__func__);
           ctrlp->returnflag=5;
           return;
     }
     break;
     default:
           fprintf(stderr,"ERROR: %s: unknown call flag %i\n",__func__,ctrlp->f_call_num);
           ctrlp->returnflag=5;
           return;
     break;
  } 


  result16 = outbuf16;


  snprintf (logmessage, MAX_MESSAGE,"batchsize: %u \n", batchsize);
  timestamp(logmessage);
  snprintf (logmessage,MAX_MESSAGE, "sizes: %i %i batch %i \n",sizes[0],sizes[1],batch);
  timestamp(logmessage);


     pthread_attr_init(&attr);
     pthread_attr_setdetachstate(&attr, PTHREAD_CREATE_JOINABLE);

  /* calculate the slice numbers belonging to each thread  */
     batch_nopad=batch-(2*ctrlp->npad);

     chunksize=(int)floor(batch_nopad/nthreads);
     /* only slices inside the non-padded area sent to the threads */
     extra=batch_nopad-(chunksize*nthreads); /* calculate the extra slices after integer division into chunks */

     istart=ctrlp->npad;
     printf("npad: %i\n",ctrlp->npad);
     for (i=0;i<extra;i++){ // the first few chunks have an extra slice 
        threadlimit[i].mynum=i;
        threadlimit[i].start=istart;
        threadlimit[i].end=istart+chunksize+1;
        istart += chunksize+1;
     }
     for(;i<nthreads;i++){ // the rest of the chunks have the normal size
        threadlimit[i].mynum=i;
        threadlimit[i].start=istart;
        threadlimit[i].end=istart+chunksize;
        istart += chunksize;
     }

   g_filtdata.input16 = (inbuf16);

   timestamp ("starting filter setup");
   fprintf(stdout,"sizes: %li %li\n",sizes[0],sizes[1]);


  /* setup the global data that applies to all threads */

     /* the filter factor */
     g_filtdata.outlier_mu=ctrlp->outlier_mu;
     printf("set outlier mu to %f\n",g_filtdata.outlier_mu);

     /* the data locations */
     printf("g_filtdata.result16 %x\n",&(g_filtdata.result16));
     g_filtdata.result16=result16;
     g_filtdata.origsizes=sizes;


#ifdef WRITEINPUT
  // write out the input data in case of debugging 
  //
  write_raw_16(g_filtdata.input16,0,imagesize,batch,"Iinp");
#endif

  printf("running the dezinger correction ...\n");
  //timestamp("running thedezinger correction ...");
  //snprintf (logmessage, MAX_MESSAGE,"nthreads: %u \n", nthreads);
  //timestamp(logmessage);
#ifdef SINGLETHREAD
  /* mainly for debugging, just run the function once in the main thread */
     threadlimit[0].start=0;
     threadlimit[0].end=batch;

     /* call the function with limits 0 and total batch size */
     threaddezing((void *)(threadlimit));

     timestamp ("finished single threaddezing");
     printf (" finished single threaddezing  \n");

#else /* true multithread calculation of the filter */
  printf("launching threads:  %i ...\n" , nthreads);
  for (i=0;i<nthreads;i++){

  printf("launching thread %i ...\n" , i);
     retval=pthread_create(thread+i,&attr,threaddezing,(void *)(threadlimit+i));

     if (retval != 0 ){
        fprintf(stderr,"ERROR creating thread %i: code %i\n",i,retval);
     }
  }
 printf ("waiting for dezing threads\n");
 timestamp ("waiting for dezing threads");

  for (i=0;i<nthreads;i++){
     retval=pthread_join(thread[i],&status);
     if (retval != 0 ){
        fprintf(stderr,"ERROR joining thread %i: code %i\n",i,retval);
     }
#ifdef DEBUG_THREADDEZING
     else{
        fprintf(stdout,"SUCCESS joining thread %i: code %li\n",i,(long int)status);
     }
#endif /*DEGUG*/
     //snprintf(logmessage,MAX_MESSAGE,"finished joining thread %i: code %li\n",i,(long int)status);
     //timestamp(logmessage);
  }

 timestamp ("finished waiting for dezing threads");
 pthread_attr_destroy(&attr);


#endif/*SINGLETHREAD*/
ctrlp->returnflag=0;

}

////////////////////////////////////////////////////////////////////////////////
// Filtering operations
////////////////////////////////////////////////////////////////////////////////





   // 172x167
   //
/* the dezing function */
static float getfix(u_int16_t * inputs, int size){
   float sumsq;
   float mean;
   float sum;
   float diff,var,sdev;
   float testval;
   int i;
   sum=0;
   sumsq=0;
   
   for (i=0;i<size;i++){
         if (i != 2){
            sum += inputs[i];
         }
   }
   mean=sum/(size - 1 );
   //mean=sum/(size  );
   for (i=0;i<size;i++){
         if (i != 2){
            diff=(mean - inputs[i]);
            sumsq += diff * diff;
         }
   }
  // var=(1/((float)(size)-1))*(sumsq);
   var=(1/((float)(size)-2))*(sumsq);
   sdev=sqrtf(var);
   testval=fabsf((mean-inputs[2])/sdev);

   /* vflag 5 mode will return the test value scaled to be meaningful in  ushort */

   if (vflag == 5 ) return (testval * 1000);

   /* vflag 6 mode will just indicate the replaced pixels */
   if (testval > g_filtdata.outlier_mu){
      /* if the test is bad, then */
      /* form the mean of remaining pixels except this one */
      if (vflag == 6 ) return(50000);
      return(mean);

   }else{ /* return the original value */
      if (vflag == 6) return(0);
      return(inputs[2]);
   }

   return(-1);
}

static void * threaddezing (void * in_struct) {

           const static int thisnum=5; /* the number of neighbours in the neighbourhood */
           static int mynum=0;  /* counter for logging the thread number/slice number activity */
           int thisthread;
           Threadlimit * tlim; /* container for the thread-specific data passed in via void* */
           int i,j,k;
           long int   idx,rowidx,slicestart;
           int nbi,nbj,offset,nbidx;
           u_int16_t thisnb[thisnum]; /* array of neighbours */
           const  long int size = g_filtdata.origsizes[0]*g_filtdata.origsizes[1];
           const  int width=g_filtdata.origsizes[0];
           const  int height=g_filtdata.origsizes[1];

#ifdef DEBUG_ALGORITHM
           /* count the threads */
           pthread_mutex_lock(&count_mutex);
           thisthread=mynum;
           mynum++;
           pthread_mutex_unlock(&count_mutex);
           /********************/
#endif /* DEBUG_ALGORITHM */
           

           tlim = (Threadlimit *)(in_struct);

#ifdef DEBUG_ALGORITHM
           /* count the threads */
           pthread_mutex_lock(&count_mutex) ;
              printf("dezing: thread %i batchchunk %hi tlim %i %i\n",thisthread,tlim->mynum,tlim->start,tlim->end);
              printf("dezing: thread %i width %u height %u \n",thisthread,width,height);
           pthread_mutex_unlock(&count_mutex);
           /********************/
#endif /* DEBUG_ALGORITHM */

           idx=0;
           for (j=1;j<(size_t)(g_filtdata.origsizes[1])-1;j++){
              rowidx=j*(g_filtdata.origsizes[0]);
              for(i=1;i<g_filtdata.origsizes[0]-1;i++){
                 idx=rowidx+i;
                 slicestart=tlim->start * size; 

                 for (k=tlim->start ;k<tlim->end;k++){
                    for(nbj=-2;nbj<=+2;nbj++){
                          offset=nbj*size;
                          nbidx=(nbj+2);
                          thisnb[nbidx] = g_filtdata.input16[slicestart+idx+offset];
                    }/*neighbour j nbj*/
                       g_filtdata.result16[idx + slicestart ] = (u_int16_t)(getfix(thisnb,thisnum));
                       slicestart += size; /* increment the slice */
                 }/* slice k */
                 idx++; /* increment the in-plane index */
              } /* i index */

           }/* j index */


#ifndef SINGLETHREAD
           pthread_exit(NULL);
#endif

}

