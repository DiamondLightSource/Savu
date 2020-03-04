# Copyright 2014 Diamond Light Source Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
.. module:: scikitimage_sart
   :platform: Unix
   :synopsis: Wrapper for scikitimage SART function

"""

import logging
from savu.plugins.reconstructions.base_recon import BaseRecon
from savu.data.plugin_list import CitationInformation
from savu.plugins.driver.cpu_plugin import CpuPlugin

import skimage.transform as transform
import numpy as np
from scipy import ndimage

from savu.plugins.utils import register_plugin


@register_plugin
class ScikitimageSart(BaseRecon, CpuPlugin):
    """
    A Plugin to reconstruct an image by filter back projection using the \
    inverse radon transform from scikit-image.

    :param iterations: Number of iterations in the reconstruction. Default: 1.
    :param output_size: Number of rows and columns in the \
        reconstruction. Default: None.
    :param filter: Filter used in frequency domain \
        filtering. Ramp filter used by default. Filters available: ramp, \
        shepp-logan, cosine, hamming, hann.  Assign None to use no \
        filter. Default: 'ramp'.
    :param interpolation: interpolation method used in reconstruction. \
        Methods available: 'linear', 'nearest', and 'cubic' \
        ('cubic' is slow). Default: 'linear'.
    :param circle: Assume the reconstructed image is zero outside the \
        inscribed circle. Also changes the default output_size to match the \
        behaviour of radon called with circle=True. Default: False.
    :param image: 2D array, dtype=float, optional.  Image containing an \
        initial reconstruction estimate. Shape of this array should be \
        (radon_image.shape[0], radon_image.shape[0]). The default is a filter \
        backprojection using scikit.image.iradon as "result". Default: None.

    :param projection_shifts : 1D array, dtype=float. Shift the projections \
        contained in radon_image (the sinogram) by this many pixels before \
        reconstructing the image. The i'th value defines the shift of the \
        i'th column of radon_image.  Default: None.
    :param clip : length-2 sequence of floats. Force all values in the \
        reconstructed tomogram to lie in the range \
        [clip[0], clip[1]]. Default: None.
    :param relaxation : float. Relaxation parameter for the update step. A \
        higher value can improve the convergence rate, but one runs the risk \
        of instabilities. Values close to or higher than 1 are not \
        recommended. Default: None.

    :~param outer_pad: Not required. Default: False.
    :~param centre_pad: Not required. Default: False.

    """

    def __init__(self):
        logging.debug("initialising Scikitimage SART")
        logging.debug("Calling super to make sure that all superclasses are " +
                      " initialised")
        super(ScikitimageSart, self).__init__("ScikitimageSart")

    def _shift(self, sinogram, centre_of_rotation):
        centre_of_rotation_shift = (sinogram.shape[0]/2) - \
            float(centre_of_rotation)
        return ndimage.interpolation.shift(sinogram, centre_of_rotation_shift)

    def process_frames(self, data):
        sino = data[0]
        centre_of_rotations, angles, vol_shape, init = self.get_frame_params()
        in_pData = self.get_plugin_in_datasets()[0]
        sinogram = np.swapaxes(sino, 0, 1)
        sinogram = self._shift(sinogram, centre_of_rotations)
        sino = sinogram.astype(np.float64)
        theta = np.linspace(0, 180, sinogram.shape[1])
        result = \
            transform.iradon(sino, theta=theta,
                             output_size=(in_pData.get_shape()[1]),
                             # self.parameters['output_size'],
                             filter='ramp',  # self.parameters['filter'],
                             interpolation='linear',
                             # self.parameters['linear'],
                             circle=False)  # self.parameters[False])

        for i in range(self.parameters["iterations"]):
            print("Iteration %i" % i)
            result = transform.iradon_sart(sino, theta=theta, image=result,
                                           # self.parameters['result'],
                                           projection_shifts=None,
                                           # self.parameters['None'],
                                           clip=None,
                                           # self.parameters[None],
                                           relaxation=0.15
                                           # self.parameters[0.15])
                                           )
        return result

    def get_max_frames(self):
        return 'single'

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
        cite_info.doi = "https://doi.org/10.1137/1.9780898719277"
        return cite_info
