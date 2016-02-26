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
import logging
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
        self.pattern_dict = patternDict
        self.current = patternDict['current'][patternDict['current'].keys()[0]]
        if patternDict['next']:
            self.next = patternDict['next'][patternDict['next'].keys()[0]]
        else:
            self.next = self.current

        try:
            self.next_pattern = patternDict['next'].keys()[0]
        except AttributeError:
            self.next_pattern = patternDict['current'].keys()[0]

        self.exp = exp
        self.core = None
        self.slice1 = None
        self.other = None

    def calculate_chunking(self, shape, ttype):
        """
        Calculate appropriate chunk sizes for this dataset
        """
        logging.debug("shape = %s", shape)
        if len(shape) < 3:
            return True

        chunks = [1]*len(shape)
        adjust = self.set_adjust_params(shape)
        self.set_chunks(chunks, shape, adjust)

        if 0 in chunks:
            return True
        else:
            chunks = self.adjust_chunk_size(chunks, ttype, shape, adjust)
            logging.debug("chunks %s", chunks)
#            logging.debug("chunks before %s", chunks)
#            for chunk in chunks:
#                chunk += 1
#            logging.debug("chunks after %s", chunks)
            return tuple(chunks)

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
        inc_dict = {'up': [1]*array_len, 'down': [1]*array_len}
        bounds = {'min': [1]*array_len, 'max': adjust_max}
        return {'dim': adjust_dim, 'inc': inc_dict, 'bounds': bounds}

    def get_adjustable_dims(self):
        """
        Get all core dimensions and fastest changing slice dimension (all
        potentially adjustable)
        """
        self.core = \
            list(self.current['core_dir']) + list(self.next['core_dir'])
        c_sl = list(self.current['slice_dir'])
        n_sl = list(self.next['slice_dir'])
        self.slice1 = [c_sl[0]] + [n_sl[0]]
        self.other = c_sl[1:] + n_sl[1:]
        return list(set(self.core + self.slice1))

    def set_chunks(self, chunks, shape, adjust):
        """
        Calculate initial chunk values
        """
        chunk_functions = {0: self.slice_slice, 1: self.slice_other,
                           2: self.core_core, 3: self.core_other,
                           4: self.core_slice}
        adj_idx = 0
        for dim in adjust['dim']:
            count = (dim in self.core)*4 + (dim in self.slice1)*2 + \
                (dim in self.other) - 2
            chunks[dim] = chunk_functions[count](dim, adj_idx, adjust, shape)
            if 'VOLUME' in self.next_pattern:
                self.set_volume_bounds(adjust, dim, chunks)
            adj_idx += 1
        return chunks

    def set_volume_bounds(self, adjust, dim, chunks):
        adjust['bounds']['min'][dim] = \
            eval(str(62) + adjust['inc']['down'][dim])
        chunks[dim] = int(min(adjust['bounds']['max'][dim], 62))

    def core_core(self, dim, adj_idx, adjust, shape):
        adjust['inc']['up'][adj_idx] = '+1'
        adjust['inc']['down'][adj_idx] = '/2'
        adjust['bounds']['max'][adj_idx] = shape[dim]
        return shape[dim]

    def core_slice(self, dim, adj_idx, adjust, shape):
        max_frames = self.get_max_frames_dict()[dim]
        adjust['inc']['up'][adj_idx] = '+' + str(max_frames)
        adjust['inc']['down'][adj_idx] = '-' + str(max_frames)
        adjust['bounds']['max'][adj_idx] = \
            self.max_frames_per_process(shape[dim], max_frames)
        return min(max_frames, shape[dim])

    def core_other(self, dim, adj_idx, adjust, shape):
        adjust['inc']['up'][adj_idx] = '+1'
        adjust['inc']['down'][adj_idx] = '-1'
        adjust['bounds']['max'][adj_idx] = shape[dim]
        return 1

    def slice_slice(self, dim, adj_idx, adjust, shape):
        max_frames = self.get_max_frames_dict()[dim]
        adjust['inc']['up'][adj_idx] = '+' + str(max_frames)
        adjust['inc']['down'][adj_idx] = '-' + str(max_frames)
        adjust['bounds']['max'][adj_idx] = \
            self.max_frames_per_process(shape[dim], max_frames)
        return min(max_frames, shape[dim])

    def slice_other(self, dim, adj_idx, adjust, shape):
        adjust['inc']['up'][adj_idx] = '+1'
        adjust['inc']['down'][adj_idx] = '-1'
        adjust['bounds']['max'][adj_idx] = shape[dim]
        return 1

    def get_max_frames_dict(self):
        current_sdir = self.current['slice_dir'][0]
        next_sdir = self.next['slice_dir'][0]
        if current_sdir == next_sdir:
            c_max = self.current['max_frames']
            n_max = self.next['max_frames']
            least_common_multiple = (c_max*n_max)/gcd(c_max, n_max)
            ddict = {current_sdir: least_common_multiple}
        else:
            ddict = {self.current['slice_dir'][0]: self.current['max_frames'],
                     self.next['slice_dir'][0]: self.next['max_frames']}
        return ddict

    def max_frames_per_process(self, shape, nFrames):
        """
        Calculate the max possible frames per process
        """
        total_plugin_runs = np.ceil(float(shape)/nFrames)
        frame_list = np.arange(total_plugin_runs)
        nProcs = len(self.exp.meta_data.get_meta_data('processes'))
        frame_list_per_proc = np.array_split(frame_list, nProcs)
        flist_len = []
        for flist in frame_list_per_proc:
            flist_len.append(len(flist))
        runs_per_proc = int(np.median(np.array(flist_len)))
        return int(min(runs_per_proc*nFrames, shape))

    def adjust_chunk_size(self, chunks, ttype, shape, adjust):
        """
        Adjust the chunk size to as close to 1MB as possible
        """
        chunks = np.array(chunks)
        chunk_size = np.prod(chunks)*np.dtype(ttype).itemsize
        cache_size = 1000000
        if (chunk_size > cache_size):
            self.decrease_chunks(chunks, ttype, adjust)
        else:
            chunks = self.increase_chunks(chunks, ttype, shape, adjust)
        return tuple(chunks)

    def decrease_chunks(self, chunks, ttype, adjust):
        """
        Decrease the chunk size to below but as close to 1MB as possible
        """
        while ((np.prod(chunks)*np.dtype(ttype).itemsize) > 1000000):
            idx = self.get_idx_decrease(chunks, adjust)
            dim = adjust['dim'].index(idx)
