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
.. module:: remove_large_rings
   :platform: Unix
   :synopsis: Method working in the sinogram space to remove large ring
    artifacts.
.. moduleauthor:: Nghia Vo <scientificsoftware@diamond.ac.uk>

"""

from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin
import numpy as np
from scipy.ndimage import median_filter
from scipy.ndimage import binary_dilation


@register_plugin
class RemoveLargeRings(Plugin, CpuPlugin):

    def __init__(self):
        super(RemoveLargeRings, self).__init__(
            "RemoveLargeRings")

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        out_dataset[0].create_dataset(in_dataset[0])
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('SINOGRAM', 'single')
        out_pData[0].plugin_data_setup('SINOGRAM', 'single')

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
        badpixelratio = 0.05  # To avoid false detection
        ndrop = np.int16(badpixelratio * self.height1)
        sinosorted = np.sort(sinogram, axis=0)
        sinosmoothed = median_filter(sinosorted, (1, self.size))
        list1 = np.mean(sinosorted[ndrop:self.height1 - ndrop], axis=0)
        list2 = np.mean(sinosmoothed[ndrop:self.height1 - ndrop], axis=0)
        listfact = np.divide(list1, list2,
                             out=np.ones_like(list1), where=list2 != 0)
        listmask = self.detect_stripe(listfact, self.snr)
        listmask = binary_dilation(listmask, iterations=1).astype(
            listmask.dtype)
        matfact = np.tile(listfact, (self.height1, 1))
        sinogram = sinogram / matfact
        sinogram1 = np.transpose(sinogram)
        matcombine = np.asarray(np.dstack((self.matindex, sinogram1)))
        matsort = np.asarray(
            [row[row[:, 1].argsort()] for row in matcombine])
        matsort[:, :, 1] = np.transpose(sinosmoothed)
        matsortback = np.asarray(
            [row[row[:, 0].argsort()] for row in matsort])
        sino_corrected = np.transpose(matsortback[:, :, 1])
        listxmiss = np.where(listmask > 0.0)[0]
        sinogram[:, listxmiss] = sino_corrected[:, listxmiss]
        return sinogram
