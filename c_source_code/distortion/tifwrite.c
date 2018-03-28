#define TIFWRITE_C
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>

#include "machine.h"
#include "tifwrite.h"

#ifndef MAX_MESSAGE
#define MAX_MESSAGE (1024)
#endif /*MAX_MESSAGE*/


int tiffree(Mytiff * mytiff){
   #ifdef INMEM
   free (mytiff->data);
   #endif
return(0);
}




int tifread_into_buffer(Mytiff * mytiff, void ** buffer){

}
/* obtain some values from the tiff and check if they are what was expected */
int tifgettags(Mytiff * mytiff){
   int row,cval;
   int32_t ww=0,hh=0,bb=0;


   cval=TIFFGetField(mytiff->tiffp,TIFFTAG_IMAGEWIDTH,&ww);
   if(cval != 1 ) {
      fprintf(stderr,"ERROR: %s: error reading width\n",__func__);
      return(103);
   }

   cval=TIFFGetField(mytiff->tiffp,TIFFTAG_ROWSPERSTRIP,&hh);
   //printf("rowsperstrip: %i\n",hh);
   mytiff->stripnum=TIFFNumberOfStrips(mytiff->tiffp);
   mytiff->stripsize=TIFFRawStripSize(mytiff->tiffp,0);


   cval=TIFFGetField(mytiff->tiffp,TIFFTAG_STRIPOFFSETS,&(mytiff->offsets));
   if(cval != 1 ) {
      fprintf(stderr,"ERROR: %s: error reading offsets\n",__func__);
      return(103);
   }

   cval=TIFFGetField(mytiff->tiffp,TIFFTAG_STRIPBYTECOUNTS,&(mytiff->bytecounts));
   if(cval != 1 ) {
      fprintf(stderr,"ERROR: %s: error reading bytecounts\n",__func__);
      return(103);
   }

   cval=TIFFGetField(mytiff->tiffp,TIFFTAG_IMAGELENGTH,&hh);
   if(cval != 1 ) {
      fprintf(stderr,"ERROR: %s: error reading length\n",__func__);
      return(103);
   }

   cval=TIFFGetField(mytiff->tiffp,TIFFTAG_BITSPERSAMPLE,&bb);
   if(cval != 1 ) {
      fprintf(stderr,"ERROR: %s: error reading bitspersample\n",__func__);
      return(103);
   }

   /* check validity of this tiff for the job */
   /* height and width should always match */
   /* unless zero then it's unknown */
   /* and the new value used */

    
   if (mytiff->wd != 0) {
       if(ww != mytiff->wd){
          fprintf(stderr,"ERROR: data mismatch in  %s!\n found ww=%i hh=%i bb=%i \n",__func__,ww,hh,bb);
          fprintf(stderr,"expected wd=%i ht=%i bits=%i \n",mytiff->wd,mytiff->ht,mytiff->bits);
         return(102);
       }
   }

   if (mytiff->ht != 0) {
       if(hh != mytiff->ht){
          fprintf(stderr,"ERROR: data mismatch in  %s!\n found ww=%i hh=%i bb=%i \n",__func__,ww,hh,bb);
          fprintf(stderr,"expected wd=%i ht=%i bits=%i \n",mytiff->wd,mytiff->ht,mytiff->bits);
         return(102);
       }
   }

   if (mytiff->bits != 0) {
       if(bb != mytiff->bits){
          fprintf(stderr,"ERROR: data mismatch in  %s!\n found ww=%i hh=%i bb=%i \n",__func__,ww,hh,bb);
          fprintf(stderr,"expected wd=%i ht=%i bits=%i \n",mytiff->wd,mytiff->ht,mytiff->bits);
          return(102);
       }
   }


   mytiff->ht = hh;
   mytiff->wd = ww;
   mytiff->bits=(bb);
   mytiff->bytes=(bb/8);
   mytiff->ndata=mytiff->wd * mytiff->ht;
   mytiff->nbytes = mytiff->ndata * mytiff->bytes;

   /* obtain the raw file io descriptor number */
   mytiff->tiffno=TIFFFileno(mytiff->tiffp);


return(0);
}

int tifclose(Mytiff * mytiff){
   int cval;
   TIFFClose(mytiff->tiffp);
   tiffree (mytiff);
   return(0);
}