#            if idx == -1:
#                break
            chunks[idx] = int(np.ceil(eval(str(float(chunks[idx])) +
                              adjust['inc']['down'][dim])))

    def increase_chunks(self, chunks, ttype, shape, adjust):
        """
        Increase the chunk size as close to 1MB as possible
        """
        next_chunks = copy.copy(chunks)
        while ((np.prod(next_chunks)*np.dtype(ttype).itemsize) <= 1000000):
            chunks = copy.copy(next_chunks)
            idx = self.get_idx_increase(next_chunks, adjust)
            if idx == -1:
                break
            dim = adjust['dim'].index(idx)
            next_chunks[idx] = \
                eval(str(next_chunks[idx]) + adjust['inc']['up'][dim])
        return chunks

    def get_idx_decrease(self, chunks, adjust):
        """
        Determine the chunk dimension to decrease
        """
        self.check = lambda a, b, c, i: \
            True if (eval(str(a) + b[i])) < c['min'][i] else False
        self.check_adjust_dims(adjust, chunks, 'down')
        return self.get_idx_order(adjust, chunks, 'down')

    def get_idx_increase(self, chunks, adjust):
        """
        Determine the chunk dimension to increase
        """
        self.check = lambda a, b, c, i: \
            True if (eval(str(a) + b[i])) > c['max'][i] else False
        self.check_adjust_dims(adjust, chunks, 'up')
        return self.get_idx_order(adjust, chunks, 'up')

    def get_idx_order(self, adjust, chunks, direction):
        process_order = [self.slice1, self.core]
        sl = slice(None, None, -1)
        if direction is 'up':
            sl = slice(None, None, 1)
            process_order = process_order[::-1]

        avail1 = list(set(adjust['dim']).intersection(process_order[0]))
        idx_order = np.argsort(chunks[avail1])[sl]

        if not idx_order.size:
            avail2 = list(set(adjust['dim']).intersection(process_order[1]))
            idx_order = np.argsort(chunks[avail2])[sl]

        return adjust['dim'][idx_order[0]] if idx_order.size else -1

    def check_adjust_dims(self, adjust, chunks, up_down):
        nDel = 0
        for i in range(len(adjust['dim'])):
            i -= nDel
            dim = adjust['dim'][i]
            if self.check(chunks[dim], adjust['inc'][up_down],
                          adjust['bounds'], i):
                adjust['inc']['down'][i] = '-1'
            if self.check(chunks[dim], adjust['inc'][up_down],
                          adjust['bounds'], i):
                del adjust['dim'][i]
                del adjust['inc']['up'][i]
                del adjust['inc']['down'][i]
                del adjust['bounds']['max'][i]
                del adjust['bounds']['min'][i]
                nDel += 1
