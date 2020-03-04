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
.. module:: vo_centering_iterative
   :platform: Unix
   :synopsis: A plugin to find the center of rotation per frame
.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>
"""

import math
import logging
import numpy as np
import scipy.ndimage as ndi
import scipy.ndimage.filters as filter
import pyfftw.interfaces.scipy_fftpack as fft

from scipy import signal

from savu.plugins.utils import register_plugin
from savu.data.plugin_list import CitationInformation
from savu.plugins.filters.base_filter import BaseFilter
from savu.plugins.driver.iterative_plugin import IterativePlugin

#    :u*param search_area: Search area in pixels from horizontal approximate \
#        centre of the image. Default: (-50, 50).
#    Deprecated !!!

@register_plugin
class VoCenteringIterative(BaseFilter, IterativePlugin):
    """
    A plugin to calculate the centre of rotation using the Vo Method

    :param ratio: The ratio between the size of object and FOV of \
        the camera. Default: 0.5.
    :param row_drop: Drop lines around vertical center of the \
        mask. Default: 20.
    :param search_radius: Use for fine searching. Default: 6.
    :param step: Step of fine searching. Default: 0.5.
    :param expand_by: The number of pixels to expand the search region by \
        on each iteration.  Default: 5
    :param boundary_distance: Accepted distance of minima from the boundary of\
        the listshift in the coarse search.  Default: 3.
    :u*param preview: A slice list of required frames (sinograms) to use in \
    the calulation of the centre of rotation (this will not reduce the data \
    size for subsequent plugins). Default: [].
    :param datasets_to_populate: A list of datasets which require this \
        information. Default: [].
    :param out_datasets: The default \
        names. Default: ['cor_raw','cor_fit', 'reliability'].
    :u*param start_pixel: The approximate centre. If value is None, take the \
        value from .nxs file else set to image centre. Default: None.
    """

    def __init__(self):
        super(VoCenteringIterative, self).__init__("VoCenteringIterative")
        self.search_area = (-20, 20)
        self.peak_height_min = 50000  # arbitrary
        self.min_dist = 3  # min distance deamed acceptible from boundary
        self.expand_by = 5  # expand the search region by this amount
        self.list_shift = None
        self.warning_level = 0
        self.final = False
        self.at_boundary = False
        self.list_metric = []
        self.expand_direction = None

    def _create_mask(self, Nrow, Ncol, obj_radius):
        du, dv = 1.0/Ncol, (Nrow-1.0)/(Nrow*2.0*math.pi)
        cen_row, cen_col = int(np.ceil(Nrow/2)-1), int(np.ceil(Ncol/2)-1)
        drop = self.parameters['row_drop']
        mask = np.zeros((Nrow, Ncol), dtype=np.float32)
        for i in range(Nrow):
            num1 = np.round(((i-cen_row)*dv/obj_radius)/du)
            p1, p2 = (np.clip(np.sort((-num1+cen_col, num1+cen_col)),
                              0, Ncol-1)).astype(int)
            mask[i, p1:p2+1] = np.ones(p2-p1+1, dtype=np.float32)

        if drop < cen_row:
            mask[cen_row-drop:cen_row+drop+1, :] = \
                np.zeros((2*drop + 1, Ncol), dtype=np.float32)
        mask[:, cen_col-1:cen_col+2] = np.zeros((Nrow, 3), dtype=np.float32)
        return mask

    def _get_start_shift(self, centre):
        if self.parameters['start_pixel'] is not None:
            shift = centre - int(self.parameters['start_pixel']/self.downlevel)
        else:
            in_mData = self.get_in_meta_data()[0]
            shift = centre - in_mData['centre'] if 'centre' in \
                list(in_mData.get_dictionary().keys()) else 0
        return int(shift)

    def _coarse_search(self, sino, list_shift):
        # search minsearch to maxsearch in 1 pixel steps
        list_metric = np.zeros(len(list_shift), dtype=np.float32)
        (Nrow, Ncol) = sino.shape
        # check angles to determine if a sinogram should be chopped off.
        # Copy the sinogram and flip left right, to make a full [0:2Pi] sino
        sino2 = np.fliplr(sino[1:])
        # This image is used for compensating the shift of sino2
        compensateimage = np.zeros((Nrow-1, Ncol), dtype=np.float32)
        # Start coarse search in which the shift step is 1
        compensateimage[:] = np.flipud(sino)[1:]
        mask = self._create_mask(2*Nrow-1, Ncol,
                                 0.5*self.parameters['ratio']*Ncol)
        count = 0
        for i in list_shift:
            sino2a = np.roll(sino2, i, axis=1)
            if i >= 0:
                sino2a[:, 0:i] = compensateimage[:, 0:i]
            else:
                sino2a[:, i:] = compensateimage[:, i:]
            list_metric[count] = np.sum(
                np.abs(fft.fftshift(fft.fft2(np.vstack((sino, sino2a)))))*mask)
            count += 1
        return list_metric

    def _fine_search(self, sino, raw_cor):
        (Nrow, Ncol) = sino.shape
        centerfliplr = (Ncol + 1.0)/2.0-1.0
        # Use to shift the sino2 to the raw CoR
        shiftsino = np.int16(2*(raw_cor-centerfliplr))
        sino2 = np.roll(np.fliplr(sino[1:]), shiftsino, axis=1)
        lefttake = 0
        righttake = Ncol-1
        search_rad = self.parameters['search_radius']

        if raw_cor <= centerfliplr:
            lefttake = np.int16(np.ceil(search_rad+1))
            righttake = np.int16(np.floor(2*raw_cor-search_rad-1))
        else:
            lefttake = np.int16(np.ceil(raw_cor-(Ncol-1-raw_cor)+search_rad+1))
            righttake = np.int16(np.floor(Ncol-1-search_rad-1))

        Ncol1 = righttake-lefttake + 1
        mask = self._create_mask(2*Nrow-1, Ncol1,
                                 0.5*self.parameters['ratio']*Ncol)
        numshift = np.int16((2*search_rad)/self.parameters['step'])+1
        listshift = np.linspace(-search_rad, search_rad, num=numshift)
        listmetric = np.zeros(len(listshift), dtype=np.float32)
        num1 = 0
        factor1 = np.mean(sino[-1, lefttake:righttake])
        for i in listshift:
            sino2a = ndi.interpolation.shift(sino2, (0, i), prefilter=False)
            factor2 = np.mean(sino2a[0, lefttake:righttake])
            sino2a = sino2a*factor1/factor2
            sinojoin = np.vstack((sino, sino2a))
            listmetric[num1] = np.sum(np.abs(fft.fftshift(
                fft.fft2(sinojoin[:, lefttake:righttake + 1])))*mask)
            num1 = num1 + 1
        minpos = np.argmin(listmetric)
        rotcenter = raw_cor + listshift[minpos]/2.0
        return rotcenter

    def _get_listshift(self):
        smin, smax = self.search_area if self.get_iteration() is 0 \
            else self._expand_search()
        list_shift = np.arange(smin, smax+2, 2) - self.start_shift
        logging.debug('list shift is %s', list_shift)
        return list_shift

    def _expand_search(self):
        if self.expand_direction == 'left':
            return self._expand_left()
        elif self.expand_direction == 'right':
            return self._expand_right()
        else:
            raise Exception('Unknown expand direction.')

    def _expand_left(self):
        smax = self.list_shift[0] - 2
        smin = smax - self.expand_by*2

        if smin <= -self.boundary:
            smin = -self.boundary
            self.at_boundary = True
        return smin, smax

    def _expand_right(self):
        smin = self.list_shift[-1] + 2
        smax = self.list_shift[-1] + self.expand_by*2

        if smax <= self.boundary:
            smax = self.boundary
            self.at_boundary = True

        return smin, smax

    def pre_process(self):
        pData = self.get_plugin_in_datasets()[0]
        label = pData.get_data_dimension_by_axis_label
        Ncol = pData.get_shape()[label('detector_x')]
        self.downlevel = 4 if Ncol > 1800 else 1
        self.downsample = slice(0, Ncol, self.downlevel)
        Ncol_downsample = len(np.arange(0, Ncol, self.downlevel))
        self.centre_fliplr = (Ncol_downsample - 1.0)/2.0
        self.start_shift = self._get_start_shift(self.centre_fliplr)*2
        self.boundary = int(np.ceil(Ncol/4.0))

    def process_frames(self, data):
        if not self.final:
            logging.debug('performing coarse search for iteration %s',
                          self.get_iteration())
            sino = filter.gaussian_filter(data[0][:, self.downsample], (3, 1))
            list_shift = self._get_listshift()
            list_metric = self._coarse_search(sino, list_shift)
            self._update_lists(list(list_shift), list(list_metric))

            self.coarse_cor, dist, reliability_metrics = \
                self._analyse_result(self.list_metric, self.list_shift)

            return [np.array([self.coarse_cor]), np.array([dist]),
                    np.array([reliability_metrics]), np.array([self.list_metric])]
        else:
            logging.debug("performing fine search")
            sino = filter.median_filter(data[0], (2, 2))
            cor = self._fine_search(sino, self.coarse_cor)
            self.set_processing_complete()
            return [np.array([cor]), np.array([self.list_metric])]

    def _update_lists(self, shift, metric):
        if self.expand_direction == 'left':
            self.list_shift = shift + self.list_shift
            self.list_metric = metric + self.list_metric
        elif self.expand_direction == 'right':
            self.list_shift += shift
            self.list_metric += metric
        else:
            self.list_shift = shift
            self.list_metric = metric

    def _analyse_result(self, metric, shift):
        minpos = np.argmin(metric)
        dist = min(abs(len(shift) - minpos), -minpos)

        rot_centre = (self.centre_fliplr + shift[minpos]/2.0)*self.downlevel
        peaks = self._find_peaks(metric)

        good_nPeaks = True
        if len(peaks) != 1:
            good_nPeaks = False
        good_peak_height = True if np.any(peaks) and \
            max(peaks) > self.peak_height_min else False

        metric = 0.0
        if (good_peak_height and good_nPeaks):
            metric = 1.0
        elif (good_peak_height or good_nPeaks):
            metric = 0.5

        return rot_centre, dist, metric

    def _find_peaks(self, metric):
        import peakutils
        grad2 = np.gradient(np.gradient(metric))
        grad2[grad2 < 0] = 0
        index = peakutils.indexes(grad2, thres=0.5, min_dist=3)
        return np.sort(grad2[index])

    def post_process(self):
        logging.debug("in the post process function")
        in_datasets, out_datasets = self.get_datasets()

        # =====================================================================
        # Analyse distance of centre values from boundary of search region
        dist_from_boundary = np.squeeze(out_datasets[1].data[...])
        near_boundary = np.where(abs(dist_from_boundary) < self.min_dist)[0]
        nEntries = len(dist_from_boundary)

        # Case1: Greater than half the results are near the boundary
        if (len(near_boundary)/float(nEntries)) > 0.5:
            # find which boundary
            signs = np.sign(dist_from_boundary[near_boundary])
            left, right = len(signs[signs < 0]), len(signs[signs > 0])

            logging.debug("res: results are near boundary")
            if not self.at_boundary:
                # if they are all at the same boundary expand the search region
                if not (left and right):
                    logging.debug("res: expanding")
                    self.expand_direction = 'left' if left else 'right'
                # if they are at different boundaries determine which values
                # are most reliable
                else:
                    logging.debug("res: choosing a boundary")
                    self.expand_direction = \
                        self._choose_boundary(near_boundary, signs)
                    # case that the results are close to different boundaries
                    # Analyse reliability and choose direction
            else:
                logging.debug("res: at the edge of the boundary")
                # Move on to the fine search
                self._set_final_process()
                self.warning_level = 1 # change this to be more descriptive ***
        else:
            logging.debug("result is not near the boundary")
            # Move on to the fine search
            self._set_final_process()
        # =====================================================================

    def _choose_boundary(self, idx, signs):
        good, maybe, bad = self._get_reliability_levels()
        sign = self._check_entries(good, signs[good])
        self.warning_level = 0
        if not sign:
            sign = self._check_entries(maybe, signs[maybe])
            self.warning_level = 1
        if not sign:
            sign = self._check_entries(bad, signs[bad])
            self.warning_level = 2
        return sign

    def _check_entries(self, idx, signs):
        if np.any(idx):
            left, right = signs[signs < 0], signs[signs > 0]
            if not (left and right):
                # use all the good ones
                return 'left' if left else 'right'
        return None

    def _get_reliability_levels(self, final=False):
        in_datasets, out_datasets = \
            self.get_datasets() if not final else self.get_original_datasets()
        reliability = np.squeeze(out_datasets[2].data[...])
        logging.debug('reliability is %s', reliability)
        good = np.where(reliability == 1.0)[0]
        maybe = np.where(reliability == 0.5)[0]
        bad = np.where(reliability == 0.0)[0]
        return good, maybe, bad

    def final_post_process(self):

        # choose which values to include
        good, maybe, bad = self._get_reliability_levels(final=True)
        # Do I need to change the warning levels here?
        entries = good if np.any(good) else maybe if np.any(maybe) else bad
        self.warning_level = 0 if np.any(good) else 1 if np.any(maybe) else 2
        logging.debug('sinograms used in final calculations are %s', entries)

        # do some curve fitting here
        # Get a handle on the original datasets
        in_dataset, out_dataset = self.get_original_datasets()
        cor_raw = np.squeeze(out_dataset[0].data[...])[entries]
        cor_fit = out_dataset[1].data[...]
        fit = np.zeros(cor_fit.shape)
        fit[:] = np.median(cor_raw)
        cor_fit = fit
        out_dataset[1].data[:] = cor_fit[:]

        self.populate_meta_data('cor_raw', cor_raw)
        self.populate_meta_data('centre_of_rotation',
                                out_dataset[1].data[:].squeeze(axis=1))

    def _set_final_process(self):
        self.final = True
        self.post_process = self.final_post_process
        in_dataset, out_dataset = self.get_datasets()
        self.set_iteration_datasets(
                self.get_iteration()+1, [in_dataset[0]], [out_dataset[0]])

    def populate_meta_data(self, key, value):
        datasets = self.parameters['datasets_to_populate']
        in_meta_data = self.get_in_meta_data()[0]
        in_meta_data.set(key, value)
        for name in datasets:
            self.exp.index['in_data'][name].meta_data.set(key, value)

    def setup(self):
        # set up the output dataset that is created by the plugin
        in_dataset, out_dataset = self.get_datasets()

        self.orig_full_shape = in_dataset[0].get_shape()

        # reduce the data as per data_subset parameter
        self.set_preview(in_dataset[0], self.parameters['preview'])

        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('SINOGRAM', self.get_max_frames())
        # copy all required information from in_dataset[0]
        fullData = in_dataset[0]

        slice_dirs = np.array(in_dataset[0].get_slice_dimensions())
        new_shape = (np.prod(np.array(fullData.get_shape())[slice_dirs]), 1)
        self.orig_shape = \
            (np.prod(np.array(self.orig_full_shape)[slice_dirs]), 1)

        self._create_metadata_dataset(out_dataset[0], new_shape)
        self._create_metadata_dataset(out_dataset[1], self.orig_shape)
        self._create_metadata_dataset(out_dataset[2], new_shape)
        
        # output metric
        new_shape = (np.prod(np.array(fullData.get_shape())[slice_dirs]), 21)
        self._create_metadata_dataset(out_dataset[3], new_shape)

        out_pData[0].plugin_data_setup('METADATA', self.get_max_frames())
        out_pData[1].plugin_data_setup('METADATA', self.get_max_frames())
        out_pData[2].plugin_data_setup('METADATA', self.get_max_frames())
        out_pData[3].plugin_data_setup('METADATA', self.get_max_frames())

    def _create_metadata_dataset(self, data, shape):
        data.create_dataset(shape=shape,
                            axis_labels=['x.pixels', 'y.pixels'],
                            remove=True,
                            transport='hdf5')
        data.add_pattern("METADATA", core_dims=(1,), slice_dims=(0,))

    def nOutput_datasets(self):
        return 4

    def get_max_frames(self):
        return 'single'

    def fix_transport(self):
        # This plugin requires communication between processes in the post
        # process, which it does via files
        return 'hdf5'

    def executive_summary(self):
        if self.warning_level == 0:
            msg = "Confidence in the centre value is high."
        elif self.warning_level == 1:
            msg = "Confidence in the centre value is average."
        else:
            msg = "Confidence in the centre value is low."
        return [msg]

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
        cite_info.doi = "https://doi.org/10.1364/OE.22.019078"
        return cite_info
