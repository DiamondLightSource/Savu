import logging

from savu.plugins.filter import Filter
from savu.plugins.cpu_plugin import CpuPlugin

from savu.data import structures
import numpy as np
import math


class PaganinFilter(Filter, CpuPlugin):
    def __init__(self):
        logging.debug("initialising Paganin Filter")
        logging.debug("Calling super to make sure that all superclases are " +
                      " initialised")
        super(PaganinFilter,
              self).__init__("PaganinFilter")
        self.filtercomplex = None

    def populate_default_parameters(self):
        """
        All plugins have the populate_default_patamters method, in this you
        need to add to the self.parameters dictionary any parameters which you
        wish the end user to ultimately be able to change, in this case we will
        let them define the size of the kernel we will use for out 3D median
        filter. We initialise this with a good default value, in this case a
        tuple of (3, 3, 3) If you wish to change the direction that the filter
        travels across the data, then you need to adjust the
        self.parameters['slice_direction'] = 0
        entry to be a different value,
        i.e. 1 for sinogram direction.
        """
        logging.debug("Populating parameters from superclasses, must be done!")
        super(PaganinFilter, self).populate_default_parameters()
        logging.debug("Populating Paganin Filter default parameters")
        # List of parameter  (Energy,distance,resolution,ratio,padding)
        self.parameters['Energy'] = 20.0  # keV
        self.parameters['Distance'] = 1.0  # m
        self.parameters['Resolution'] = 21.46  # micron
        self.parameters['Ratio'] = 10.0  # ratio of delta/beta

    def _setup_paganin(self, width, height):
        if self.filtercomplex is None:
            centery = np.ceil(height/2.0)-1.0
            centerx = np.ceil(width/2.0)-1.0
            micron = 10**(-6)
            keV = 1000.0
            distance = self.parameters['Distance']
            energy = self.parameters['Energy']*keV
            resolution = self.parameters['Resolution']*micron
            wavelength = (1240.0/energy)*np.power(10.0, -9)
            ratio = self.parameters['Ratio']
            # Define the paganin filter
            dpx = 1.0/(width*resolution)
            dpy = 1.0/(height*resolution)
            pxlist = (np.arange(width)-centerx)*dpx
            pylist = (np.arange(height)-centery)*dpy
            pxx = np.zeros((height, width), dtype=np.float32)
            pxx[:, 0:width] = pxlist
            pyy = np.zeros((height, width), dtype=np.float32)
            pyy[0:height, :] = np.reshape(pylist, (height, 1))
            pd = (pxx*pxx+pyy*pyy)*wavelength*distance*math.pi
            filter1 = 1.0+ratio*pd
            self.filtercomplex = filter1+filter1*1j

    def _paganin(self, data):
        pci1 = np.fft.fft2(np.float32(data))
        pci2 = np.fft.fftshift(pci1)/self.filtercomplex
        fpci = np.abs(np.fft.ifft2(pci2))
        result = -0.5*self.parameters['Ratio']*np.log(fpci+0.1)
        return result

    def filter_frame(self, data):
        logging.debug("Getting the filter frame of Paganin Filter")
        (depth, height, width) = data.shape
        result = np.zeros((depth, height, width), dtype=np.float32)
        self._setup_paganin(width, height)
        for i in range(depth):
            sanitised = np.nan_to_num(data[i])
            sanitised[sanitised == 0] = 1.0
            result[i] = self._paganin(sanitised)
        return result[result.shape[0]/2, :, :]

    def required_data_type(self):
        """
        The input for this plugin is RawTimeseriesData
        :returns: Data
        """
        return structures.ProjectionData

    def output_data_type(self):
        """
        The output of this plugin is ProjectionData
        :returns: Data
        """
        return structures.ProjectionData
