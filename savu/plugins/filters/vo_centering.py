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
.. module:: vo_centering
   :platform: Unix
   :synopsis: A plugin to find the center of rotation per frame

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""
from savu.plugins.driver.cpu_plugin import CpuPlugin

import scipy.ndimage as ndi

import numpy as np
import scipy.fftpack as fft

from savu.plugins.utils import register_plugin
from savu.plugins.base_filter import BaseFilter
from savu.data.plugin_list import CitationInformation


@register_plugin
class VoCentering(BaseFilter, CpuPlugin):
    """
    A plugin to calculate the center of rotation using the Vo Method
    :param datasets_to_populate: A list of datasets which require this information. Default: [].    
    :param out_datasets: The default names. Default: ['cor_raw','cor_fit'].
    :param poly_degree: The polynomial degree of the fit (1 or 0 = gradient or no gradient). Default: 1.
    :param step: The step length over the rotation axis. Default: 1.
    """

    def __init__(self):
        super(VoCentering, self).__init__("VoCentering")

    def _create_mask(self, sino, pixel_step=0.5):
        fsino = np.vstack([sino, sino])
        mask = np.zeros(fsino.shape, dtype=np.bool)
        count = float(mask.shape[1]/2)
        for i in np.arange(mask.shape[0]/2, -1, -1):
            if count < 0:
                mask[i, :] = True
                mask[-i, :] = True
            else:
                mask[i, int(count):-(int(count+1))] = True
                mask[-i, int(count):-(int(count+1))] = True
            count -= pixel_step
        return mask

    def _scan(self, cor_positions, in_sino):
        mask = self._create_mask(in_sino)
        values = []
        sino = np.nan_to_num(in_sino)
        for i in cor_positions:
            ssino = ndi.interpolation.shift(sino, (0, i), mode='wrap')
            fsino = np.vstack([ssino, ssino[:, ::-1]])
            fftsino = fft.fftshift(fft.fft2(fsino))
            values.append(np.sum(np.abs(fftsino)*mask))
        vv = np.array(values)
        vv = abs(vv)
        return cor_positions[vv.argmin()]

    def filter_frames(self, data):
        print data[0].shape
        data = data[0][::self.parameters['step']]
        print data.shape
        width = data.shape[1]/4
        step = width/10.
        point = 0.0

        while step > 0.01:
            x = np.arange(point-width, point+width, step)
            point = self._scan(x, data)
            width = step
            step = width/10.

        cor_raw = (data.shape[1]/2.0) - point
        # temporary for testing
        cor_fit = (data.shape[1]/2.0) - point

        return [np.array([cor_raw]), np.array([cor_fit])]

    def post_process(self):
        # do some curve fitting here
        in_datasets, out_datasets = self.get_datasets()

        cor_raw = np.squeeze(out_datasets[0].data[...])
        cor_fit = np.squeeze(out_datasets[1].data[...])

        # now fit the result
        x = np.arange(cor_raw.shape[0])

        # first clean all points where the derivative is too high
        diff = np.abs(np.diff(cor_raw))

        tolerance = np.median(diff)
        diff = np.append(diff, tolerance)

        x_clean = x[diff <= tolerance * 2.0]
        cor_clean = cor_raw[diff <= tolerance * 2.0]

        # set up for the iterative clean on the fit
        cor_fit = cor_clean
        max_disp = 10
        p = None

        # keep fitting and removing points until the fit is within
        # the tolerances
        while max_disp > tolerance:
            mask = (np.abs(cor_fit-cor_clean)) < (max_disp / 2.)
            print x_clean, '\n', mask, '\n'
            x_clean = x_clean[mask]
            print x_clean[mask], '\n'
            print cor_clean, '\n'
            cor_clean = cor_clean[mask]
            print cor_clean, '\n'
            z = np.polyfit(x_clean, cor_clean, self.parameters['poly_degree'])
            p = np.poly1d(z)
            cor_fit = p(x_clean)
            max_disp = (np.abs(cor_fit-cor_clean)).max()

        # build a full array for the output fit
        cor_fit = p(x)

        print cor_fit
        out_datasets[1].data[:] = cor_fit[:, np.newaxis]
        # add to metadata
        self.populate_meta_data('cor_raw', cor_raw)
        self.populate_meta_data('centre_of_rotation', cor_fit)

    def populate_meta_data(self, key, value):
        datasets = self.parameters['datasets_to_populate']
        in_meta_data = self.get_in_meta_data()[0]
        in_meta_data.set_meta_data(key, value)
        for name in datasets:
            self.exp.index['in_data'][name].meta_data.set_meta_data(key, value)

    def setup(self):

        self.exp.log(self.name + " Start")

        # set up the output dataset that is created by the plugin
        in_dataset, out_dataset = self.get_datasets()
        # copy all required information from in_dataset[0]
        fullData = in_dataset[0]

        out_dataset[0].create_dataset(shape=(fullData.get_shape()[1], 1),
                                      axis_labels=['x.pixels', 'y.pixels'],
                                      remove=True)
        out_dataset[0].add_pattern("METADATA", core_dir=(1,), slice_dir=(0,))

        out_dataset[1].create_dataset(shape=(fullData.get_shape()[1], 1),
                                      axis_labels=['x.pixels', 'y.pixels'],
                                      remove=True)
        out_dataset[1].add_pattern("METADATA", core_dir=(1,), slice_dir=(0,))

        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('SINOGRAM', self.get_max_frames())
        out_pData[0].plugin_data_setup('METADATA', self.get_max_frames())
        out_pData[1].plugin_data_setup('METADATA', self.get_max_frames())

        self.exp.log(self.name + " End")

    def nOutput_datasets(self):
        return 2

    def get_max_frames(self):
        """
        This filter processes 1 frame at a time

         :returns:  1
        """
        return 1

    def get_citation_information(self):
        cite_info = CitationInformation()
        cite_info.description = \
            ("The center of rotation for this reconstruction was calculated " +
             "automatically using the method described in this work")
        cite_info.bibtex = \
            ("@article{vo2014reliable,\n" +
             "title={Reliable method for calculating the center of rotation " +
             "in parallel-beam tomography},\n" +
             "author={Vo, Nghia T and Drakopoulos, Michael and Atwood, " +
             "Robert C and Reinhard, Christina},\n" +
             "journal={Optics Express},\n" +
             "volume={22},\n" +
             "number={16},\n" +
             "pages={19078--19086},\n" +
             "year={2014},\n" +
             "publisher={Optical Society of America}\n" +
             "}")
        cite_info.endnote = \
            ("%0 Journal Article\n" +
             "%T Reliable method for calculating the center of rotation in " +
             "parallel-beam tomography\n" +
             "%A Vo, Nghia T\n" +
             "%A Drakopoulos, Michael\n" +
             "%A Atwood, Robert C\n" +
             "%A Reinhard, Christina\n" +
             "%J Optics Express\n" +
             "%V 22\n" +
             "%N 16\n" +
             "%P 19078-19086\n" +
             "%@ 1094-4087\n" +
             "%D 2014\n" +
             "%I Optical Society of America")
        cite_info.doi = "http://dx.doi.org/10.1364/OE.22.019078"
        return cite_info
