import logging

from savu.plugins.filter import Filter
from savu.plugins.cpu_plugin import CpuPlugin

from savu.data import structures
import numpy as np
import math


class PaganinFilter(Filter, CpuPlugin):
    """
    A plugin to apply Paganin filter (contrast enhancement) on projections
    
    :param Energy: Given X-ray energy in keV. Default: 20.
    :param Distance: Distance from sample to detection - Unit is metre. Default: 1.0.
    :param Resolution: Pixel size - Unit is micron. Default: 21.46.
    :param Ratio: ratio of delta/beta. Default: 10.0.
    :param Padtopbottom: Pad to the top and bottom of projection. Default: 10.
    :param Padleftright: Pad to the left and right of projection. Default: 10.
    :param Padmethod: Method of padding. Default: 'edge'.
    """
    
    def __init__(self):
        logging.debug("initialising Paganin Filter")
        logging.debug("Calling super to make sure that all superclases are " +
                      " initialised")
        super(PaganinFilter,
              self).__init__("PaganinFilter")
        self.filtercomplex = None

    def _setup_paganin(self, width, height):
        if self.filtercomplex is None:
            micron = 10**(-6)
            keV = 1000.0
            distance = self.parameters['Distance']
            energy = self.parameters['Energy']*keV
            resolution = self.parameters['Resolution']*micron
            wavelength = (1240.0/energy)*10.0**(-9)
            ratio = self.parameters['Ratio']
            padtopbottom = self.parameters['Padtopbottom']
            padleftright = self.parameters['Padleftright']
            height1 = height + 2*padtopbottom
            width1 = width + 2*padleftright
            centery = np.ceil(height1/2.0)-1.0
            centerx = np.ceil(width1/2.0)-1.0
            # Define the paganin filter
            dpx = 1.0/(width1*resolution)
            dpy = 1.0/(height1*resolution)
            pxlist = (np.arange(width1)-centerx)*dpx
            pylist = (np.arange(height1)-centery)*dpy
            pxx = np.zeros((height1, width1), dtype=np.float32)
            pxx[:, 0:width1] = pxlist
            pyy = np.zeros((height1, width1), dtype=np.float32)
            pyy[0:height1, :] = np.reshape(pylist, (height1, 1))
            pd = (pxx*pxx+pyy*pyy)*wavelength*distance*math.pi
            filter1 = 1.0+ratio*pd
            self.filtercomplex = filter1+filter1*1j

    def _paganin(self, data, axes):
        pci1 = np.fft.fft2(np.float32(data))
        pci2 = np.fft.fftshift(pci1)/self.filtercomplex
        fpci = np.abs(np.fft.ifft2(pci2))
        result = -0.5*self.parameters['Ratio']*np.log(fpci+1.0)
        return result

    def filter_frame(self, data):
        logging.debug("Getting the filter frame of Paganin Filter")
        (depth, height, width) = data.shape
        self._setup_paganin(width, height)
        data = np.nan_to_num(data)  # Noted performance
        data[data == 0] = 1.0
        padtopbottom = self.parameters['Padtopbottom']
        padleftright = self.parameters['Padleftright']
        padmethod = self.parameters['Padmethod']
        #data1 = np.lib.pad(data, ((padtopbottom, padtopbottom), (padleftright, padleftright)), padmethod)
        data = np.lib.pad(data, ((0, 0), (padtopbottom, padtopbottom), (padleftright, padleftright)), padmethod)
        result = np.apply_over_axes(self._paganin, data, 0)
        return result[result.shape[0]/2, padtopbottom:-padtopbottom, padleftright: -padleftright]

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
