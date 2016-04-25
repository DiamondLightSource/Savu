#include <stdio.h>
#include <iostream>
#include <typeinfo>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <limits.h>
#include <unistd.h>
#include "imagenorm.h"
#include "tifwrite.h"
#include "options.h"
#include "timestamp.h"
#define SVN_ID_UNWARP_FUNCTIONS_CPP "$Id: unwarp_functions.cpp 451 2016-01-04 15:08:19Z kny48981 $"

#define F_SETUP (0)
#define F_RUN (1)
#define F_CLEANUP (2)
#ifdef SAVU
#define printf(...)
#endif


//
// some globals 
unsigned char vflag = 0; /* flag for verbose output */
const unsigned char True = 1; /* convenience values */
const unsigned char False = 0; /* convenience values */
FILE *logfp ; /* log file  available anywhere */
char *myname;       /* convenience to store the name of the program */

extern double find_new_radius (double a, double b, double c, double d, double r);

// extern void cuda_device_init (void);
/* this isn't the CUDA version */


#ifdef BITS16
    typedef  u_int16_t Pixeltype;
#   warning BITS16 DEFINED
#elif defined BITS32

    typedef  float Pixeltype;
#   warning BITS32 DEFINED

#else
#   error BITS NOT DEFINED
#endif

#if defined(BITS16) && defined(BITS32)
#error BITS16 and BITS32 BOTH DEFINED!
#endif

#   define MINVAL (0);
#   define MAXVAL (65535);

#   define MINVAL32 (-1e10);
#   define MAXVAL32 (1e10);

/* insert suitable values for other datatypes here .. */



#define DL (0)
#define DR (1)
#define UL (2)
#define UR (3)

