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
#ifdef DEBUG_ALGORITHM
static pthread_mutex_t count_mutex=PTHREAD_MUTEX_INITIALIZER; 
#endif /*DEBUG_ALGORITHM*/
unsigned char vflag=0;

char gmessagebuf[MAX_MESSAGE];

extern void timestamp(const char *const stampmsg,const int loglevel);

static void svn_id_file(FILE * fp){

   //printf("%s: SVN ID: $Id: dezing_functions.c 464 2016-02-16 10:54:37Z kny48981 $\n",__FILE__);
   snprintf(gmessagebuf,MAX_MESSAGE,"%s: SVN ID: $Id: dezing_functions.c 464 2016-02-16 10:54:37Z kny48981 $",__FILE__);
   timestamp(gmessagebuf,LEVEL_USER);
   snprintf(gmessagebuf,MAX_MESSAGE,"%s: SVN URL: $URL: file:///home/kny48981/SVN/progs/dezing_cython/dezing_functions.c $",__FILE__);
   logprint(gmessagebuf,LEVEL_USER);
   snprintf(gmessagebuf,MAX_MESSAGE,"%s: SVN header ID: %s","options.h",OPTIONS_H);
   logprint(gmessagebuf,LEVEL_USER);
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


static Filtdata g_filtdata;


void write_raw_16(const u_int16_t * const datap, const u_int32_t filenum,const size_t tsize,const u_int32_t batch,const char * const prefix) {
    FILE *ofp;
    char  fname[1024];
    size_t nw = 0;
    snprintf(fname,1024,"%s_%03d.raw",prefix,filenum);
    timestamp ("writing ...",LEVEL_DEBUG);
    ofp = fopen (fname, "w");
    nw = fwrite (datap, sizeof (u_int16_t), tsize * batch, ofp);
    snprintf (gmessagebuf,MAX_MESSAGE,"wrote %zu uint16 values to %s",nw,  fname);
    logprint(gmessagebuf,LEVEL_DEBUG);
    fclose(ofp);
}

void write_raw_real(const Real * const datap, const u_int32_t filenum,const size_t tsize,const u_int32_t batch,const char * const prefix) {
    FILE *ofp;
    char  fname[1024];
    size_t nw = 0;
    snprintf(fname,1024,"%s_%03d.raw",prefix,filenum);
    timestamp ("writing ...",LEVEL_DEBUG);
    ofp = fopen (fname, "w");
    nw = fwrite (datap, sizeof (float), tsize * batch, ofp);
    printf ("wrote %zu float values to %s\n",nw,  fname);
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
  long int nprocavail=0;
  long int nslotsavail=0;
  char * envstring;
  unsigned short int nthreads=16;
  unsigned short int nthreadsmax=16;
  unsigned int chunksize,extra,istart=0;


  size_t batchsize, imagesize, sizex, sizey, batch ;
  int32_t batch_nopad;

  int  sizes[2];

 // static char * logmessage;
  static char  logmessage[MAX_MESSAGE];
  //static char * fname;
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



  snprintf(logmessage,MAX_MESSAGE,"versionflag: %hhu",ctrlp->versionflag);
  timestamp(logmessage,LEVEL_DEBUG);
  snprintf(logmessage,MAX_MESSAGE,"f_call_num: %hhu",ctrlp->f_call_num);
  timestamp(logmessage,LEVEL_DEBUG);
  snprintf(logmessage,MAX_MESSAGE,"outlier_mu: %f",ctrlp->outlier_mu);
  timestamp(logmessage,LEVEL_DEBUG);

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

  /* nproc refers to actual processor cores on the local system */
  /* nslots refers to the number of processors assigned by the resource manager (queue) system */
  /* nthreadsreq to the number requested by the script configuration or user input */
  /* nthreadsmax set to the most that shoudl be allowed */
  /* nthreads may be reduced if the batch of data is small */

  envstring=getenv("NSLOTS");
  nprocavail=sysconf( _SC_NPROCESSORS_ONLN );

  if (envstring != NULL){
     nslotsavail=atol(envstring);
  }

  if (ctrlp->nthreadsreq ==0){
     if (envstring == NULL){
        /* not running in the queue */
        /* use all the processors */
      nthreadsmax = nprocavail;
     }else{
        /* running in the queue,*/
        /* get number of processors from the queue environment */
        nthreadsmax=nslotsavail;

        if (nthreadsmax < 1 ){
           fprintf(stderr,"WARNING: no processors detected! Something is wrong with the environment variable NSLOTS\n");
           ctrlp->warnflag=1;
           nthreadsmax=2;
        }
     }
  }else{
     if((ctrlp->nthreadsreq > nslotsavail) && (nslotsavail != 0 )){
           fprintf(stderr,"WARNING: selected n-threads > nslots\n");
           fprintf(stderr,"nthreads %i > nslots %li\n",ctrlp->nthreadsreq,nslotsavail);
           snprintf(logmessage,MAX_MESSAGE,"WARNING: nthreads %i > nslots %li",ctrlp->nthreadsreq,nslotsavail);
           timestamp(logmessage,LEVEL_WARN);
           ctrlp->warnflag=1;
     }
     if(ctrlp->nthreadsreq > nprocavail){
           fprintf(stderr,"WARNING: selected n-threads > nprocs\n");
           snprintf(logmessage,MAX_MESSAGE,"WARNING: nthreads %i > nproc %li",ctrlp->nthreadsreq,nprocavail);
           timestamp(logmessage,LEVEL_WARN);
           ctrlp->warnflag=1;
     }
     nthreadsmax=ctrlp->nthreadsreq;
  }

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
  snprintf(logmessage,MAX_MESSAGE,"Image size to read : sizex %lu sizey %lu imagesize %lu batchsize %lu",sizex,sizey,imagesize,batchsize);
  timestamp(logmessage,LEVEL_INFO);


  /* number of slices in this batch */
  snprintf(logmessage,MAX_MESSAGE,"thisbatch %i",thisbatch);
  timestamp(logmessage,LEVEL_INFO);

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
           ctrlp->errflag=0;
           ctrlp->warnflag=0;
           svn_id_file(NULL);

           //**************************
           timestamp("allocating the memory in dezing functions",LEVEL_INFO);
           snprintf(logmessage,MAX_MESSAGE,"batchsize %zu allocating the memory in dezing functions",batchsize);
           timestamp(logmessage,LEVEL_INFO);
           //fname=(char *) calloc(1024 , sizeof (char));

        /* array of threadspecific data , one for each thread */ 
        /* hmm..   when to free this array??*/
           thread=(pthread_t *)calloc(nthreadsmax,sizeof(pthread_t));
           threadlimit=(Threadlimit *)calloc(nthreadsmax,sizeof(Threadlimit));

           snprintf (logmessage, MAX_MESSAGE,"Threads available: %u ", nthreadsmax);
           timestamp(logmessage,LEVEL_DEBUG);
           snprintf (logmessage, MAX_MESSAGE,"Threads requested: %u ", ctrlp->nthreadsreq );
           timestamp(logmessage,LEVEL_DEBUG);
           snprintf (logmessage, MAX_MESSAGE,"Threads used: %u ", nthreads);
           timestamp(logmessage,LEVEL_INFO);

           timestamp("finished allocating the memory in the dezing functions",LEVEL_INFO);
           ctrlp->returnflag=0;
           return;
        }else{
           snprintf(logmessage,MAX_MESSAGE,"ERROR: %s: attempted to double-allocate !",__func__);
           timestamp(logmessage,LEVEL_ERR);
           //exit(0);
           ctrlp->returnflag=5;
           ctrlp->errflag=1;
           return;
        }
     break;

     case(1):
        if (!alloc){
           fprintf(stderr,"ERROR: %s: attempted to run without allocating !\n",__func__);
           snprintf(logmessage,MAX_MESSAGE,"ERROR: %s: attempted to run without allocating !",__func__);
           timestamp(logmessage,LEVEL_ERR);
           ctrlp->returnflag=5;
           ctrlp->errflag=1;
           return;
        }
        if(nthreads ==0){
           fprintf(stderr,"ERROR: %s: attempted to run with zero threads!\n",__func__);
           snprintf(logmessage,MAX_MESSAGE,"ERROR: %s: attempted to run with zero threads!",__func__);
           timestamp(logmessage,LEVEL_ERR);
           ctrlp->returnflag=5;
           ctrlp->errflag=1;
           return;
        }
       //printf("logmessage addr: %x\n",logmessage);

       snprintf (logmessage, MAX_MESSAGE,"Threads available: %u ", nthreadsmax);
       timestamp(logmessage,LEVEL_DEBUG);
       snprintf (logmessage, MAX_MESSAGE,"Threads requested: %u ", ctrlp->nthreadsreq );
       timestamp(logmessage,LEVEL_DEBUG);
       snprintf (logmessage, MAX_MESSAGE,"Threads used: %u ", nthreads);
       timestamp(logmessage,LEVEL_INFO);
     break;

     case(2):
     if(alloc){
        alloc=0;
        timestamp("freeing the memory in dezing functions",LEVEL_INFO);
        timestamp("freeing thread",LEVEL_DEBUG);
        free(thread);
        timestamp("freeing threadlimit",LEVEL_DEBUG);
        free(threadlimit);
        //timestamp("freeing logmessage",LEVEL_DEBUG);
        //free(logmessage);
        //timestamp("freeing filename",LEVEL_DEBUG);
        //free(fname);
        timestamp("finished freeing the memory in dezing functions",LEVEL_INFO);
           ctrlp->returnflag=0;
        return;
     }else{
           fprintf(stderr,"ERROR: %s: attempted to double-free !\n",__func__);
           snprintf(logmessage,MAX_MESSAGE,"ERROR: %s: attempted to double-free !",__func__);
           timestamp(logmessage,LEVEL_ERR);
           ctrlp->returnflag=5;
           ctrlp->errflag=1;
           return;
     }
     break;
     default:
           fprintf(stderr,"ERROR: %s: unknown call flag %i\n",__func__,ctrlp->f_call_num);
           ctrlp->returnflag=5;
           ctrlp->errflag=1;
           return;
     break;
  } 


  result16 = outbuf16;


  snprintf (logmessage, MAX_MESSAGE,"batchsize: %zu", batchsize);
  timestamp(logmessage,LEVEL_INFO);
  snprintf (logmessage,MAX_MESSAGE, "sizes: %i %i batch %zu",sizes[0],sizes[1],batch);
  timestamp(logmessage,LEVEL_DEBUG);


     pthread_attr_init(&attr);
     pthread_attr_setdetachstate(&attr, PTHREAD_CREATE_JOINABLE);

  /* calculate the slice numbers belonging to each thread  */
     batch_nopad=batch-(2*ctrlp->npad);

     chunksize=(int)floor(batch_nopad/nthreads);
     /* only slices inside the non-padded area sent to the threads */
     extra=batch_nopad-(chunksize*nthreads); /* calculate the extra slices after integer division into chunks */

     istart=ctrlp->npad;
     snprintf(logmessage,MAX_MESSAGE,"npad: %i",ctrlp->npad);
     timestamp(logmessage,LEVEL_DEBUG);
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

   timestamp ("starting filter setup",LEVEL_INFO);
   fprintf(stdout,"sizes: %i %i\n",sizes[0],sizes[1]);


  /* setup the global data that applies to all threads */

     /* the filter factor */
     g_filtdata.outlier_mu=ctrlp->outlier_mu;
     snprintf(logmessage,MAX_MESSAGE,"set outlier mu to %f",g_filtdata.outlier_mu);
     timestamp(logmessage,LEVEL_DEBUG);

     /* the data locations */
     snprintf(logmessage,MAX_MESSAGE,"g_filtdata.result16 %p",(void *)(&(g_filtdata.result16)));
     timestamp(logmessage,LEVEL_DEBUG);

     g_filtdata.result16=result16;
     g_filtdata.origsizes=sizes;


