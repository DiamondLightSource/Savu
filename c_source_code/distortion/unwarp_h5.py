import  unwarpint16 as unwarp
import tifffile 
import numpy as np
import sys
import h5py

def read_image_set(data,pstart=0,pstop=50,npad=2):
   padstart=True
   padend=True
   print(data.shape)
   intype=data.dtype
   sidx=pstart
   eidx=pstop

   #check for the chunk being at the very beginnning or end of the whole stack

   if (pstart >=npad):
      sidx=pstart - npad
      padstart=False
   if (pstop < data.shape[0]-npad):
      eidx=pstop+npad
      padend=False

   #pad the very start
   if padstart:
      spadarray=np.empty((npad,data.shape[1],data.shape[2]),dtype=intype)
      for i in range(0,npad):
         print((pstart+npad-i),"->",i)
         np.copyto(spadarray[i,:,:],data[pstart+npad-i])

   #pad the very end
   if padend:
      epadarray=np.empty((npad,data.shape[1],data.shape[2]),dtype=intype)
      for i in range(0,npad):
         print((pstop-i),"->",i)
         np.copyto(epadarray[i,:,:],data[pstop-i])

   dset=data[sidx:eidx,:,:]
   print(dset.shape)

   #concatenate the very beginning and/or very end padding
   outarray=dset
   if (padstart or padend):
      if padstart:
         print ("Padding start")
         outarray=np.vstack((spadarray,outarray))

      if padend:
         print ("Padding end")
         outarray=np.vstack((outarray,epadarray))

   print(outarray.shape)
   return(np.ascontiguousarray(outarray))


def main():
   slabsize=4
   h5chunksize=4
   if len(sys.argv) <= 4 :
      print("   ")
      print(sys.argv[0])
      print("USAGE: %s  h5file chunkstart chunkstop h5outputfile "%sys.argv[0])
      print("chunk must not be smaller than  %i  projections"%h5chunksize)
      sys.exit(0)
   npad=0 # should be 0 
   input=sys.argv[1] #first argument, filename of h5 file , should contain /entry/instrument/detector/data and be uint16
   chunkstart=int(sys.argv[2]) # the start of the chunk (without padding)
   chunkstop=int(sys.argv[3]) #the end of the chunk (without padding)
   outname=sys.argv[4] #the output file


   infp=h5py.File(input)
   #data=infp['/entry/instrument/detector/data']
   data=infp['/entry1/tomo_entry/data/data']

   chunksize=chunkstop-chunkstart
   nslabs = int(chunksize/slabsize)

   h5outp=h5py.File(outname,"w")
   outgrp=h5outp.create_group("/entry1/tomo_entry/data")
   outdset=outgrp.create_dataset("data",(chunksize,data.shape[1],data.shape[2]),chunks=(h5chunksize,h5chunksize,data.shape[2]))

   print("nslabs=%i"%nslabs)
   lastslabsize=chunksize-(nslabs*slabsize)
   print("lastslabsize=%i"%lastslabsize)
   #set the coefficients -- this coudl be rolled into setup with additional args?
   #unwarp.setcoeff(1,-1e-3,-6e-7,5e-10,-4e-13) #fisheye test
   #unwarp.setctr(500,1000) #fisheye test
   #unwarp.setcoeff(1,0,0,0,0)
   unwarp.setcoeff(1.00015076,1.9289e-6,-2.4325e-8,1.00439e-11,-3.99352e-15)
   unwarp.setctr(1283.25,data.shape[1]-1164.765)

   outim=np.empty((slabsize+2*npad,data.shape[1],data.shape[2]),dtype=np.uint16) #create an empty array , the program will fill it up

   firststop=chunkstart+slabsize
   instack=read_image_set(data,chunkstart,firststop,npad) #npad is optional, default is 2
   unwarp.setup(instack,outim) #call the program to initialize the arrays

   for slab in range(nslabs):
      print("SLAB %i of %i"%(slab,nslabs))
      slabstart=slab*slabsize
      slabstop=slabstart+slabsize
      instack=read_image_set(data,slabstart,slabstop,npad) #npad is optional, default is 2
      unwarp.run(instack,outim)           #could call again with a different instack before cleaning up, if it is teh same size



      output=outim[npad:outim.shape[0]-npad] #discard the padded area
      for slice in range(slabstart,slabstop):
         tifffile.imsave("/dls/i12/data/2015/cm12163-5/tmp/out_%05d.tif"%slice,outim[slice-slabstart]) #example, save the chunk

      outdset[slabstart-chunkstart:slabstop-chunkstart,:,:]=output


   unwarp.cleanup()       #call the program to de-allocate the arrays

   #now the last slab
   if lastslabsize > 0:

      outim=np.empty((lastslabsize+2*npad,data.shape[1],data.shape[2]),dtype=np.uint16) #create an empty array , the program will fill it up
      print("last outim shape",outim.shape)

      laststart=chunkstart+nslabs*slabsize
      slabstart=laststart
      slabstop=chunkstop

      instack=read_image_set(data,slabstart,slabstop,npad) #npad is optional, default is 2

      unwarp.setup(instack,outim) #call the program to initialize the arrays
      unwarp.run(instack,outim)           #could call again with a different instack before cleaning up, if it is teh same size

      output=outim[npad:outim.shape[0]-npad] #discard the padded area
      for slice in range(slabstart,slabstop):
         tifffile.imsave("/dls/i12/data/2015/cm12163-5/tmp/out_%05d.tif"%slice,outim[slice-slabstart]) #example, save the chunk

      print("slabstart=",slabstart, "slabstop=",slabstop)
      print("output shape",output.shape)
      print("outdset shape",outdset.shape)
      print("chunksize",chunksize)
      outdset[slabstart-chunkstart:slabstop-chunkstart,:,:]=output

      unwarp.cleanup()       #call the program to de-allocate the arrays

   rot=infp[ "/entry1/tomo_entry/data/rotation_angle"]
   key=infp["/entry1/tomo_entry/instrument/detector/image_key"] 
   
   outrot=h5outp.create_dataset("/entry1/tomo_entry/data/rotation_angle",data=rot[chunkstart:chunkstop])
   outkey=h5outp.create_dataset("/entry1/tomo_entry/instrument/detector/image_key",data=key[chunkstart:chunkstop]) 

   h5outp.close()






if __name__ == "__main__":
   print("Running main procedure")
   main()
