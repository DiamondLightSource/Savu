# Copyright 2015 Diamond Light Source Ltd.
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
.. module:: base_transport_data
   :platform: Unix
   :synopsis: Base class for transport mechanism data functions.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import copy
import logging
import numpy as np
from typing import List


class BaseTransportData(object):
    """
    Implements functions associated with the transport of the data.
    """

    def __init__(self, data_obj, name='BaseTransportData'):
        self.data = data_obj
        self.mfp = None

    def _get_data_obj(self):
        return self.data

    def _get_slice_list_per_process(self, expInfo):
        """
        A slice list required by the current process.
        """
        raise NotImplementedError("get_slice_list_per_process needs to be"
                                  " implemented in  %s", self.__class__)

    def _get_padded_data(self, input_slice_list):
        """
        Fetch the data with relevant padding (as determined by the plugin).
        """
        raise NotImplementedError("_get_padded_data needs to be"
                                  " implemented in  %s", self.__class__)

    def _calc_max_frames_transfer(self, nFrames):
        """ Calculate the number of frames to transfer from file at a time.
        """
        raise NotImplementedError("_calc_max_frames_transfer needs to be"
                                  " implemented in  %s", self.__class__)

    def _calc_max_frames_process(self, nFrames):
        nSlices = self.params['shape'][self.params['sdir'][0]]
        mfp = 1 if nFrames == 'single' else nFrames if \
            isinstance(nFrames, int) else self.mfp if self.mfp else nSlices
        return int(mfp)

    def _calc_max_frames_transfer_single(self, nFrames):
        """ Only one transfer per process """
        self.params = self.data._get_plugin_data().meta_data.get_dictionary()
        mft = np.ceil(
                self.params['total_frames']/float(self.params['mpi_procs']))

        # added for basic runner
        nSlices = self.params['shape'][self.params['sdir'][0]]
        self.mfp = nFrames if isinstance(nFrames, int) else min(mft, nSlices)

        fchoices, size_list = self._get_frame_choices(
            self.params['sdir'], 1, mft)
        self.mft = mft
        return int(mft), size_list[fchoices.index(mft)]

    def _calc_max_frames_transfer_multi(self, nFrames):
        """ Multiple transfer per process """
        self.params = self.data._get_plugin_data().meta_data.get_dictionary()
        mft, fchoices, size_list = self.__get_optimum_distribution(nFrames)
        if nFrames == 'single':
            return mft, size_list[fchoices.index(mft)]
        nSlices = self.params['shape'][self.params['sdir'][0]]
        self.mfp = nFrames if isinstance(nFrames, int) else min(mft, nSlices)
        mft, fchoices, size_list = \
            self.__refine_distribution_for_multi_mfp(mft, size_list, fchoices)
        self.mft = mft
        return mft, size_list[fchoices.index(mft)]

    def _set_boundaries(self):
        b_per_f = self.params.get('bytes_per_frame')
        b_per_p = self.params.get('bytes_per_process')

        mem_multiply = \
            self._get_data_obj()._get_plugin_data()._plugin.get_mem_multiply()

        settings = self.data.exp.meta_data.get(
                ['system_params', 'data_transfer_settings'])
        max_bytes = self.__convert_str(
                settings['max_bytes'], b_per_p)*mem_multiply
        bytes_threshold = self.__convert_str(
                settings['bytes_threshold'], b_per_p)*mem_multiply
        b_per_p = b_per_p if b_per_p < bytes_threshold else bytes_threshold

        min_bytes = self.__convert_str(settings['min_bytes'], b_per_p)     
        max_mft = int(np.floor(float(max_bytes)/b_per_f))
        if max_mft == 0:
            raise Exception("The size of a single frame exceeds the permitted "
                            "maximum bytes per frame.")
        min_mft = int(max(np.floor(float(min_bytes) / b_per_f), 1))

        return min_mft, max_mft

    def __convert_str(self, val, b_per_p):
        if isinstance(val, str):
            # FIXME this is still a potential security risk!
            value = eval(val, {'__builtins__': None, 'b_per_p': b_per_p})
            return value

    def __get_optimum_distribution(self, nFrames):
        """ The number of frames each process should retrieve from file at a
        time.
        """
        min_mft, max_mft = self.__get_boundaries(nFrames)

        if isinstance(nFrames, int) and nFrames > max_mft:
            logging.warning("The requested %s frames excedes the maximum "
                         "preferred of %s." % (nFrames, max_mft))
            max_mft = nFrames

        # find all possible choices of nFrames, being careful with boundaries
        sdir = self.params['sdir']
        # for multiple mft slice dimensions
        #slice_shape = [self.params['shape'][d] for d in sdir]
        #nSlices = np.prod(slice_shape)
        nSlices = self.params['shape'][sdir[0]]
        nFrames = 1 if isinstance(nFrames, str) else nFrames
        fchoices, size_list = self._get_frame_choices(
            sdir, nFrames, min(max_mft, max(nFrames, nSlices)))

        threshold_idx = [i for i in range(len(fchoices)) if fchoices[i] >= min_mft]

        if threshold_idx:
            fchoices = [fchoices[i] for i in threshold_idx]
            size_list = [size_list[i] for i in threshold_idx]