#ifdef WRITEINPUT
  // write out the input data in case of debugging 
  //
     {
        static int counter=0;
           write_raw_16(g_filtdata.input16,counter,imagesize,batch,"Iinp");
           counter++;
     }
#endif

  timestamp("running the dezinger correction ...",LEVEL_INFO);
  //timestamp("running thedezinger correction ...");
  //snprintf (logmessage, MAX_MESSAGE,"nthreads: %u ", nthreads);
  //timestamp(logmessage);
#ifdef SINGLETHREAD
  /* mainly for debugging, just run the function once in the main thread */
     threadlimit[0].start=0;
     threadlimit[0].end=batch;

     /* call the function with limits 0 and total batch size */
     threaddezing((void *)(threadlimit));

     timestamp ("finished single threaddezing",LEVEL_INFO);

#else /* true multithread calculation of the filter */
  snprintf(logmessage,MAX_MESSAGE,"launching threads:  %i ..." , nthreads);
  timestamp(logmessage,LEVEL_DEBUG);
  for (i=0;i<nthreads;i++){
  snprintf(logmessage,MAX_MESSAGE,"launching thread %i ..." , i);
  timestamp(logmessage,LEVEL_DEBUG);

     retval=pthread_create(thread+i,&attr,threaddezing,(void *)(threadlimit+i));

     if (retval != 0 ){
        fprintf(stderr,"ERROR creating thread %i: code %i\n",i,retval);
        ctrlp->errflag=1;
     }
  }
 timestamp ("waiting for dezing threads",LEVEL_INFO);

  for (i=0;i<nthreads;i++){
     retval=pthread_join(thread[i],&status);
     if (retval != 0 ){
        fprintf(stderr,"ERROR joining thread %i: code %i\n",i,retval);
        ctrlp->errflag=1;

     }
#ifdef DEBUG_THREADDEZING
     else{
        fprintf(stdout,"SUCCESS joining thread %i: code %li\n",i,(long int)status);
     }
#endif /*DEGUG*/
     //snprintf(logmessage,MAX_MESSAGE,"finished joining thread %i: code %li\n",i,(long int)status);
     //timestamp(logmessage);
  }

 timestamp ("finished waiting for dezing threads",LEVEL_INFO);
 pthread_attr_destroy(&attr);


