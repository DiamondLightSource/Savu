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
.. module:: Remove stripe artefacts
   :platform: Unix
   :synopsis: A plugin working in sinogram space to remove large stripe artefacts
.. moduleauthor:: Nghia Vo <scientificsoftware@diamond.ac.uk>

"""

from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin
from savu.data.plugin_list import CitationInformation
import numpy as np
from scipy.ndimage import median_filter
from scipy.ndimage import binary_dilation
from scipy.ndimage import uniform_filter1d
from scipy import interpolate

@register_plugin
class RemoveAllRings(Plugin, CpuPlugin):
    """
---
      - name: RemoveAllRings
        category: Filter
        synopsis: Method to remove all types of stripe artifacts in a sinogram (<-> ring artefacts in a reconstructed image).
        parameters:
           - la_size:
                  visibility: param
                  type: int
                  description: Size of the median filter window to remove large stripes.
                  default: 71
           - sm_size:
                  visibility: param
                  type: int
                  description: Size of the median filter window to remove small-to-medium stripes.
                  default: 31
           - snr:
                  visibility: param
                  type: float
                  description: Ratio used to detect locations of stripes. Greater is less sensitive.
                  default: 3.0
    """
    """
    Method to remove all types of stripe artefacts in a sinogram \
    (<-> ring artefacts in a reconstructed image). 

    :param la_size: Size of the median filter window to remove large stripes\
    . Default: 71.
    :param sm_size: Size of the median filter window to remove small-to-medium\
    stripes. Default: 31.
    :param snr: Ratio used to detect locations of stripes. Greater is\
     less sensitive. Default: 3.0.
    """

    def __init__(self):
        super(RemoveAllRings, self).__init__(
                "RemoveAllRings")

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        out_dataset[0].create_dataset(in_dataset[0])
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('SINOGRAM', 'single')
        out_pData[0].plugin_data_setup('SINOGRAM', 'single')

    def remove_stripe_based_sorting(self, matindex, sinogram, size):
        """
        Algorithm 3 in the paper. Remove partial and full stripes\
        using the sorting technique.        
        """
        sinogram = np.transpose(sinogram)
        matcomb = np.asarray(np.dstack((matindex, sinogram)))
        matsort = np.asarray(
            [row[row[:, 1].argsort()] for row in matcomb])
        matsort[:, :, 1] = median_filter(matsort[:, :, 1],(size,1))
        matsortback = np.asarray(
            [row[row[:, 0].argsort()] for row in matsort])
        sino_corrected = matsortback[:, :, 1]
        return np.transpose(sino_corrected)

    def detect_stripe(self, listdata, snr):
        """
        Algorithm 4 in the paper. Used to locate stripe positions.
        ---------
        Parameters: - listdata: 1D normalized array.
                    - snr: ratio used to discriminate between useful
                        information and noise.
        ---------
        Return:     - 1D binary mask.
        """
        numdata = len(listdata)
        listsorted = np.sort(listdata)[::-1]
        xlist = np.arange(0, numdata, 1.0)
        ndrop = np.int16(0.25 * numdata)
        (_slope, _intercept) = np.polyfit(
            xlist[ndrop:-ndrop-1], listsorted[ndrop:-ndrop - 1], 1)
        numt1 = _intercept + _slope * xlist[-1]
        noiselevel = np.abs(numt1 - _intercept)
        val1 = np.abs(listsorted[0] - _intercept) / noiselevel
        val2 = np.abs(listsorted[-1] - numt1) / noiselevel
        listmask = np.zeros_like(listdata)
        if (val1 >= snr):
            upper_thresh = _intercept + noiselevel * snr * 0.5
            listmask[listdata > upper_thresh] = 1.0
        if (val2 >= snr):
            lower_thresh = numt1 - noiselevel * snr * 0.5
            listmask[listdata <= lower_thresh] = 1.0
        return listmask
    
    def remove_large_stripe(self, matindex, sinogram, snr, size):
        """
        Algorithm 5 in the paper. Use to remove large stripes
        ---------
        Parameters: - sinogram: 2D array.
                    - snr: ratio used to discriminate between useful
                        information and noise.
                    - size: window size of the median filter.
        ---------
        Return:     - stripe-removed sinogram.
        """
        badpixelratio = 0.05
        (nrow, ncol) = sinogram.shape
        ndrop = np.int16(badpixelratio * nrow)
        sinosorted = np.sort(sinogram, axis=0)
        sinosmoothed = median_filter(sinosorted, (1, size))
        list1 = np.mean(sinosorted[ndrop:nrow - ndrop], axis=0)
        list2 = np.mean(sinosmoothed[ndrop:nrow - ndrop], axis=0)
        listfact = list1 / list2
        listmask = self.detect_stripe(listfact, snr)
        listmask = binary_dilation(listmask, iterations=1).astype(listmask.dtype)
        matfact = np.tile(listfact,(nrow,1))
        sinogram = sinogram / matfact
        sinogram1 = np.transpose(sinogram)
        matcombine = np.asarray(np.dstack((matindex, sinogram1)))
        matsort = np.asarray(
            [row[row[:, 1].argsort()] for row in matcombine])
        matsort[:, :, 1] = np.transpose(sinosmoothed)
        matsortback = np.asarray(
            [row[row[:, 0].argsort()] for row in matsort])
        sino_corrected = np.transpose(matsortback[:, :, 1])
        listxmiss = np.where(listmask > 0.0)[0]
        sinogram[:, listxmiss] = sino_corrected[:, listxmiss]
        return sinogram

    def remove_unresponsive_and_fluctuating_stripe(self, sinogram, snr, size):
        """
        Algorithm 6 in the paper. Remove unresponsive or fluctuating stripes.
        ---------
        Parameters: - sinogram: 2D array.
                    - snr: ratio used to discriminate between useful
                        information and noise
                    - size: window size of the median filter.
        ---------
        Return:     - stripe-removed sinogram.
        """
        (nrow, _) = sinogram.shape
        sinosmoothed = np.apply_along_axis(uniform_filter1d, 0, sinogram, 10)
        listdiff = np.sum(np.abs(sinogram - sinosmoothed), axis=0)
        nmean = np.mean(listdiff)
        listdiffbck = median_filter(listdiff, size)
        listdiffbck[listdiffbck == 0.0] = nmean
        listfact = listdiff / listdiffbck
        listmask = self.detect_stripe(listfact, snr)
        listmask = binary_dilation(listmask, iterations=1).astype(listmask.dtype)
        listmask[0:2] = 0.0
        listmask[-2:] = 0.0
        listx = np.where(listmask < 1.0)[0]
        listy = np.arange(nrow)
        matz = sinogram[:, listx]
        finter = interpolate.interp2d(listx, listy, matz, kind='linear')
        listxmiss = np.where(listmask > 0.0)[0]
        if len(listxmiss) > 0:
            matzmiss = finter(listxmiss, listy)
            sinogram[:, listxmiss] = matzmiss
        return sinogram

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
        self.matindex = np.tile(listindex,(self.width1,1))        
        self.la_size = np.clip(np.int16(self.parameters['la_size']), 1, self.width1-1)
        self.sm_size = np.clip(np.int16(self.parameters['sm_size']), 1, self.width1-1)
        self.snr = np.clip(np.float32(self.parameters['snr']), 1.0, None)
        
    def process_frames(self, data):
        """
        Apply algorithm 6, 5, and 3 in the paper to removal all types of stripes.
        """
        sinogram = np.copy(data[0])        
        sinogram = self.remove_unresponsive_and_fluctuating_stripe(sinogram, self.snr, self.la_size)        
        sinogram = self.remove_large_stripe(self.matindex, sinogram, self.snr, self.la_size)
        sinogram = self.remove_stripe_based_sorting(self.matindex, sinogram, self.sm_size) 
        return sinogram

    def get_citation_information(self):
        cite_info = CitationInformation()
        cite_info.description = \
            ("The code of ring removal is the implementation of the work of \
            Nghia T. Vo et al. taken from algorithm 3,4,5,6 in this paper.")
        cite_info.bibtex = \
            ("@article{Vo:18,\n" +
             "title={Superior techniques for eliminating ring artifacts in\
              X-ray micro-tomography},\n" +
             "author={Nghia T. Vo, Robert C. Atwood,\
              and Michael Drakopoulos},\n" +
             "journal={Opt. Express},\n" +
             "volume={26},\n" +
             "number={22},\n" +
             "pages={28396--28412},\n" +
             "year={2018},\n" +
             "publisher={OSA}" +
             "}")
        cite_info.doi = "doi: DOI: 10.1364/OE.26.028396"
        return cite_info