# use this for multiple mft slice dimensions
#        mft, idx = self._find_best_frame_distribution(
#            size_list, slice_shape, self.params['mpi_procs'],
#            idx=True)
        mft, idx = self._find_best_frame_distribution(
            fchoices, nSlices, self.params['mpi_procs'], idx=True)
        return int(mft), fchoices, size_list

    def __refine_distribution_for_multi_mfp(self, mft, size_list, fchoices):
        flimit = self._get_data_obj()._get_plugin_data().get_frame_limit()
        mfp = self.mfp
        if flimit and flimit < mfp:
            mfp = flimit

        multi = self._find_multiples_of_b_that_divide_a(mft, mfp)
        possible = sorted(list(set(set(multi).intersection(set(fchoices)))),
                          reverse=True)
        idx = [fchoices.index(i) for i in possible]
        possible_size_list = [size_list[i] for i in idx]

        # closest of fchoices to mfp plus difference as boundary padding
        if not possible:
            mft, _ = self._find_closest_lower(fchoices[::-1], mfp)  # does this need to be updated?
        else:
            size_list = possible_size_list
            fchoices = possible
# use this for multiple mft slice dimensions
#            mft, idx = self._find_best_frame_distribution(
#                    size_list, self.params['total_frames'],
#                    self.params['mpi_procs'], idx=True)
            mft, idx = self._find_best_frame_distribution(
                    possible, self.params['total_frames'],
                    self.params['mpi_procs'], idx=True)

        self.mfp = mfp
        return int(mft), fchoices, size_list

    def __get_boundaries(self, nFrames):
        min_mft, max_mft = self._set_boundaries()
        if isinstance(nFrames, int) and nFrames > max_mft:
            logging.warning("The requested %s frames excedes the maximum "
                         "preferred of %s." % (nFrames, max_mft))
            max_mft = nFrames
        return min_mft, max_mft

    def __get_bool_slice_dir_index(self, dim, dir_idx):
        shape = self.data_info.get('orig_shape')[dim]
        bool_idx = np.ones(shape, dtype=bool)
        bool_idx[dir_idx] = True
        return bool_idx

    def _get_slice_dir_matrix(self, dim):
        starts, stops, steps, chunks = \
            self.data.get_preview().get_starts_stops_steps()
        chunk = chunks[dim]
        a = np.tile(np.arange(starts[dim], stops[dim], steps[dim]), (chunk, 1))
        b = np.transpose(np.tile(np.arange(chunk)-chunk // 2, (a.shape[1], 1)))
        dim_idx = a + b
        if dim_idx[dim_idx < 0].size:
            raise Exception('Cannot have a negative value in the slice list.')
        return dim_idx

    def _find_closest_lower(self, vlist, value):
        rem = [f if f != 0 else value for f in [m % value for m in vlist]]
        min_val = min(rem, key=lambda x: abs(x-value))
        idx = rem.index(min_val)
        return vlist[idx], idx

# use this for multiple mft slice dimensions
#    def _get_frame_choices(self, sdir, max_mft):
#        """ Find all possible combinations of increasing slice dimension sizes
#        with their product less than max_mft and return a list of these
#        products. """
#        nDims = len(sdir)
#        temp = [1]*len(sdir)
#        shape = self.data.get_shape()
#        idx = 0
#        choices = []
#        size_list = []
#
#        while(np.prod(temp) <= max_mft):
#            dshape = shape[sdir[idx]]
#            choices.append(np.prod(temp))
#            size_list.append(copy.copy(temp))
#
#            if temp[idx] == dshape:
#                idx += 1
#                if idx == nDims:
#                    break
#            temp[idx] += 1
#
#        return choices[::-1], size_list[::-1]
# the above method is commented out as it was found to be slower than the one
# below - try again in a different version of HDF5

    def _get_frame_choices(self, sdir, min_mft, max_mft):
        """ Find all possible combinations of increasing slice dimension sizes
        with their product less than max_mft and return a list of these
        products. """
        temp = [1]*len(sdir)
        temp[0] = min_mft
        shape = self.data.get_shape()
        idx = 0
        choices = []
        size_list = []

        while(np.prod(temp) <= max_mft):
            dshape = shape[sdir[idx]]
            choices.append(np.prod(temp))
            size_list.append(copy.copy(temp))

            if temp[idx] == dshape:
                break
            temp[idx] += 1

        return choices[::-1], size_list[::-1]

    def _find_multiples_of_b_that_divide_a(self, a, b):
        """ Find all positive multiples of b that divide a. """
        val_list = []
        i = 0
        val = (int(a/b)+i)*b
        while(val > 0):
            if a % val == 0:
                val_list.append(val)
            i -= 1
            val = (int(a/b)+i)*b
        return val_list

    def _find_best_frame_distribution(self, flist, nframes, nprocs, idx=False):
        """ Determine which of the numbers in the list of possible frame
        chunks gives the best distribution of frames per process. """
        multi_list: List[float] = [(nframes / float(v)) / nprocs for v in flist]
        min_val, closest_lower_idx = self._find_closest_lower(multi_list, 1)
        if idx:
            return flist[closest_lower_idx], closest_lower_idx
        return flist[closest_lower_idx]
