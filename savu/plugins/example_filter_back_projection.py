import logging
from savu.plugins.base_recon import BaseRecon
from savu.data.process_data import CitationInfomration
from savu.plugins.cpu_plugin import CpuPlugin

from scipy.optimize import curve_fit
import skimage.transform.iradon as FBP
import numpy as np


class ExampleFilterBackProjection(BaseRecon, CpuPlugin):
    """
    A Plugin to reconstruct an image by filter back projection using the inverse radon transform from scikit-image 
    :param output_size: Number of rows and columns in the reconstruction. Default: (None).
    :param filter: Filter used in frequency domain filtering. Ramp filter used by default. Filters available: ramp, shepp-logan, cosine, hamming, hann. Assign None to use no filter. Default: ('ramp').
    :param interpolation: interpolation method used in reconstruction. Methods available: 'linear', 'nearest', and 'cubic' ('cubic' is slow). Default: ('linear').
    :param circle: Assume the reconstructed image is zero outside the inscribed circle. Also changes the default output_size to match the behaviour of radon called with circle=True. Default: (False). 
    """


    def __init__(self):
        logging.debug("initialising Example Filter Back Projection")
        logging.debug("Calling super to make sure that all superclasses are " +
                      " initialised")
        super(ExampleFilterBackProjection,self).__init__("ExampleFilterBackProjection")


    def populate_default_parameters(self):
        logging.debug("Populating parameters from superclasses, must be done!")
        super(ExampleFilterBackProjection, self).populate_default_parameters()
        logging.debug("Populating Example Filter Back Projection default parameters")
        self.parameters['output_size'] = (None)
        self.parameters['filter'] = ('ramp')
        self.parameters['interpolation'] = ('linear')
        self.parameters['circle'] = (False)


    def filter_back_project(self, sinogram, centre_of_rotation, angles, shape, center):
        result = np.zeros(shape)
        sino = np.nan_to_num(sinogram)
        for i in range(sinogram.shape[0]):
            # recon using the iradon method
            theta = i * (np.pi/sinogram.shape[0])
        result = iradon(sino, theta=theta, output_size=self.parameters['output_size'], filter =  self.parameters['filter'],interpolation = self.parameters['linear'],circle = self.parameters[False])
        return result


    def get_citation_inforamtion(self):
        cite_info = CitationInfomration()
        cite_info.description = \
            ("The Tomographic reconstruction performed in this processing " +
            "chain is derived from this work.")
        cite_info.bibtex = \
            ("@book{avinash2001principles,\n" +
            " title={Principles of computerized tomographic imaging},\n" +
            " author={Kak, Avinash C. and Slaney, Malcolm},\n" +
            " year={2001},\n" +
            " publisher={Society for Industrial and Applied Mathematics}\n" +
            "}")
        cite_info.endnote = \
            ("%0 Book\n" +
            "%T Principles of computerized tomographic imaging\n" +
            "%A Kak, Avinash C.\n" +
            "%A Slaney, Malcolm\n" +
            "%@ 089871494X\n" +
            "%D 2001\n" +
            "%I Society for Industrial and Applied Mathematics")
        cite_info.doi = "http://dx.doi.org/10.1137/1.9780898719277"
        return cite_info