#endif/*SINGLETHREAD*/
#ifdef WRITEOUTPUT

  // write out the output data in case of debugging 
  //
     {
        static int counter=0;
           write_raw_16(g_filtdata.result16,counter,imagesize,batch,"Ioutp");
           counter++;
     }
#endif
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
           Threadlimit * tlim; /* container for the thread-specific data passed in via void* */
           int i,j,k;
           long int   idx,rowidx,slicestart;
           int nbj,offset,nbidx;
           u_int16_t thisnb[thisnum]; /* array of neighbours */
           const  long int size = g_filtdata.origsizes[0]*g_filtdata.origsizes[1];
#ifdef DEBUG_ALGORITHM
           static int mynum=0;  /* counter for logging the thread number/slice number activity */
           int thisthread;
           const  int width=g_filtdata.origsizes[0];
           const  int height=g_filtdata.origsizes[1];

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
              j=1;
              rowidx=j*(g_filtdata.origsizes[0]);

              //printf("dezing: thread %i batchchunk %hi tlim %i %i first rowidx: %i\n",thisthread,tlim->mynum,tlim->start,tlim->end,rowidx);
              //printf("dezing: thread %i width %u height %u \n",thisthread,width,height);
           pthread_mutex_unlock(&count_mutex);
           /********************/
