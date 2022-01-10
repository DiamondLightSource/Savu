import numpy as np
cimport numpy as np
cimport cdezing


cdef cdezing.Options ctrl
cdef unsigned int batchsize

def getversion():
   global ctrl
   ctrl.versionflag=1
   cdezing.runDezing(&ctrl,0,NULL,NULL)


def setup_size(array_size,outlier_mu,npad,logfile="dezing.log",versionflag=0): #,bytes summary):
   global ctrl
   global batchsize

   /* ... some other python code here ... */

   cdezing.timestamp( "calling c function setup" )
   cdezing.runDezing(&ctrl,batchsize, NULL, NULL)
   pass

def setup(np.ndarray[np.uint16_t,ndim=3,mode="c"] inarray,np.ndarray[np.uint16_t,ndim=3,mode="c"] outarray,outlier_mu,npad,logfile="dezing.log",versionflag=0): #,bytes summary):

   /* ... some other python code here ... */

   cdezing.timestamp( "calling c function setup" )
   cdezing.runDezing(&ctrl,batchsize, inbuf, outbuf)
   pass

def run(np.ndarray[np.uint16_t,ndim=3,mode="c"] inarray,np.ndarray[np.uint16_t,ndim=3,mode="c"] outarray): #,bytes summary):

   /* ... some other python code here ... */

   cdezing.runDezing(&ctrl,batchsize, <unsigned char *>np.PyArray_DATA(inarray), <unsigned char *> np.PyArray_DATA(outarray))
   pass


def cleanup(): #,bytes summary):

   /* ... some other python code here ... */

   cdezing.runDezing(&ctrl,batchsize, NULL,NULL)
   cdezing.timestamp_close()

