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


class BaseTransportData(object):
    """
    Implements functions associated with the transport of the data.
    """

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
        raise NotImplementedError("get_padded_data needs to be"
                                  " implemented in  %s", self.__class__)

    def _calc_max_frames_transfer(self, nFrames):
        """ The number of frames each process should retrieve from file at a
        time.
        """
        pData = self._get_plugin_data()
        max_mft, min_mft, threshold = self.__checks_and_boundaries(nFrames)
        sdir, shape, total_frames, mpi_procs, frames_per_process = \
            pData._get_max_frames_parameters()

        # find all possible choices of nFrames, being careful with boundaries
        fchoices, size_list = self.__get_frame_choices(
                sdir, min(max_mft, np.prod([shape[d] for d in sdir])))

        if frames_per_process > threshold:
            min_mft = min(max(fchoices), min_mft)
            fchoices = [f for f in fchoices if f >= min_mft]

        mft, idx = self.__find_best_frame_distribution(
            fchoices, total_frames, mpi_procs, idx=True)

        # this should be enforced
        pData._set_shape_transfer(size_list[fchoices.index(mft)])

        if nFrames == 'single':
            pData._log_max_frames(mft, 1, total_frames, mpi_procs)
            return int(mft)

        mfp = nFrames if isinstance(nFrames, int) else min(mft, shape[sdir[0]])

        multi = self.__find_multiples_of_b_that_divide_a(mft, mfp)
        possible = sorted(list(set(set(multi).intersection(set(fchoices)))))

        # closest of fchoices to mfp plus difference as boundary padding
        if not possible:
            mft, _ = self.__find_closest_lower(fchoices[::-1], mfp)
            self.__set_boundary_padding(mfp - mft)
        else:
            mft = self.__find_best_frame_distribution(
                possible[::-1], total_frames, mpi_procs)

        pData._set_shape_transfer(size_list[fchoices.index(mft)])
        pData._log_max_frames(mft, mfp, total_frames, mpi_procs)

        # Retain the shape if the first slice dimension has length 1
        if mfp == 1 and nFrames != 1:
            self.__set_no_squeeze()
        return int(mft)

    def __checks_and_boundaries(self, nFrames):
        options = ['single', 'multiple']
        if not isinstance(nFrames, int) and nFrames not in options:
            e_str = "The value of nFrames is not recognised.  Please choose "
            "from 'single' and 'multiple' (or an integer in exceptional "
            "circumstances)."
            raise Exception(e_str)

        max_mft = 32  # max frames that can be transferred from file at a time
        frame_threshold = 32  # no idea if this is a good number
        # min frames required if frames_per_process > frame_threshold
        min_mft = 16
        if isinstance(nFrames, int) and nFrames > max_mft:
            logging.warn("The requested %s frames excedes the maximum "
                         "preferred of %s." % (nFrames, max_mft))
            max_mft = nFrames
        return max_mft, min_mft, frame_threshold

    def __find_closest_lower(self, vlist, value):
        rem = [f if f != 0 else value for f in [m % value for m in vlist]]
        min_val = min(rem, key=lambda x: abs(x-value))
        idx = rem.index(min_val)
        return vlist[idx], idx

    def __get_frame_choices(self, sdir, max_mft):
        """ Find all possible combinations of increasing slice dimension sizes
        with their product less than max_mft and return a list of these
        products. """
        nDims = len(sdir)
        temp = [1]*len(sdir)
        shape = self.get_shape()
        idx = 0
        choices = []
        size_list = []

        while(np.prod(temp) <= max_mft):
            dshape = shape[sdir[idx]]
            # could remove this if statement and ensure padding at the end of
            # each slice dimension instead.
            if dshape % temp[idx] == 0 or nDims == 1:
                choices.append(np.prod(temp))
                size_list.append(copy.copy(temp))
            if temp[idx] == dshape:
                idx += 1
                if idx == nDims:
                    break
            temp[idx] += 1

        return choices[::-1], size_list[::-1]

    def __find_multiples_of_b_that_divide_a(self, a, b):
        """ Find all positive multiples of b that divide a. """
        val = 1
        val_list = []
        i = 0
        while(val > 0):
            val = (int(a/b)+i)*b
            val_list.append(val)
            i -= 1
        return val_list[:-1]

    def __find_best_frame_distribution(self, flist, nframes, nprocs,
                                       idx=False):
        """ Determine which of the numbers in the list of possible frame
        chunks gives the best distribution of frames per process. """
        multi_list = [(nframes/float(v))/nprocs for v in flist]
        min_val, closest_lower_idx = self.__find_closest_lower(multi_list, 1)
        if idx:
            return flist[closest_lower_idx], closest_lower_idx
        return flist[closest_lower_idx]
