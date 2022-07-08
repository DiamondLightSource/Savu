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
.. moduleauthor:: Mark Basham, Nghia Vo, Nicola Wadeson \
                    <scientificsoftware@diamond.ac.uk>
"""
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin
from savu.plugins.filters.base_filter import BaseFilter
from savu.core.iterate_plugin_group_utils import check_if_in_iterative_loop
import savu.core.utils as cu

import logging
import numpy as np
import scipy.ndimage as ndi
import pyfftw.interfaces.scipy_fftpack as fft


@register_plugin
class VoCentering(BaseFilter, CpuPlugin):

    def __init__(self):
        super(VoCentering, self).__init__("VoCentering")

    def _create_mask(self, nrow, ncol, radius, drop):
        du = 1.0 / ncol
        dv = (nrow - 1.0) / (nrow * 2.0 * np.pi)
        cen_row = np.int16(np.ceil(nrow / 2.0) - 1)
        cen_col = np.int16(np.ceil(ncol / 2.0) - 1)
        drop = min(drop, np.int16(np.ceil(0.05 * nrow)))
        mask = np.zeros((nrow, ncol), dtype='float32')
        for i in range(nrow):
            pos = np.int16(np.round(((i - cen_row) * dv / radius) / du))
            (pos1, pos2) = np.clip(np.sort(
                (-pos + cen_col, pos + cen_col)), 0, ncol - 1)
            mask[i, pos1:pos2 + 1] = 1.0
        mask[cen_row - drop:cen_row + drop + 1, :] = 0.0
        mask[:, cen_col - 1:cen_col + 2] = 0.0
        return mask

    def _coarse_search(self, sino, start_cor, stop_cor, ratio, drop):
        """
        Coarse search for finding the rotation center.
        """
        (nrow, ncol) = sino.shape
        start_cor, stop_cor = np.sort((start_cor, stop_cor))
        start_cor = np.int16(np.clip(start_cor, 0, ncol - 1))
        stop_cor = np.int16(np.clip(stop_cor, 0, ncol - 1))
        cen_fliplr = (ncol - 1.0) / 2.0
        flip_sino = np.fliplr(sino)
        comp_sino = np.flipud(sino)
        list_cor = np.arange(start_cor, stop_cor + 1.0)
        list_metric = np.zeros(len(list_cor), dtype=np.float32)
        mask = self._create_mask(2 * nrow, ncol, 0.5 * ratio * ncol, drop)
        sino_sino = np.vstack((sino, flip_sino))
        for i, cor in enumerate(list_cor):
            shift = np.int16(2.0 * (cor - cen_fliplr))
            _sino = sino_sino[nrow:]
            _sino[...] = np.roll(flip_sino, shift, axis=1)
            if shift >= 0:
                _sino[:, :shift] = comp_sino[:, :shift]
            else:
                _sino[:, shift:] = comp_sino[:, shift:]
            list_metric[i] = np.mean(
                np.abs(np.fft.fftshift(fft.fft2(sino_sino))) * mask)
        minpos = np.argmin(list_metric)
        if minpos == 0:
            self.error_msg_1 = "!!! WARNING !!! Global minimum is out of " \
                               "the searching range. Please extend smin"
            logging.warning(self.error_msg_1)
            cu.user_message(self.error_msg_1)
        if minpos == len(list_metric) - 1:
            self.error_msg_2 = "!!! WARNING !!! Global minimum is out of " \
                               "the searching range. Please extend smax"
            logging.warning(self.error_msg_2)
            cu.user_message(self.error_msg_2)
        rot_centre = list_cor[minpos]
        return rot_centre

    def _fine_search(self, sino, start_cor, search_radius,
                     search_step, ratio, drop):
        """
        Fine search for finding the rotation center.
        """
        # Denoising
        (nrow, ncol) = sino.shape
        flip_sino = np.fliplr(sino)
        search_radius = np.clip(np.abs(search_radius), 1, ncol // 10 - 1)
        search_step = np.clip(np.abs(search_step), 0.1, 1.1)
        start_cor = np.clip(start_cor, search_radius, ncol - search_radius - 1)
        cen_fliplr = (ncol - 1.0) / 2.0
        list_cor = start_cor + np.arange(
            -search_radius, search_radius + search_step, search_step)
        comp_sino = np.flipud(sino)  # Used to avoid local minima
        list_metric = np.zeros(len(list_cor), dtype=np.float32)
        mask = self._create_mask(2 * nrow, ncol, 0.5 * ratio * ncol, drop)
        for i, cor in enumerate(list_cor):
            shift = 2.0 * (cor - cen_fliplr)
            sino_shift = ndi.interpolation.shift(
                flip_sino, (0, shift), order=3, prefilter=True)
            if shift >= 0:
                shift_int = np.int16(np.ceil(shift))
                sino_shift[:, :shift_int] = comp_sino[:, :shift_int]
            else:
                shift_int = np.int16(np.floor(shift))
                sino_shift[:, shift_int:] = comp_sino[:, shift_int:]
            mat1 = np.vstack((sino, sino_shift))
            list_metric[i] = np.mean(
                np.abs(np.fft.fftshift(fft.fft2(mat1))) * mask)
        min_pos = np.argmin(list_metric)
        cor = list_cor[min_pos]
        return cor

    def _downsample(self, image, dsp_fact0, dsp_fact1):
        """Downsample an image by averaging.

        Parameters
        ----------
            image : 2D array.
            dsp_fact0 : downsampling factor along axis 0.
            dsp_fact1 : downsampling factor along axis 1.

        Returns
        ---------
            image_dsp : Downsampled image.
        """
        (height, width) = image.shape
        dsp_fact0 = np.clip(np.int16(dsp_fact0), 1, height // 2)
        dsp_fact1 = np.clip(np.int16(dsp_fact1), 1, width // 2)
        height_dsp = height // dsp_fact0
        width_dsp = width // dsp_fact1
        if dsp_fact0 == 1 and dsp_fact1 == 1:
            image_dsp = image
        else:
            image_dsp = image[0:dsp_fact0 * height_dsp, 0:dsp_fact1 * width_dsp]
            image_dsp = image_dsp.reshape(
                height_dsp, dsp_fact0, width_dsp, dsp_fact1).mean(-1).mean(1)
        return image_dsp

    def set_filter_padding(self, in_data, out_data):
        padding = np.int16(self.parameters['average_radius'])
        if padding > 0:
            in_data[0].padding = {'pad_multi_frames': padding}

    def pre_process(self):
        self.drop = np.int16(self.parameters['row_drop'])
        self.smin, self.smax = np.int16(self.parameters['search_area'])
        self.search_radius = np.float32(self.parameters['search_radius'])
        self.search_step = np.float32(self.parameters['step'])
        self.ratio = np.float32(self.parameters['ratio'])
        self.est_cor = self.parameters['start_pixel']
        self.broadcast_method = str(self.parameters['broadcast_method'])
        self.error_msg_1 = ""
        self.error_msg_2 = ""
        self.error_msg_3 = ""
        if not ((self.broadcast_method == 'mean')
                or (self.broadcast_method == 'median')
                or (self.broadcast_method == 'linear_fit')
                or (self.broadcast_method == 'nearest')):
            self.error_msg_3 = "!!!WARNING!!! Selected broadcasting method" \
                               " is out of the list. Use the default option:" \
                               " 'median'"
            logging.warning(self.error_msg_3)
            cu.user_message(self.error_msg_3)
            self.broadcast_method = 'median'
        in_pData = self.get_plugin_in_datasets()[0]
        data = self.get_in_datasets()[0]
        # the preview parameters from the centering plugin (calculated as absolute values - not related to the loader preview values)
        starts, stops, steps = data.get_preview().get_starts_stops_steps()[0:3]
        start_ind = starts[1]
        stop_ind = stops[1]
        step_ind = steps[1]
        name = data.get_name()
        # the preview parameters from the original loader (note that this metadata might be absent if the data has been modified
        # after loader and the preview metadata is not copied !)
        pre_start = self.exp.meta_data.get(name + '_preview_starts')[1]
        pre_stop = self.exp.meta_data.get(name + '_preview_stops')[1]
        pre_step = self.exp.meta_data.get(name + '_preview_steps')[1]
        self.origin_prev = np.arange(pre_start, pre_stop, pre_step)
        # making the plugin preview parameters relative to the loader preview parameters
        self.plugin_prev = self.origin_prev[start_ind:stop_ind:step_ind]
        num_sino = len(self.plugin_prev)
        if num_sino > 20:
            warning_msg = "\n!!!WARNING!!! You selected to calculate the " \
                          "center-of-rotation using '{}' sinograms.\n" \
                          "This is computationally expensive. Considering to " \
                          "adjust the preview parameter to use\na smaller " \
                          "number of sinograms (< 20).\n".format(num_sino)
            logging.warning(warning_msg)
            cu.user_message(warning_msg)

    def process_frames(self, data):
        if len(data[0].shape) > 2:
            sino = np.mean(data[0], axis=1)
        else:
            sino = data[0]
        (nrow, ncol) = sino.shape
        dsp_row = 1
        dsp_col = 1
        if ncol > 2000:
            dsp_col = 4
        if nrow > 2000:
            dsp_row = 2
        # Denoising
        sino_csearch = ndi.gaussian_filter(sino, (3, 1), mode='reflect')
        sino_fsearch = ndi.gaussian_filter(sino, (2, 2), mode='reflect')
        sino_dsp = self._downsample(sino_csearch, dsp_row, dsp_col)
        fine_srange = max(self.search_radius, dsp_col)
        off_set = 0.5 * dsp_col if dsp_col > 1 else 0.0
        if self.est_cor is None:
            self.est_cor = (ncol - 1.0) / 2.0
        else:
            self.est_cor = np.float32(self.est_cor)
        start_cor = np.int16(
            np.floor(1.0 * (self.est_cor + self.smin) / dsp_col))
        stop_cor = np.int16(
            np.ceil(1.0 * (self.est_cor + self.smax) / dsp_col))
        raw_cor = self._coarse_search(sino_dsp, start_cor, stop_cor,
                                      self.ratio, self.drop)
        cor = self._fine_search(
            sino_fsearch, raw_cor * dsp_col + off_set, fine_srange,
            self.search_step, self.ratio, self.drop)
        return [np.array([cor]), np.array([cor])]

    def post_process(self):
        in_datasets, out_datasets = self.get_datasets()
        cor_prev = out_datasets[0].data[...]
        cor_broad = out_datasets[1].data[...]
        cor_broad[:] = np.median(np.squeeze(cor_prev))
        self.cor_for_executive_summary = np.median(cor_broad[:])
        if self.broadcast_method == 'mean':
            cor_broad[:] = np.mean(np.squeeze(cor_prev))
            self.cor_for_executive_summary = np.mean(cor_broad[:])
        if (self.broadcast_method == 'linear_fit') and (len(cor_prev) > 1):
            afact, bfact = np.polyfit(self.plugin_prev, cor_prev[:, 0], 1)
            list_cor = self.origin_prev * afact + bfact
            cor_broad[:, 0] = list_cor
            self.cor_for_executive_summary = cor_broad[:]
        if (self.broadcast_method == 'nearest') and (len(cor_prev) > 1):
            for i, pos in enumerate(self.origin_prev):
                minpos = np.argmin(np.abs(pos - self.plugin_prev))
                cor_broad[i, 0] = cor_prev[minpos, 0]
            self.cor_for_executive_summary = cor_broad[:]
        out_datasets[1].data[:] = cor_broad[:]
        self.populate_meta_data('cor_preview', np.squeeze(cor_prev))
        self.populate_meta_data('centre_of_rotation',
                                out_datasets[1].data[:].squeeze(axis=1))

    def populate_meta_data(self, key, value):
        datasets = self.parameters['datasets_to_populate']
        in_meta_data = self.get_in_meta_data()[0]
        in_meta_data.set(key, value)
        for name in datasets:
            self.exp.index['in_data'][name].meta_data.set(key, value)

    def setup(self):
        self.exp.log(self.name + " Start calculating center of rotation")
        # set up the output dataset that is created by the plugin
        in_dataset, out_dataset = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('SINOGRAM', self.get_max_frames())
        slice_dirs = list(in_dataset[0].get_slice_dimensions())
        self.orig_full_shape = in_dataset[0].get_shape()

        # reduce the data as per data_subset parameter
        self.set_preview(in_dataset[0], self.parameters['preview'])
        total_frames = \
            self._calc_total_frames(in_dataset[0].get_preview(), slice_dirs)

        # copy all required information from in_dataset[0]
        fullData = in_dataset[0]
        new_shape = (np.prod(np.array(fullData.get_shape())[slice_dirs]), 1)
        self.orig_shape = \
            (np.prod(np.array(self.orig_full_shape)[slice_dirs]), 1)
        # check if the plugin is in an iterative loop:
        # - if not, then mark the two output datasets as "to remove" as normal
        # - but if so, then don't mark the two output datasets as "to remove",
        # since they need to be re-used in subsequent iterations
        iterate_group = check_if_in_iterative_loop(self.exp)
        to_remove = True
        if iterate_group is not None:
            to_remove = False
        out_dataset[0].create_dataset(shape=new_shape,
                                      axis_labels=['x.pixels', 'y.pixels'],
                                      remove=to_remove,
                                      transport='hdf5')
        out_dataset[0].add_pattern("METADATA", core_dims=(1,), slice_dims=(0,))

        out_dataset[1].create_dataset(shape=self.orig_shape,
                                      axis_labels=['x.pixels', 'y.pixels'],
                                      remove=to_remove,
                                      transport='hdf5')
        out_dataset[1].add_pattern("METADATA", core_dims=(1,), slice_dims=(0,))
        out_pData[0].plugin_data_setup('METADATA', self.get_max_frames())
        out_pData[1].plugin_data_setup('METADATA', self.get_max_frames())
        out_pData[1].meta_data.set('fix_total_frames', total_frames)
        self.exp.log(self.name + " End")

    def _calc_total_frames(self, preview, slice_dims):
        starts, stops, steps, _ = preview.get_starts_stops_steps()
        lengths = [len(np.arange(starts[i], stops[i], steps[i]))
                   for i in range(len(starts))]
        return np.prod([lengths[i] for i in slice_dims])

    def nOutput_datasets(self):
        return 2

    def get_max_frames(self):
        return 'single'

    def fix_transport(self):
        return 'hdf5'

    def executive_summary(self):
        if ((self.error_msg_1 == "")
                and (self.error_msg_2 == "")):
            msg = "Centre of rotation is : %s" % (
                str(self.cor_for_executive_summary))
        else:
            msg = "\n" + self.error_msg_1 + "\n" + self.error_msg_2
            msg2 = "(Not well) estimated centre of rotation is : %s" % (str(
                self.cor_for_executive_summary))
            cu.user_message(msg2)
        return [msg]
