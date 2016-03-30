#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <limits.h>
#include <unistd.h>
#include "options.h"
#include "timestamp.h"
#include "unwarp_functions.h"
#define SVN_ID_TEST_MAIN "$Id: testmain.cpp 444 2015-12-15 11:56:04Z kny48981 $"

Options  ctrl;

void setcoeff(float a, float b, float c, float d, float e){
   ctrl.acoeff=a;
   ctrl.bcoeff=b;
   ctrl.ccoeff=c;
   ctrl.dcoeff=d;
   ctrl.ecoeff=e;
}

int main(int argc,char **argv){
   unsigned char * inarray;
   unsigned char * outarray;
   unsigned int batchsize;
   batchsize=atoi(argv[1]);
   ctrl.wd=2000;
   ctrl.ht=2000;
   int k;

   inarray=(unsigned char * )calloc(batchsize * ctrl.wd*ctrl.ht,2);
   outarray=(unsigned char * )calloc(batchsize * ctrl.wd*ctrl.ht,2);
   timestamp_open("test.log");
   timestamp_init();

   ctrl.versionflag=0;

   for (k=0;k<10000;k++){
      setcoeff(1,-1e-5,0,0,0);
      ctrl.xcentre=1000;
      ctrl.ycentre=1000;
      ctrl.f_call_num=0;
      runUnwarp(&ctrl,batchsize,inarray,outarray);
      ctrl.f_call_num=1;
      runUnwarp(&ctrl,batchsize,inarray,outarray);
   }

   ctrl.f_call_num=2;
   runUnwarp(&ctrl,batchsize,inarray,outarray);
   timestamp_close();

   // run twice to check persistance of the lookup tables
   // runUnwarp(&ctrl,batchsize,inarray,outarray);

   free(inarray);
   free(outarray);

}