template < typename T > struct Warper{
   /* object to handle the optical distortion correction */
  float cx,cy;
  u_int32_t wd,ht;
  T * imagedat;
  T *inputbuf,*outputbuf;
  const static T valmin ;
  const static T valmax ;
  const static T outside = 0;
  float aa,bb,cc,dd,ee;
  typedef T mypixel;

  void setptr(u_int8_t * input, u_int8_t * output){
     inputbuf=(T *)(input);
     outputbuf=(T *)(output);
  }

  struct Interp_tab {
     bool is_alloc;
     int npix;
     off_t * offsets;
     off_t uroff,uloff,droff,dloff;
     float * weights;
     u_int8_t * is_outside;


     Interp_tab(){
        is_alloc=0;
        npix=0;
        timestamp("Instantiated interpolation table",LEVEL_DEBUG);
     }

     ~Interp_tab(){
        if (is_alloc == 1 ){
           free(offsets);
           free(weights);
           free(is_outside);
           is_alloc=0;
           npix=0;
        }
        //timestamp("Cleared interpolation table",LEVEL_DEBUG);
     }


     void allocate(int N){
        /* is the parameter being changed but already a table allocatedd? */
        if (is_alloc == 1 ){
           /* is the size being changed?*/
           if (npix !=N){
              free(offsets);
              free(weights);
              free(is_outside);
              is_alloc=0;
           }
        }

        /* if only the parameter is changed don't reallocate */
        if(is_alloc == 0 ){
           npix=N;
           offsets=(off_t *)calloc( 4*npix,sizeof(off_t));
           weights=(float *)calloc( 4*npix,sizeof(float));
           is_outside=(u_int8_t *)calloc( npix,sizeof(u_int8_t));

           uroff=UR*npix;
           uloff=UL*npix;
           droff=DR*npix;
           dloff=DL*npix;

           timestamp("Allocated interpolation table",LEVEL_DEBUG);
           is_alloc=1;
        }
     }
  } itab;

  void allocate_itab(){
     itab.allocate(wd*ht);
  }


  /* DEBUG_X */
  int thisx,thisy;

  Warper(){
     timestamp("Hello, world!",LEVEL_DEBUG);


  };
  void helloworld(){
     timestamp("Hello, world!",LEVEL_DEBUG);
  }



  /* trying ot be c++ style oriented .. access methods */
  void setheight(int newht){
     ht = newht;
   };
  void setwidth(int newwd){
     wd = newwd;
   };

  void setdata(T * id){
     imagedat = id;
  };
     
  void setctr(float xxx, float yyy){
	  cx = xxx;
	  cy = yyy;
  };

  void setcoeff(float a1, float a2, float a3,float a4,float a5){
     /* set the coefficients of a  fifth order polynomial  without constant*/
    aa=a1;
    bb=a2;
    cc=a3;
    dd=a4;
    ee=a5;
   }

   float calcdist( float *x, float *y){
      return  (sqrt(*x * *x + *y * *y));
   }

  float unwarpfunc(float * d){
     /* calculate the inverse polynomial of the suppled value (radius) */
      double result;
      result=find_new_radius(aa,bb,cc,dd,*d);

     return  (float)(result);

  };


  float warpfunc(float * d){
     /* calculate the polynomial of the suppled value (distance) */
     return   aa + bb * *d + cc * *d * *d + dd * *d * *d * *d + ee * *d * *d * *d * *d;
  };

  void setup_itab(){
     /* bilinear interpolation function */
      char message[MAX_MESSAGE];
      int up,down,left,right;
      off_t dloff,uloff,droff,uroff;
      float dlval,drval,ulval,urval,uval,dval,val=0;
      float dlweight,drweight,ulweight,urweight;
      T retval;
      float xp,yp;
      unsigned int i,j,idx;
      for (j=0;j< ht;j++){
         for (i=0;i<wd;i++){
            idx=j*wd+i;
            /* calculate the primed coordinate related to the pixel */
            /* i and j are the output (undistorted) pixel indices */
	    calcprime(&i,&j,&xp,&yp);

            down=(int) floorf(yp);
            up = down + 1;
            left=(int) floorf(xp);
            right = left +1 ;

            if (down < 0 || down >= ht 
               || up < 0 || up >= ht
               || left < 0 || left >= wd
               || right < 0 || right >= wd){
               itab.is_outside[idx]=1;
            }else{
               itab.is_outside[idx]=0;
            }

            
            /* calculate the offsets */
            itab.offsets[itab.uloff + idx] =  wd * up + left;
            itab.offsets[itab.uroff + idx] =  wd * up + right;
            itab.offsets[itab.dloff + idx] =  wd * down + left;
            itab.offsets[itab.droff + idx] =  wd * down + right;
            
            /* calculate the weight factors */
            ulweight = ( right - xp ) * ( yp-down);
            urweight = ( xp -left)  *   ( yp-down);

            dlweight = (right-xp)   *   (up-yp);
            drweight = (xp-left)    *   (up-yp);

            itab.weights[itab.uloff + idx]=ulweight;
            itab.weights[itab.uroff + idx]=urweight;
            itab.weights[itab.dloff + idx]=dlweight;
            itab.weights[itab.droff + idx]=drweight;

            if (ulweight < 0){
               snprintf(message,MAX_MESSAGE,"negative ulweight %i",idx);
               errprint(message,LEVEL_USER);
            }
            if (urweight < 0){
               snprintf(message,MAX_MESSAGE,"negative urweight %i",idx);
               errprint(message,LEVEL_USER);
            }
            if (dlweight < 0){
               snprintf(message,MAX_MESSAGE,"negative dlweight %i",idx);
               errprint(message,LEVEL_USER);
            }
            if (drweight < 0){
               snprintf(message,MAX_MESSAGE,"negative drweight %i",idx);
               errprint(message,LEVEL_USER);
            }
         }
      }


  };

  
   void dowarp_by_table(T * outimage){
      /* apply the distortion function to all pixels */
      unsigned int i,j,idx;
      float ulweight,urweight,dlweight,drweight;
      float ulval,urval,dlval,drval;
      float val;
      T newval;
      static int debug_ctr=0;
      for (j=0;j< ht;j++){
         for (i=0;i<wd;i++){
            idx=j*wd+i;


            if (itab.is_outside[idx] == 1 ){ /* check for outside points */ newval=outside;
            }else{
               ulweight=itab.weights[itab.uloff + idx];
               urweight=itab.weights[itab.uroff + idx];
               dlweight=itab.weights[itab.dloff + idx];
               drweight=itab.weights[itab.droff + idx];

               ulval=(float)(*(imagedat +itab.offsets[itab.uloff + idx]));
               urval=(float)(*(imagedat +itab.offsets[itab.uroff + idx]));
               dlval=(float)(*(imagedat +itab.offsets[itab.dloff + idx]));
               drval=(float)(*(imagedat +itab.offsets[itab.droff + idx]));

               val = ulweight * ulval + urweight * urval + dlweight * dlval + drweight * drval ;

               /* DEBUGGING */
               // val=dlval;
               //val=(65536 * ulweight);
#ifdef DEBUG_CTR
               if (debug_ctr == 0){
                  printf("ulval %f urval %f dlval %f drval %f\n",ulval,urval,dlval,drval);
                  printf("ulweight %f urweight %f dlweight %f drweight %f\n",ulweight,urweight,dlweight,drweight);
                  printf("val %f\n",val);

                  debug_ctr++;
               }
#endif /*DEBUG_CTR*/

               /* check and clamp datatype range */
                 if (val > (float)valmax){
                    newval = valmax;
                 } else  if (val < (float)valmin) {
                    newval = valmin;
                 }else{
                    newval = (T)(val);
                 }
            }

	   *(outimage + idx)=newval;

	 }
      }
   };

   void dowarp(T * outimage){
      /* apply the distortion function to all pixels */
      unsigned int i;
      unsigned int j;
      float xprime,yprime;
      T newval;

      for (j=0;j< ht;j++){
         for (i=0;i<wd;i++){
            /* calculate the primed coordinate related to the pixel */
            /* i and j are the output (undistorted) pixel indices */
	   calcprime(&i,&j,&xprime,&yprime);
           /* interpolate the value at the  primed coordinate */
           /* and store in the output image */
	   newval=interp(&xprime,&yprime);
	   *(outimage + j*wd + i)=newval;
	 }
      }
   };


	    

   void calcprime(unsigned int *x,unsigned  int *y , float * xp, float * yp){
      /* calculate transformed coordinates in xprime,yprime system */
      float dx,dy,dxp,dyp;
      float dist;
      float ratio;

      /* first calculate the distance */
      /* of the source coordinate from the optical centre */
      /* dx and dy are the translation of the undistorted coordinate from the optical centre */
      dx = float(*x) - float(cx);
      dy = float(*y) - float(cy);


      dist=calcdist(&dx,&dy);

      /* to the distance apply the optical distortion function */
      ratio=warpfunc(&dist);

      /* calculate the new coordinates */
      *xp=(float)cx + dx * (ratio);
      *yp=(float)cy + dy * (ratio);


   }/* end of calcprime routine */


  T interp(float * xp, float * yp){
     /* bilinear interpolation function */
      int up,down,left,right;
      off_t dloff,uloff,droff,uroff;
      float dlval,drval,ulval,urval,uval,dval,val=0;
      T retval;


      down=(int) floorf(*yp);
      up = down + 1;
      left=(int) floorf(*xp);
      right = left +1 ;

      /* is there a way to avoid this check ? */
      /* does it take up much time ? */
      if (down < 0 || down >= ht 
         || up < 0 || up >= ht
         || left < 0 || left >= wd
         || right < 0 || right >= wd){
		 return(outside);
      }

      /* interpolate  in floating point*/
      
      /*
      dloff =  wd * down + left;
      uloff =  wd * up + left;
      droff =  wd * down + right;
      uroff =  wd * up + right;
      */

      dlval = *(imagedat + wd * down + left);
      ulval = *(imagedat + wd * up + left);
      drval = *(imagedat + wd * down + right);
      urval = *(imagedat + wd * up + right);

      uval = ulval + (*xp - left) * (urval - ulval);

      dval = dlval + (*xp - left) * (drval - dlval);
      val = dval + (*yp -down) * (uval - dval);

     /* check the bounds  of the value */
      
     if (val > (float)valmax) retval = valmax;

     else  if (val < (float)valmin) retval = valmin;

     /* cast to the template type */
     else retval = (T) val;
     return(retval);

  };
};


