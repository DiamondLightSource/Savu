import tifffile 
import numpy as np
import sys
import os
import unwarp
nbatch=100

def get_image_array():
   global nbatch
   #inim=np.expand_dims(tifffile.imread("index-1.tif"),0)
   #inim=np.expand_dims(tifffile.imread("p_00600.tif"),0)
   inim=np.expand_dims(tifffile.imread("i32.tif"),0)
   inimt=np.tile(inim,(nbatch,1,1))
   inim3=np.ascontiguousarray(inimt.astype(np.float32))
   print("shape: ",inim3.shape)
   outim=np.empty_like(inim3)
   return(inim3,outim)
#end of get_image_array

(inarray,outarray)=get_image_array()

#set the coefficients -- this coudl be rolled into setup with additional args?
unwarp.setcoeff(1,-1e-3,-6e-7,5e-10,-4e-13)
unwarp.setctr(1000,1000)

#call setup routine 
unwarp.setup(inarray,outarray)

unwarp.run(inarray,outarray)
#multiple calls so long as centre and parameters are fixed 
#could be different data solong as it is same type/size/etc
unwarp.run(inarray,outarray)


unwarp.cleanup()

print("Writing the files to /dls/i12/data/2015/cm12163-5/tmp/unwarptest/cython_out")
try:
   os.makedirs("/dls/i12/data/2015/cm12163-5/tmp/unwarptest/cython_out")
   print ("Creating Folder")
except:
   print ("Folder already exists")


for i in range(0,1):
   tifffile.imsave( "/dls/i12/data/2015/cm12163-5/tmp/unwarptest/cython_out/p_%05d.tif"%i,outarray[i,:,:])