#endif /* DEBUG_ALGORITHM */

           idx=0;
           //for (j=1;j<(size_t)(g_filtdata.origsizes[1])-1;j++)
           for (j=0;j<(size_t)(g_filtdata.origsizes[1]);j++)
           {
              rowidx=j*(g_filtdata.origsizes[0]);

              //for(i=1;i<g_filtdata.origsizes[0]-1;i++)
              for(i=0;i<g_filtdata.origsizes[0];i++)
              {
                 idx=rowidx+i;
                 slicestart=tlim->start * size; 

                 for (k=tlim->start ;k<tlim->end;k++){
                    for(nbj=-2;nbj<=+2;nbj++){ /*neighborhood loop */
                          offset=nbj*size;
                          nbidx=(nbj+2);
                          thisnb[nbidx] = g_filtdata.input16[slicestart+idx+offset];
#ifdef DEBUG_ALGORITHM
                          {
                             static int first=1;
                             int firstidx;
                             pthread_mutex_lock(&count_mutex) ;
                             if ( first == 1 && tlim->mynum==0 ){
                                firstidx=slicestart+idx+offset;
                                first=0;
                                printf("dezing: thread %i width %u height %u slicestart %i idx %i offset %i ",thisthread,width,height,slicestart,idx,offset);
                                printf(" batchchunk %hi tlim %i %i first nb idx: %i\n",tlim->mynum,tlim->start,tlim->end,firstidx);
                             }
                             pthread_mutex_unlock(&count_mutex);
                          }
#endif /* DEBUG_ALGORITHM */
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

