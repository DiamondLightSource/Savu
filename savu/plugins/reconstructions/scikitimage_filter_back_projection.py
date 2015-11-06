import logging
from savu.plugins.base_recon import BaseRecon
from savu.data.plugin_info import CitationInformation
from savu.plugins.driver.cpu_plugin import CpuPlugin

import skimage.transform as transform
import numpy as np
from scipy import ndimage

from savu.plugins.utils import register_plugin

@register_plugin
class ScikitimageFilterBackProjection(BaseRecon, CpuPlugin):
    """
    A Plugin to reconstruct an image by filter back projection
    using the inverse radon transform from scikit-image.

    :param output_size: Number of rows and columns in the
    reconstruction. Default: None.
    :param filter: Filter used in frequency domain filtering
    Ramp filter used by default. Filters available: ramp, shepp-logan,
    cosine, hamming, hann. Assign None to use no filter. Default: 'ramp'.
    :param interpolation: interpolation method used in reconstruction.
    Methods available: 'linear', 'nearest', and 'cubic' ('cubic' is slow).
    Default: 'linear'.
    :param circle: Assume the reconstructed image is zero outside the inscribed
    circle. Also changes the default output_size to match the behaviour of
    radon called with circle=True. Default: False.
    """

    def __init__(self):
        logging.debug("initialising Scikitimage Filter Back Projection")
        logging.debug("Calling super to make sure that all superclasses are " +
                      " initialised")
        super(ScikitimageFilterBackProjection,
              self).__init__("ScikitimageFilterBackProjection")

    def _shift(self, sinogram, centre_of_rotation):
        centre_of_rotation_shift = (sinogram.shape[0]/2) - centre_of_rotation
        result = ndimage.interpolation.shift(sinogram,
                                             (centre_of_rotation_shift[0],
                                              0))
        return result

    def reconstruct(self, sinogram, centre_of_rotations,
                    vol_shape, params):
        sinogram = np.swapaxes(sinogram, 0, 1)
        sinogram = self._shift(sinogram, centre_of_rotations)
        sino = np.nan_to_num(sinogram)
        theta = np.linspace(0, 180, sinogram.shape[1])
        result = \
            transform.iradon(sino, theta=theta,
                             output_size=(sinogram.shape[0]),
                             # self.parameters['output_size'],
                             filter='ramp',  # self.parameters['filter'],
                             interpolation='linear',
                             # self.parameters['linear'],
                             circle=False)  # self.parameters[False])
        return result

    def get_max_frames(self):
        """
        Should be overridden to define the max number of frames to process at
        a time

        :returns:  an integer of the number of frames
        """
        return 1

    def get_citation_information(self):
        cite_info = CitationInformation()
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