/* create an object of the image warper , over the specified pixel datatype */
typedef Warper<Pixeltype> Warpertype;

   template <> const u_int16_t Warper<u_int16_t>::valmin = MINVAL;
   template <> const u_int16_t Warper<u_int16_t>::valmax = MAXVAL;

   template <> const float Warper<float>::valmin = MINVAL32;
   template <> const float Warper<float>::valmax = MAXVAL32;

void runUnwarp(Options * ctrlp, unsigned int thisbatch,unsigned char *inbuf, unsigned char * outbuf){
   Pixeltype *h_data=NULL,*h_final=NULL;
   static Warpertype warper;
   static u_int32_t npixels;
   static int iter=0;
   char message[MAX_MESSAGE];

   //printf("mypixel size %i\n",sizeof(Warpertype::mypixel));

   static unsigned char setupflag=0;
   u_int32_t slice=0;


     snprintf(message,MAX_MESSAGE,"calling %s",__func__);
           timestamp(message,LEVEL_INFO);

     snprintf(message,MAX_MESSAGE,"versionflag: %hhu",ctrlp->versionflag);
           timestamp(message,LEVEL_INFO);
           
     snprintf(message,MAX_MESSAGE,"pixelflag: %hhu",ctrlp->pixelflag);
           timestamp(message,LEVEL_INFO);

     snprintf(message,MAX_MESSAGE,"f_call_num: %hhu",ctrlp->f_call_num);
           timestamp(message,LEVEL_INFO);

     //warper.helloworld();

     switch(ctrlp->f_call_num) {

        case (F_SETUP): 
           snprintf(message,MAX_MESSAGE,"calling %s for setup",__func__);
           timestamp(message,LEVEL_USER);

           //fprintf(stderr,"C++: Running setup %i %i \n",ctrlp->ht,ctrlp->wd);
           timestamp("C++: Running setup",LEVEL_DEBUG);
           snprintf(message,MAX_MESSAGE,"C++: ht= %i wd= %i",ctrlp->ht,ctrlp->wd);
           timestamp(message,LEVEL_DEBUG);

           warper.setheight(ctrlp->ht);
           warper.setwidth(ctrlp->wd);
           warper.allocate_itab();
           warper.setctr(ctrlp->xcentre,ctrlp->ycentre);
           warper.setcoeff(ctrlp->acoeff,ctrlp->bcoeff,ctrlp->ccoeff,ctrlp->dcoeff,ctrlp->ecoeff);

           timestamp("C++: Running setup_itab",LEVEL_DEBUG);
           warper.setup_itab();

           npixels=ctrlp->ht * ctrlp->wd;

           snprintf(message,MAX_MESSAGE,"npixels = %u",npixels);
              timestamp(message,LEVEL_DEBUG);
           snprintf(message,MAX_MESSAGE,"testval = %li",(long int)(warper.itab.offsets[0]));
              timestamp(message,LEVEL_DEBUG);

           setupflag=1;
           timestamp("C++: Finished setup_itab",LEVEL_DEBUG);
        break;

        case (F_RUN):
           snprintf(message,MAX_MESSAGE,"C++: running unwarp chunk ht= %i wd= %i batch=%i iter=%i",ctrlp->ht,ctrlp->wd,thisbatch,iter); timestamp("C++: running unwarp chunk",LEVEL_DEBUG);
              timestamp(message,LEVEL_USER);
           snprintf(message,MAX_MESSAGE,"Running unwarp for %u slices ",thisbatch);
              timestamp(message,LEVEL_DEBUG);
           snprintf(message,MAX_MESSAGE,"npixels = %u",npixels);
              timestamp(message,LEVEL_DEBUG);
           snprintf(message,MAX_MESSAGE,"testval = %li",(long int)(warper.itab.offsets[0]));
              timestamp(message,LEVEL_DEBUG);
           snprintf(message,MAX_MESSAGE,"testout = %hhu",warper.itab.is_outside[0]);
              timestamp(message,LEVEL_DEBUG);

           if (setupflag == 0 ){
              fprintf(stderr,"ERROR: setup has not been called! \n");
              return;
           }


           h_data=(Pixeltype *)(inbuf);
           h_final=(Pixeltype *)(outbuf);

#ifndef SAVU
           { 
              static int testout=0;
              FILE * testoutp;
              if (testout == 0 ){
                 testoutp=fopen("testout.raw","w");
                 fwrite(h_data,sizeof(Pixeltype),npixels*thisbatch,testoutp);
                 fclose(testoutp);
                 testout=1;
              }
           }
#endif


           warper.setptr(inbuf,outbuf);

           for (slice=0; slice < thisbatch; slice++){
                warper.setdata(warper.inputbuf + slice * npixels );
                warper.dowarp_by_table(warper.outputbuf + slice * npixels );
           }
           timestamp("C++: finished unwarp chunk ",LEVEL_DEBUG);
           iter++;

        break;

        case(F_CLEANUP):
           snprintf(message,MAX_MESSAGE,"calling %s for cleanup",__func__);
           timestamp(message,LEVEL_USER);
        break;
     }
     
     snprintf(message,MAX_MESSAGE,"returning from %s",__func__);
           timestamp(message,LEVEL_USER);

}

