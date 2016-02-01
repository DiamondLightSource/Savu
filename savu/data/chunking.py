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
.. module:: hdf5_tomo_saver
   :platform: Unix
   :synopsis: A class for saving tomography data using the standard savers
   library.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import copy
from fractions import gcd

import numpy as np
from savu.plugins.utils import register_plugin

NX_CLASS = 'NX_class'


@register_plugin
class Chunking(object):
    """
    A class to save tomography data to a hdf5 file
    """

    def __init__(self, exp, patternDict):
        self.current = patternDict['current'][patternDict['current'].keys()[0]]
        if patternDict['next']:
            self.next = patternDict['next'][patternDict['next'].keys()[0]]
        else:
            self.next = self.current
        self.exp = exp

    def calculate_chunking(self, shape, ttype):
        """
        Calculate appropriate chunk sizes for this dataset
        """
        print "shape = ", shape
        if len(shape) < 3:
            return True

        intersect_cores, remaining_cores = self.separate_cores(shape)
        chunks = [1]*len(shape)
        adjust = self.set_adjust_params(shape)

        if 'VOLUME' in self.current.keys()[0]:
            self.set_volume_chunks(shape, chunks)
        else:
            self.set_chunks(intersect_cores, remaining_cores, chunks, shape,
                            adjust)

        if 0 in chunks:
            return True
        else:
            chunks = self.adjust_chunk_size(chunks, ttype, shape, adjust)
            print chunks
            return tuple(chunks)

    def adjust_chunk_size(self, chunks, ttype, shape, adjust):
        """
        Adjust the chunk size to as close to 1MB as possible
        """
        chunks = np.array(chunks)
        print "****initial chunks", chunks
        print "****adjust chunks", adjust
        chunk_size = np.prod(chunks)*np.dtype(ttype).itemsize
        cache_size = 1000000
        if (chunk_size > cache_size):
            print "decreasing"
            self.decrease_chunks(chunks, ttype, adjust)
        else:
            print "increasing"
            chunks = self.increase_chunks(chunks, ttype, shape, adjust)
        return tuple(chunks)

    def decrease_chunks(self, chunks, ttype, adjust):
        """
        Decrease the chunk size to below but as close to 1MB as possible
        """
        # if core dimensions are reduced then need to re-think: reduce by a factor! (of 2?)
        while ((np.prod(chunks)*np.dtype(ttype).itemsize) > 1000000):
            idx = self.get_idx_decrease(chunks, adjust)
            dim = adjust['dim'].index(idx)
            chunks[idx] = chunks[idx] - adjust['inc'][dim]

    def increase_chunks(self, chunks, ttype, shape, adjust):
        """
        Increase the chunk size as close to 1MB as possible
        """
        #*** need to check next indices if increasing the current one goes over
        # the 1MB mark
        next_chunks = copy.copy(chunks)
        while (((np.prod(next_chunks)*np.dtype(ttype).itemsize) < 1000000)
                and not np.any(np.greater(next_chunks, np.array(shape)))):
            chunks = copy.copy(next_chunks)
            idx = self.get_idx_increase(next_chunks, adjust)
            if idx == -1:
                return
            dim = adjust['dim'].index(idx)
            next_chunks[idx] = next_chunks[idx] + adjust['inc'][dim]
        return chunks

    def get_max_frames_dict(self):
        current_sdir = self.current['slice_dir'][0]
        next_sdir = self.next['slice_dir'][0]
        if current_sdir == next_sdir:
            common_denom = gcd(self.current['max_frames'],
                               self.next['max_frames'])
            ddict = {current_sdir: common_denom}
        else:
            ddict = {self.current['slice_dir'][0]: self.current['max_frames'],
                     self.next['slice_dir'][0]: self.next['max_frames']}
        return ddict

    def calc_max(self, shape, nFrames):
        """
        Calculate the max possible value of a chunking dimension
        """
        total_plugin_runs = np.ceil(float(shape)/nFrames)
        frame_list = np.arange(total_plugin_runs)
        nProcs = len(self.exp.meta_data.get_meta_data('processes'))
        frame_list_per_proc = np.array_split(frame_list, nProcs)
        flist_len = []
        for flist in frame_list_per_proc:
            flist_len.append(len(flist))
        runs_per_proc = np.median(np.array(flist_len))
        return runs_per_proc*nFrames

    def get_adjustable_dims(self):
        """
        Get all core dimensions and fastest changing slice dimension (all
        potentially adjustable)
        """
        dims = []
        dims += [self.current['slice_dir'][0]]
        dims += list(self.current['core_dir'])
        dims += [self.next['slice_dir'][0]]
        dims += list(self.next['core_dir'])
        return list(set(dims))

    def separate_cores(self, shape):
        """
        Based on the current and next patterns associated with the dataset
        that is being created, determine the shared/unshared core directions.
        """
        current_cores = self.current['core_dir']
        next_cores = self.next['core_dir']
        intersect = set(current_cores).intersection(set(next_cores))
        remaining = set(current_cores).difference(intersect).\
            union(set(next_cores).difference(intersect))
        return list(intersect), list(remaining)

    def set_volume_chunks(self, shape, chunks, adjust):
        """
        Calculate initial chunk values for volume datasets
        """
        adj_dims = self.get_adjustable_dims()
        for dim in adj_dims:
            chunks[dim] = min(shape[dim], 64)
        self.set_adjust_slice_dims(adjust, self.current['slice_dir'][0], shape)
        return chunks

    def set_chunks(self, in_cores, out_cores, chunks, shape, adjust):
        """
        Calculate initial chunk values
        """
        for dim in in_cores:
            chunks[dim] = shape[dim]
        max_frames_dict = self.get_max_frames_dict()
        print "theoutcores are:"+str(out_cores)
        for dim in out_cores:
            max_frames = max_frames_dict[dim]
            chunks[dim] = min(shape[dim], max_frames)
            adjust['inc'][dim] = max_frames
            adjust['max'][dim] = self.calc_max(shape[dim], max_frames)
        slice_dirs = \
            list(set(self.get_slice_dims()).difference(set(out_cores)))
        self.set_adjust_slice_dims(adjust, slice_dirs, shape)
        return chunks

    def set_adjust_params(self, shape):
        """
        Set adjustable dimension parameters (the dimension number, increment
        and max value)
        """
        adjust_dim = self.get_adjustable_dims()
        array_len = len(adjust_dim)
        adjust_max = [1]*array_len
        for i in range(array_len):
            adjust_max[i] = shape[adjust_dim[i]]
        return {'dim': adjust_dim, 'inc': [1]*array_len, 'max': adjust_max}

    def set_adjust_slice_dims(self, adjust, sdirs, shape):
        """
        Set adjustable parameters for the slice dimensions
        """
        max_frames = self.current['max_frames']
        for sdir in sdirs:
            adjust['inc'][sdir] = max_frames
            adjust['max'][sdir] = self.calc_max(shape[sdir], max_frames)

    def get_idx_decrease(self, chunks, adjust):
        """
        Determine the chunk dimension to decrease
        """
        check = lambda a, b, c: True if (a - b) < 1 else False
        self.check_adjust_dims(adjust, chunks, check)

        # process slice dimensions first
        current_sdir = \
            list(set(adjust['dim']).difference(self.get_slice_dims()))
        idx_order = np.argsort(chunks[current_sdir])[::-1]

        # if there are no slice dimensions try the core dimensions
        # *** change this
        if not idx_order.size:
            idx_order = np.argsort(chunks[adjust['dim']])
            print "idx_order=", idx_order

        return adjust['dim'][idx_order[0]] if idx_order.size else -1

    def get_idx_increase(self, chunks, adjust):
        """
        Determine the chunk dimension to increase
        """
        check = lambda a, b, c: True if (a - b) > c else False
        self.check_adjust_dims(adjust, chunks, check)
        idx_order = np.argsort(chunks[adjust['dim']])
        return adjust['dim'][idx_order[0]] if idx_order.size else -1

    def check_adjust_dims(self, adjust, chunks, check):
        nDel = 0
        for i in range(len(adjust['dim'])):
            i -= nDel
            dim = adjust['dim'][i]
            if check(chunks[dim], adjust['inc'][i], adjust['max'][i]):
                del adjust['dim'][i]
                del adjust['inc'][i]
                del adjust['max'][i]
                nDel += 1

    def get_slice_dims(self):
        c_slice = self.current['slice_dir'][0]
        c_slice = c_slice if isinstance(c_slice, list) else [c_slice]
        n_slice = self.next['slice_dir'][0]
        n_slice = n_slice if isinstance(n_slice, list) else [n_slice]
        slice_dims = list(set(c_slice + n_slice))
        return slice_dims
