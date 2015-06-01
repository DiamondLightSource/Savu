
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
   print "opening log file"
   cdezing.timestamp_open(logfile)
   cdezing.timestamp_init()
   print "coercing array"

   print "setting control flags"
   ctrl.versionflag=versionflag
   ctrl.outlier_mu=outlier_mu
   ctrl.cropwd=array_size[2]
   ctrl.nlines=array_size[1]
   ctrl.npad=npad
   batchsize=array_size[0]

   ctrl.f_call_num=0

   cdezing.timestamp( "calling c function setup" )
   #cdezing.runDezing(&ctrl,batchsize,<unsigned char *> inarray.data,<unsigned char *> outarray.data)
   cdezing.runDezing(&ctrl,batchsize, NULL, NULL)
   pass

def setup(np.ndarray[np.uint16_t,ndim=3,mode="c"] inarray,np.ndarray[np.uint16_t,ndim=3,mode="c"] outarray,outlier_mu,npad,logfile="dezing.log",versionflag=0): #,bytes summary):
   global ctrl
   global batchsize
   print "opening log file"
   cdezing.timestamp_open(logfile)
   cdezing.timestamp_init()
   print "coercing array"
   inbuf=<unsigned char *>np.PyArray_DATA(inarray)
   outbuf=<unsigned char *>np.PyArray_DATA(outarray)

   print "setting control flags"
   ctrl.versionflag=versionflag
   ctrl.outlier_mu=outlier_mu
   ctrl.cropwd=inarray.shape[2]
   ctrl.nlines=inarray.shape[1]
   ctrl.npad=npad
   batchsize=inarray.shape[0]

   ctrl.f_call_num=0

   cdezing.timestamp( "calling c function setup" )
   #cdezing.runDezing(&ctrl,batchsize,<unsigned char *> inarray.data,<unsigned char *> outarray.data)
   cdezing.runDezing(&ctrl,batchsize, inbuf, outbuf)
   pass

def run(np.ndarray[np.uint16_t,ndim=3,mode="c"] inarray,np.ndarray[np.uint16_t,ndim=3,mode="c"] outarray): #,bytes summary):
   global ctrl
   global batchsize

   print "coercing arrays "
   inbuf=<unsigned char *>np.PyArray_DATA(inarray)
   outbuf=<unsigned char *>np.PyArray_DATA(outarray)
   print  "in dezing.run: ctrl.cropwd is:" ,ctrl.cropwd, "batchsize is",batchsize

   batchsize=inarray.shape[0]

   cdezing.timestamp( "calling c function with run flag" )
   ctrl.f_call_num=1
   cdezing.runDezing(&ctrl,batchsize, <unsigned char *>np.PyArray_DATA(inarray), <unsigned char *> np.PyArray_DATA(outarray))
   pass



def cleanup(): #,bytes summary):
   global ctrl
   global batchsize
   print "coercing array"
   ctrl.f_call_num=2
   cdezing.timestamp( "calling c function with cleanup flag" )
   cdezing.runDezing(&ctrl,batchsize, NULL,NULL)
   cdezing.timestamp_close()







def test_run(width=2550,length=2500,batchsize=100):
   #cdef np.ndarray[np.uint16_t,ndim=3] inarray =np.ones((width,length,batchsize),dtype=np.uint16)
   #cdef np.ndarray[np.uint16_t,ndim=3] outarray =np.empty((width,length,batchsize),dtype=np.uint16)
   inarray =np.ones((width,length,batchsize),dtype=np.uint16)
   outarray =np.empty((width,length,batchsize),dtype=np.uint16)
   print "setting control flags"
   ctrl.versionflag=0
   ctrl.outlier_mu=1.5
   ctrl.cropwd=width
   ctrl.nlines=length
   print "setting a test value at element 0"
   inarray[0,0,0]=143
   print "creating random zingers"
   xarray=np.random.random_integers(0,width-1,1000)
   yarray=np.random.random_integers(0,length-1,1000)
   print "applying random zingers"
   for i in range(0,batchsize):
      for d in range(0,len(xarray)):
         xidx=xarray[d]
         yidx=yarray[d]
         inarray[xidx,yidx,i]=100*np.random.rand()
   
   print "getting slice of input"
   in50=inarray[:,:,50]
   print "setting inarray element 0 to %i"%inarray[0,0,0]
   cdezing.timestamp_open("test_run.log")


   inbuf=<unsigned char *>np.PyArray_DATA(inarray)
   outbuf=<unsigned char *>np.PyArray_DATA(outarray)

   ctrl.f_call_num=0
   print "calling c function setup"
   #cdezing.runDezing(&ctrl,batchsize,<unsigned char *> inarray.data,<unsigned char *> outarray.data)
   cdezing.runDezing(&ctrl,batchsize, inbuf, outbuf)

   ctrl.f_call_num=1
   print "calling c function"
   #cdezing.runDezing(&ctrl,batchsize,<unsigned char *> inarray.data,<unsigned char *> outarray.data)
   cdezing.runDezing(&ctrl,batchsize, <unsigned char *>np.PyArray_DATA(inarray), <unsigned char *> np.PyArray_DATA(outarray))

   ctrl.f_call_num=2
   print "calling c function cleanup"
   #cdezing.runDezing(&ctrl,batchsize,<unsigned char *> inarray.data,<unsigned char *> outarray.data)
   cdezing.runDezing(&ctrl,batchsize, <unsigned char *>np.PyArray_DATA(inarray), <unsigned char *> np.PyArray_DATA(outarray))


   cdezing.timestamp_close()
   print "finished c function"
   print "outarray element 0 is %i"%outarray[0,0,0]
   out50=outarray[:,:,50]
   return(in50,out50)




def test_data():
   cdef np.ndarray[np.uint16_t,ndim=3] inarray =np.ones((50,100,15),dtype=np.uint16)
   cdef np.ndarray[np.uint16_t,ndim=3] outarray =np.empty((50,100,15),dtype=np.uint16)
   ctrl.versionflag=2
   ctrl.outlier_mu=0.7
   ctrl.cropwd=50
   ctrl.nlines=100
   inarray[0,0,0]=143
   print "setting inarray element 0 to %i"%inarray[0,0,0]
   print "calling c function"
   cdezing.timestamp("calling c function")
   cdezing.runDezing(&ctrl,15,<unsigned char *> inarray.data,<unsigned char *> outarray.data)
   print "finished c function"
   print "outarray element 0 is %i"%outarray[0,0,0]



