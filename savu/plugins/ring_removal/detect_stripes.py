# Copyright 2022 Diamond Light Source Ltd.
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
.. module:: detect_stripes
   :platform: Unix
   :synopsis: Method working in the sinogram space to detect stripe artifacts.
.. moduleauthor:: Nghia Vo, Yousef Moazzam <scientificsoftware@diamond.ac.uk>

"""

from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin

import numpy as np
from scipy.ndimage import median_filter
from scipy.ndimage import binary_dilation
from scipy.ndimage import uniform_filter1d


@register_plugin
class DetectStripes(Plugin, CpuPlugin):
    """
    A plugin to detect stripes in a sinogram and return a 2D binary mask that
    specifies the position of the stripes.
    """
    def __init__(self):
        super(DetectStripes, self).__init__('DetectStripes')

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('SINOGRAM',self.get_max_frames())
        out_dataset[0].create_dataset(in_dataset[0])
        out_pData[0].plugin_data_setup('SINOGRAM', self.get_max_frames())

    def pre_process(self):
        in_pData = self.get_plugin_in_datasets()
        width_dim = \
            in_pData[0].get_data_dimension_by_axis_label('detector_x')
        height_dim = \
            in_pData[0].get_data_dimension_by_axis_label('rotation_angle')
        sino_shape = list(in_pData[0].get_shape())
        self.width1 = sino_shape[width_dim]
        self.height1 = sino_shape[height_dim]
        listindex = np.arange(0.0, self.height1, 1.0)
        self.matindex = np.tile(listindex, (self.width1, 1))
        self.size = np.clip(np.int16(self.parameters['size']), 1,
                            self.width1 - 1)
        self.snr = np.clip(np.float32(self.parameters['snr']), 1.0, None)

    def process_frames(self, data):
        sinogram = np.copy(data[0])
        # begin pre-processing sinogram as preparation for the stripe detection
        # algorithm
        #
        # NOTE: the pre-processing steps here are specifically for unresponsive
        # and fluctuating stripe artifacts
        sinosmoothed = np.apply_along_axis(uniform_filter1d, 0, sinogram, 10)
        listdiff = np.sum(np.abs(sinogram - sinosmoothed), axis=0)
        nmean = np.mean(listdiff)
        listdiffbck = median_filter(listdiff, self.size)
        listdiffbck[listdiffbck == 0.0] = nmean
        listfact = listdiff / listdiffbck
        # finish pre-processing sinogram

        listmask = self.detect_stripe(listfact, self.snr)
        if self.parameters['binary_dilation']:
            listmask = binary_dilation(listmask, iterations=1).astype(
                listmask.dtype)
            listmask[0:2] = 0.0
            listmask[-2:] = 0.0

        stripe_locations = np.squeeze(np.argwhere(listmask==1))
        mask_2d = np.zeros(sinogram.shape)
        # separate detected columns in `listmask` into groups that correspond to
        # the stripes that have been detected
        stripes = []
        for i in range(len(stripe_locations)):
            if i == 0:
                stripe = [stripe_locations[i]]
                continue
            elif i == len(stripe_locations) - 1:
                stripe.append(stripe_locations[i])
                stripes.append(stripe)
                continue
            if stripe_locations[i] != stripe_locations[i-1] + 1:
                stripe.append(stripe_locations[i-1])
                stripes.append(stripe)
                stripe = [stripe_locations[i]]

        # apply 1's in 2D mask at stripe locations
        for stripe in stripes:
            mask_2d[:, stripe[0]:stripe[1]] = 1

        return mask_2d

    def detect_stripe(self, listdata, snr):
        """Algorithm 4 in the paper. To locate stripe positions.

        Parameters
        ----------
        listdata : 1D normalized array.
        snr : Ratio (>1.0) used to detect stripe locations.

        Returns
        -------
        listmask : 1D binary mask.
        """
        numdata = len(listdata)
        listsorted = np.sort(listdata)[::-1]
        xlist = np.arange(0, numdata, 1.0)
        ndrop = np.int16(0.25 * numdata)
        (_slope, _intercept) = np.polyfit(
            xlist[ndrop:-ndrop - 1], listsorted[ndrop:-ndrop - 1], 1)
        numt1 = _intercept + _slope * xlist[-1]
        noiselevel = np.abs(numt1 - _intercept)
        if noiselevel == 0.0:
            raise ValueError(
                "The method doesn't work on noise-free data. If you " \
                "apply the method on simulated data, please add" \
                " noise!")
        val1 = np.abs(listsorted[0] - _intercept) / noiselevel
        val2 = np.abs(listsorted[-1] - numt1) / noiselevel
        listmask = np.zeros_like(listdata)
        if val1 >= snr:
            upper_thresh = _intercept + noiselevel * snr * 0.5
            listmask[listdata > upper_thresh] = 1.0
        if val2 >= snr:
            lower_thresh = numt1 - noiselevel * snr * 0.5
            listmask[listdata <= lower_thresh] = 1.0
        return listmask

    def get_max_frames(self):
        return 'single'

    def nInput_datasets(self):
        return 1

    def nOutput_datasets(self):
        return 1
