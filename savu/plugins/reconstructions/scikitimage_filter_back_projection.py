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
.. module:: scikitimage_filter_back_projection
   :platform: Unix
   :synopsis: Wrapper for scikitimage FBP function

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
class ScikitimageFilterBackProjection(BaseRecon, CpuPlugin):
    """
    A Plugin to reconstruct an image by filter back projection
    using the inverse radon transform from scikit-image.

    :param output_size: Number of rows and columns in the \
        reconstruction. Default: 'auto'.
    :param filter: Filter used in frequency domain filtering Ramp filter used \
        by default. Filters available: ramp, shepp-logan, cosine, hamming, \
        hann. Assign None to use no filter. Default: 'ramp'.
    :param interpolation: interpolation method used in reconstruction. \
        Methods available: 'linear', 'nearest', and 'cubic' \
        ('cubic' is slow). Default: 'linear'.
    :param circle: Assume the reconstructed image is zero outside the \
        inscribed circle. Also changes the default output_size to match the \
        behaviour of radon called with circle=True. Default: False.

    :~param outer_pad: Not required. Default: False.
    :~param centre_pad: Not required. Default: False.
    """

    def __init__(self):
        logging.debug("initialising Scikitimage Filter Back Projection")
        logging.debug("Calling super to make sure that all superclasses are " +
                      " initialised")
        super(ScikitimageFilterBackProjection,
              self).__init__("ScikitimageFilterBackProjection")

    def _shift(self, sinogram, centre_of_rotation):
        centre_of_rotation_shift = (sinogram.shape[0] // 2) - centre_of_rotation
        result = ndimage.interpolation.shift(sinogram,
                                             (centre_of_rotation_shift, 0))
        return result

    def process_frames(self, data):
        sino = data[0]
        centre_of_rotations, angles, vol_shape, init = self.get_frame_params()
        in_pData = self.get_plugin_in_datasets()[0]
        in_meta_data = self.get_in_meta_data()[0]
        sinogram = np.swapaxes(sino, 0, 1)
        sinogram = self._shift(sinogram, centre_of_rotations)
        theta = in_meta_data.get('rotation_angle')

        dim_detX = in_pData.get_data_dimension_by_axis_label('detector_x')
        size = self.parameters['output_size']
        size = in_pData.get_shape()[dim_detX] if size == 'auto' or \
            size is None else size

        result = \
            transform.iradon(sinogram, theta=theta,
                             output_size=(size),
                             filter=self.parameters['filter'],
                             interpolation=self.parameters['interpolation'],
                             circle=self.parameters['circle'])
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
