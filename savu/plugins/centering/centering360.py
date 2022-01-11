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
.. module:: centering360
   :platform: Unix
   :synopsis: A plugin to find the center of rotation per frame
.. moduleauthor:: Nghia Vo, <scientificsoftware@diamond.ac.uk>
"""
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin
from savu.plugins.filters.base_filter import BaseFilter
import savu.core.utils as cu

import logging
import numpy as np
import scipy.ndimage as ndi
from scipy import stats

@register_plugin
class Centering360(BaseFilter, CpuPlugin):

    def __init__(self):
        super(Centering360, self).__init__("Centering360")

    def find_overlap(self, mat1, mat2, win_width, side=None, denoise=True, norm=False,
                     use_overlap=False):
        """
        Find the overlap area and overlap side between two images (Ref. [1]) where
        the overlap side referring to the first image.

        Parameters
        ----------
        mat1 : array_like
            2D array. Projection image or sinogram image.
        mat2 :  array_like
            2D array. Projection image or sinogram image.
        win_width : int
            Width of the searching window.
        side : {None, 0, 1}, optional
            Only there options: None, 0, or 1. "None" corresponding to fully
            automated determination. "0" corresponding to the left side. "1"
            corresponding to the right side.
        denoise : bool, optional
            Apply the Gaussian filter if True.
        norm : bool, optional
            Apply the normalization if True.
        use_overlap : bool, optional
            Use the combination of images in the overlap area for calculating
            correlation coefficients if True.

        Returns
        -------
        overlap : float
            Width of the overlap area between two images.
        side : int
            Overlap side between two images.
        overlap_position : float
            Position of the window in the first image giving the best
            correlation metric.

        References
        ----------
        .. [1] https://doi.org/10.1364/OE.418448
        """
        (_, ncol1) = mat1.shape
        (_, ncol2) = mat2.shape
        win_width = np.int16(np.clip(win_width, 6, min(ncol1, ncol2) // 2))
        if side == 1:
            (list_metric, offset) = self.search_overlap(mat1, mat2, win_width, side,
                                                   denoise, norm, use_overlap)
            (_, overlap_position) = self.calculate_curvature(list_metric)
            overlap_position = overlap_position + offset
            overlap = ncol1 - overlap_position + win_width // 2
        elif side == 0:
            (list_metric, offset) = self.search_overlap(mat1, mat2, win_width, side,
                                                   denoise, norm, use_overlap)
            (_, overlap_position) = self.calculate_curvature(list_metric)
            overlap_position = overlap_position + offset
            overlap = overlap_position + win_width // 2
        else:
            (list_metric1, offset1) = self.search_overlap(mat1, mat2, win_width, 1, norm,
                                                     denoise, use_overlap)
            (list_metric2, offset2) = self.search_overlap(mat1, mat2, win_width, 0, norm,
                                                     denoise, use_overlap)
            (curvature1, overlap_position1) = self.calculate_curvature(list_metric1)
            overlap_position1 = overlap_position1 + offset1
            (curvature2, overlap_position2) = self.calculate_curvature(list_metric2)
            overlap_position2 = overlap_position2 + offset2
            if curvature1 > curvature2:
                side = 1
                overlap_position = overlap_position1
                overlap = ncol1 - overlap_position + win_width // 2
            else:
                side = 0
                overlap_position = overlap_position2
                overlap = overlap_position + win_width // 2
        return overlap, side, overlap_position

    def search_overlap(self, mat1, mat2, win_width, side, denoise=True, norm=False,
                       use_overlap=False):
        """
        Calculate the correlation metrics between a rectangular region, defined
        by the window width, on the utmost left/right side of image 2 and the
        same size region in image 1 where the region is slided across image 1.

        Parameters
        ----------
        mat1 : array_like
            2D array. Projection image or sinogram image.
        mat2 : array_like
            2D array. Projection image or sinogram image.
        win_width : int
            Width of the searching window.
        side : {0, 1}
            Only two options: 0 or 1. It is used to indicate the overlap side
            respects to image 1. "0" corresponds to the left side. "1" corresponds
            to the right side.
        denoise : bool, optional
            Apply the Gaussian filter if True.
        norm : bool, optional
            Apply the normalization if True.
        use_overlap : bool, optional
            Use the combination of images in the overlap area for calculating
            correlation coefficients if True.

        Returns
        -------
        list_metric : array_like
            1D array. List of the correlation metrics.
        offset : int
            Initial position of the searching window where the position
            corresponds to the center of the window.
        """
        if denoise is True:
            mat1 = ndi.gaussian_filter(mat1, (2, 2), mode='reflect')
            mat2 = ndi.gaussian_filter(mat2, (2, 2), mode='reflect')
        (nrow1, ncol1) = mat1.shape
        (nrow2, ncol2) = mat2.shape
        if nrow1 != nrow2:
            raise ValueError("Two images are not at the same height!!!")
        win_width = np.int16(np.clip(win_width, 6, min(ncol1, ncol2) // 2 - 1))
        offset = win_width // 2
        win_width = 2 * offset  # Make it even
        ramp_down = np.linspace(1.0, 0.0, win_width)
        ramp_up = 1.0 - ramp_down
        wei_down = np.tile(ramp_down, (nrow1, 1))
        wei_up = np.tile(ramp_up, (nrow1, 1))
        if side == 1:
            mat2_roi = mat2[:, 0:win_width]
            mat2_roi_wei = mat2_roi * wei_up
        else:
            mat2_roi = mat2[:, ncol2 - win_width:]
            mat2_roi_wei = mat2_roi * wei_down
        list_mean2 = np.mean(np.abs(mat2_roi), axis=1)
        list_pos = np.arange(offset, ncol1 - offset)
        num_metric = len(list_pos)
        list_metric = np.ones(num_metric, dtype=np.float32)
        for i, pos in enumerate(list_pos):
            mat1_roi = mat1[:, pos - offset:pos + offset]
            if use_overlap is True:
                if side == 1:
                    mat1_roi_wei = mat1_roi * wei_down
                else:
                    mat1_roi_wei = mat1_roi * wei_up
            if norm is True:
                list_mean1 = np.mean(np.abs(mat1_roi), axis=1)
                list_fact = list_mean2 / list_mean1
                mat_fact = np.transpose(np.tile(list_fact, (win_width, 1)))
                mat1_roi = mat1_roi * mat_fact
                if use_overlap is True:
                    mat1_roi_wei = mat1_roi_wei * mat_fact
            if use_overlap is True:
                mat_comb = mat1_roi_wei + mat2_roi_wei
                list_metric[i] = (self.correlation_metric(mat1_roi, mat2_roi)
                                  + self.correlation_metric(mat1_roi, mat_comb)
                                  + self.correlation_metric(mat2_roi, mat_comb)) / 3.0
            else:
                list_metric[i] = self.correlation_metric(mat1_roi, mat2_roi)
        min_metric = np.min(list_metric)
        if min_metric != 0.0:
            list_metric = list_metric / min_metric
        return list_metric, offset

    def correlation_metric(self, mat1, mat2):
        """
        Calculate the correlation metric. Smaller metric corresponds to better
        correlation.

        Parameters
        ---------
        mat1 : array_like
        mat2 : array_like

        Returns
        -------
        float
            Correlation metric.
        """
        metric = np.abs(
            1.0 - stats.pearsonr(mat1.flatten('F'), mat2.flatten('F'))[0])
        return metric

    def calculate_curvature(self, list_metric):
        """
        Calculate the curvature of a fitted curve going through the minimum
        value of a metric list.

        Parameters
        ----------
        list_metric : array_like
            1D array. List of metrics.

        Returns
        -------
        curvature : float
            Quadratic coefficient of the parabola fitting.
        min_pos : float
            Position of the minimum value with sub-pixel accuracy.
        """
        radi = 2
        num_metric = len(list_metric)
        min_pos = np.clip(
            np.argmin(list_metric), radi, num_metric - radi - 1)
        list1 = list_metric[min_pos - radi:min_pos + radi + 1]
        (afact1, _, _) = np.polyfit(np.arange(0, 2 * radi + 1), list1, 2)
        list2 = list_metric[min_pos - 1:min_pos + 2]
        (afact2, bfact2, _) = np.polyfit(
            np.arange(min_pos - 1, min_pos + 2), list2, 2)
        curvature = np.abs(afact1)
        if afact2 != 0.0:
            num = - bfact2 / (2 * afact2)
            if (num >= min_pos - 1) and (num <= min_pos + 1):
                min_pos = num
        return curvature, np.float32(min_pos)

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

    def pre_process(self):
        self.win_width = np.int16(self.parameters['win_width'])
        self.side = self.parameters['side']
        self.denoise = self.parameters['denoise']
        self.norm = self.parameters['norm']
        self.use_overlap = self.parameters['use_overlap']

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
        starts, stops, steps = data.get_preview().get_starts_stops_steps()[0:3]
        start_ind = starts[1]
        stop_ind = stops[1]
        step_ind = steps[1]
        name = data.get_name()
        pre_start = self.exp.meta_data.get(name + '_preview_starts')[1]
        pre_stop = self.exp.meta_data.get(name + '_preview_stops')[1]
        pre_step = self.exp.meta_data.get(name + '_preview_steps')[1]
        self.origin_prev = np.arange(pre_start, pre_stop, pre_step)
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
        """
        Find the center-of-rotation (COR) in a 360-degree scan with offset COR use
        the method presented in Ref. [1].

        Parameters
        ----------
        data : array_like
            2D array. 360-degree sinogram.

        Returns
        -------
        cor : float
            Center-of-rotation.

        References
        ----------
        .. [1] https://doi.org/10.1364/OE.418448
        """
        sino = data[0]
        (nrow, ncol) = sino.shape
        nrow_180 = nrow // 2 + 1
        sino_top = sino[0:nrow_180, :]
        sino_bot = np.fliplr(sino[-nrow_180:, :])
        overlap, side, overlap_position =\
            self.find_overlap(sino_top, sino_bot, self.win_width, self.side,
                              self.denoise, self.norm, self.use_overlap)
        #overlap : Width of the overlap area between two halves
        #           of the sinogram.
        # side : Overlap side between two halves of the sinogram.
        # overlap_position : Position of the window in the first
        #           image giving the best correlation metric."""
        if side == 0:
            cor = overlap / 2.0 - 1.0
        else:
            cor = ncol - overlap / 2.0 - 1.0
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
        out_dataset[0].create_dataset(shape=new_shape,
                                      axis_labels=['x.pixels', 'y.pixels'],
                                      remove=True,
                                      transport='hdf5')
        out_dataset[0].add_pattern("METADATA", core_dims=(1,), slice_dims=(0,))

        out_dataset[1].create_dataset(shape=self.orig_shape,
                                      axis_labels=['x.pixels', 'y.pixels'],
                                      remove=True,
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
