import numpy as np
import inspect
import sys
nCols=1000
nAngles=601


    def geom_setup_2D(sino, angles, shape, cors):
        print "ENTERING geom_setup_2D with input angles %i sino shape %s output shape %s"%(len(angles),(sino.shape,),(shape,))
        p_low, p_high = array_pad(cors, nCols)
        sino = np.pad(sino, ((0, 0), (p_low, p_high)), mode='reflect')
        print "LEAVING geom_setup_2D with  angles %i sino shape %s output shape %s"%(len(angles),(sino.shape,),(shape,))
        return sino


    def array_pad( ctr, width):
        print "ENTERING array_pad"
        # pad the array so that the centre of rotation is in the middle
        pad = 50
        alen = ctr
        blen = width - ctr
        mid = width / 2.0

        p_low = pad if (ctr > mid) else (blen - alen) + pad
        p_high = (alen - blen) + pad if (ctr > mid) else pad
        return int(p_low), int(p_high)
