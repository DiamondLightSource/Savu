
#$Id: cunwarp.pxd 444 2015-12-15 11:56:04Z kny48981 $
cdef extern from "./options.h":
   cdef cppclass Options:
   #ctypedef struct Options:
      unsigned char versionflag
      unsigned char pixelflag
      unsigned char f_call_num
      unsigned int ht;
      unsigned int wd;
      unsigned int firstslice;
      unsigned int lastslice;
      float xcentre;
      float ycentre;
      float acoeff
      float bcoeff
      float ccoeff
      float dcoeff
      float ecoeff

cdef extern from "./timestamp.h":
   void timestamp_open(const char * const logname)
   void timestamp_close()
   void timestamp_init()
   void timestamp(const char * const stampmsg,const int level)

cdef extern from "./unwarp_functions.h":
   void runUnwarp(Options * ctrlp, unsigned int thisbatch,unsigned char * inbuf, unsigned char * outbuf )