/* just open the tiff and keep the pointer in a structure */
int tifread(Mytiff * mytiff, const char * const filename){
   int cval;

   mytiff->tiffp=TIFFOpen(filename,"rc");

   if (mytiff->tiffp == NULL ){
      fprintf(stderr,"%s: TIFFOpen function failed (returned NULL) for %s!\n",__func__,filename);
      return(101);
   } 


   cval=tifgettags(mytiff);
   return(cval);
}

void tifgetstripsdata(Mytiff * mytiff,char * buf){
/* buf is already allocated */
   int i;
   char * bstart;

   bstart=buf;
   for (i=0;i<mytiff->stripnum;i++){
      TIFFReadRawStrip(mytiff->tiffp,i,bstart,mytiff->stripsize);
      bstart+=mytiff->stripsize;
   }
}

int tifwrite(Mytiff * mytiff, const char * const filename){
   int i;
   char * datap;
   int row;
   row=mytiff->wd*mytiff->bytes;

   datap=mytiff->data;
   for (i=0;i<mytiff->ht;i++){
      TIFFWriteScanline(mytiff->tiffp,datap,i,0);
      datap += ( row );
   }
   TIFFClose(mytiff->tiffp);
return(0);
}

int tifinit(Mytiff * mytiff,const char * const filename){
   int myerror;
   char * Stripbytes=NULL;
   u_int32_t stripbytes,estsize,estbytes;

   
   myerror=0;
   mytiff->ndata=mytiff->wd * mytiff->ht;
   mytiff->nbytes = mytiff->ndata * mytiff->bytes;
   mytiff->tiffp= TIFFOpen(filename,"wl");
   if (mytiff->tiffp == 0 ){
      fprintf(stderr,"ERROR: %s: %i:  failed tiff open of %s!\n",__func__,__LINE__,filename);
      fprintf(stderr,"ERROR: %s: tried to open with TIFFOpen(%s,\"wl\");  \n",__func__,filename);
      return(101);
   } 
   TIFFSetField(mytiff->tiffp,TIFFTAG_IMAGEWIDTH,mytiff->wd);
   TIFFSetField(mytiff->tiffp,TIFFTAG_IMAGELENGTH,mytiff->ht);
   TIFFSetField(mytiff->tiffp,TIFFTAG_BITSPERSAMPLE,mytiff->bytes * 8);
   TIFFSetField(mytiff->tiffp,TIFFTAG_PLANARCONFIG,1);
   TIFFSetField(mytiff->tiffp,TIFFTAG_PHOTOMETRIC,1);

   Stripbytes=getenv("I12STRIPBYTES");
   //printf("stripbytes: %s\n",Stripbytes);

   if (Stripbytes == NULL ){
      TIFFSetField(mytiff->tiffp,TIFFTAG_ROWSPERSTRIP,mytiff->ht);
      //printf("stripbytes set to: %i\n",mytiff->ht);

   }else{
      stripbytes=atoi(Stripbytes);
      estbytes=(stripbytes / (mytiff->wd * mytiff->bytes));
      estsize=TIFFDefaultStripSize(mytiff->tiffp,estbytes);
      TIFFSetField(mytiff->tiffp,TIFFTAG_ROWSPERSTRIP,estsize);
      //printf("stripbytes set to: %i\n",estsize);
   }

   return(0);
}


#ifdef MAIN
/* a test main-procedure to see if it works */
int main (int argc,char **argv){
   char * filename;
   Mytiff  * mytiff;
   int i,j;
   u_int32_t loc;
   int retval;

   retval=0;
   mytiff = (Mytiff * ) calloc(1,sizeof (Mytiff));
   filename = strdup(argv[1]);
   mytiff->wd=1024;
   mytiff->ht=768;
   mytiff->bytes=2;
   //tifinit(&mytiff,argv[1]);
   #ifdef INMEM
   for (j=0;j<768;j++){
      for(i=0;i<1024;i++){
         loc=j*1024+i;
         loc *= 2;
         mytiff.data[loc]=(char)(i);
         mytiff.data[loc + 1]=(char)(j);
      }
   }
   #endif

   retval = tifread(mytiff,filename);
return(retval);
}
#endif