#ifdef CMAIN
////////////////////////////////////////////////////////////////////////////////
// Main program
////////////////////////////////////////////////////////////////////////////////
int main (int argc, char **argv) {
  Pixeltype *h_data;
  char *h_byte;
  Pixeltype *h_final;
  size_t totalblocks;
  float dval, sdev, floatdif;
  double difsq, sdev2;
  char *infile, *outfile, *fmtstring;
  size_t datasize;
  Mytiff mytiff;
  int inflag = 0, outflag = 0;
  int i,slice;
  int firstRun = 1;             // Indicates if it's the first execution of the for loop
  int dataAmount;
  int pret;
  float stats[4];
  Options ctrl;
  Warpertype warper;

#ifdef DEBUGBLOCK
  // cuda_device_init ();
#endif

  myname = basename (strdup (argv[0]));
  //printf ("argc: %i\n", argc);

  mytiff.wd = 0;
  mytiff.ht = 0;
  mytiff.bytes = 0;
  mytiff.bits = 0;

// parse command line arguments

  pret=parseopts (argc, argv, &ctrl);

  if (pret != 0 ){
     printf("Exiting ... \n");
     return(pret);
  }

  fmtstring = (char *) calloc (PATH_MAX, sizeof (char));
  infile = (char *) calloc (PATH_MAX, sizeof (char));
  outfile = (char *) calloc (PATH_MAX, sizeof (char));

//read first file to get the size
     snprintf (fmtstring, PATH_MAX, "%s/%s", ctrl.indir, ctrl.infmt);
     snprintf (infile, PATH_MAX, fmtstring, ctrl.firstslice);
     tifread (&mytiff, infile);
     datasize = mytiff.ht * mytiff.wd;
     dataAmount = datasize;
     //printf ("using file %s\n", infile);
     //
     h_data = (Pixeltype *) calloc (datasize, sizeof (Pixeltype));
     h_byte = (char *) h_data;
     h_final = (Pixeltype * ) calloc (datasize, sizeof (Pixeltype ));


  for (slice=ctrl.firstslice;slice <=ctrl.lastslice;slice++){
     snprintf (fmtstring, PATH_MAX, "%s/%s", ctrl.indir, ctrl.infmt);
     snprintf (infile, PATH_MAX, fmtstring, slice);
     //printf ("using file %s\n", infile);

     snprintf (fmtstring, PATH_MAX, "%s/%s", ctrl.outdir, ctrl.outfmt);
     snprintf (outfile, PATH_MAX, fmtstring, slice);
     //printf ("using output file %s\n", outfile);
     inflag = 1;
     outflag = 1;

     tifread (&mytiff, infile);

     datasize = mytiff.ht * mytiff.wd;
     dataAmount = datasize;
     //tifclose (&mytiff);

     //printf ("Initializing data...\n");


       size_t nread = 0;

       //printf ("Reading %lu bytes  from %s ... \n", datasize * sizeof (float), infile);
       tifread (&mytiff, infile);
       tifgetstripsdata (&mytiff, h_byte);

     //printf ("first data value = %e \n\n", h_data[0]);

     warper.settiff(&mytiff);
     warper.setdata(h_data);
     warper.setctr(ctrl.xcentre,ctrl.ycentre);
     warper.setcoeff(ctrl.acoeff,ctrl.bcoeff,ctrl.ccoeff,ctrl.dcoeff,ctrl.ecoeff);
     warper.dowarp(h_final);


     if (outflag == 1) {
       Mytiff outtiff;
       int retval = 0;
       int nwritten = 0;
       int i;

       //printf ("Writing %lu to %s\n", datasize, outfile);
       outtiff.wd = mytiff.wd;
       outtiff.ht = mytiff.ht;
       outtiff.bytes = 2;

       retval = tifinit (&outtiff, outfile);

       if (retval != 0) {
         fprintf (stderr, "%s: problem with tiff file init of %s\n", argv[0], outfile);
         fprintf (stderr, "%s: %s: %i:  returning %i\n", myname, __func__, __LINE__, retval);
         return (retval);
       }

       outtiff.data = (char *) (h_final);
       tifwrite (&outtiff, outfile);

     } else {
       printf ("write results not selected\n");
     }
  }
  //printf ("Cleaning up...\n");
  tifclose (&mytiff);
  free (h_data);
  free (h_final);
  return (0);
}
#endif /*CMAIN*/
