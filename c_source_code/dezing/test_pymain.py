import dezing
import tifffile 
import numpy as np
import sys

#def get_image_array():
   #inim=np.expand_dims(tifffile.imread("index-1.tif"),2)
   #inimt=np.tile(inim,(1,1,100))
   #inim3=np.ascontiguousarray(inimt)
   #print "shape: ",inim3.shape

def get_image_array():
   #inim=np.expand_dims(tifffile.imread("index-1.tif"),0)
   inim=np.expand_dims(tifffile.imread("p_00600.tif"),0)
   inimt=np.tile(inim,(100,1,1))
   inim3=np.ascontiguousarray(inimt)
   print("shape: ",inim3.shape)
   outim=np.empty_like(inim3)
   return(inim3,outim)
#end of get_image_array

def read_image_set(pnum):
   instack=np.empty((12,2160,2560),dtype=np.uint16)
   startim=40383
   for i in range(0,8):
      imnum=startim+i
      imname="/dls/i12/data/2014/cm4963-3/tmp/extracted/%i/projections/p_%05d.tif"%(imnum,pnum)
      inim=tifffile.imread(imname)
      instack[i+2]=inim
      print(("image %i in stack position %i"%(imnum,i+2)))
   #pad the ends by two
   instack[0]=instack[8]
   instack[1]=instack[9]
   instack[10]=instack[2]
   instack[11]=instack[3]
   return(instack)

def dezing_brickframe(pnum):
   mu=1.5
   instack=read_image_set(pnum)
   outim=np.empty_like(instack)

   tifffile.imsave("/dls/science/users/kny48981/instack.tif",instack)

   dezing.setup(instack,outim,mu,2)
   dezing.run(instack,outim)
   dezing.cleanup(instack,outim)

   tifffile.imsave("/dls/science/users/kny48981/outstack.tif",outim)



def construct_test_array():
   width=100
   length=150
   batch=50
   inim3=np.empty((batch,length,width),dtype=np.uint16)

   for slice in range(0,batch):
      for row in range(0,length):
         for col in range(0,width):

            idx=slice*width*length+row*width+col
            inim3[slice,row,col]=idx


#   for k in range(0,5):
#      for j in range(0,5):
#         for i in range(0,5):
#            print "Python:",i,j,k,inim3[k,j,i]


   outim=np.empty_like(inim3)
   return(inim3,outim)
#end of construct_test_array

def main():
   #inim3,outim=get_image_array()
   inim3,outim=construct_test_array()

   tifffile.imsave("in.tif",inim3[:,:,0])
   tifffile.imsave("inflop.tif",inim3[0,:,:])

   print("in test_pymain: array shape is:",inim3.shape)
   mu=float(sys.argv[1])
   npad=2
   dezing.setup_size(inim3.shape,mu,npad)
   dezing.run(inim3,outim)
   dezing.cleanup()

   tifffile.imsave("out%f.tif" % mu ,outim[10,:,:])

   #ravout=np.ravel(outim,'K')
   #for k in range(0,5):
   #   for j in range(0,5):
   #      for i in range(0,5):
   #         idx=k*100*100+j*100+i
   #         print "Python Ravel K:",i,j,k,idx,ravout[idx]
   #
#dezing_brickframe(0)
main()
