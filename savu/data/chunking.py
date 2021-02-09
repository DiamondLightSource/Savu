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
.. module:: chunking
   :platform: Unix
   :synopsis: A class to optimise hdf5 chunking
.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>
"""

import copy
import logging
from math import gcd
import numpy as np


class Chunking(object):
    """
    A class to save tomography data to a hdf5 file
    """

    def __init__(self, exp, patternDict):
        self.pattern_dict = patternDict
        self.current = patternDict['current'][list(patternDict['current'].keys())[0]]
        if patternDict['next']:
            self.next = patternDict['next'][list(patternDict['next'].keys())[0]]
        else:
            self.next = self.current

        try:
            self.next_pattern = list(patternDict['next'].keys())[0]
        except AttributeError:
            self.next_pattern = list(patternDict['current'].keys())[0]

        self.exp = exp
        self.core = None
        self.slice1 = None
        self.other = None
        self.default_chunk_max = 1000000

    def __lustre_workaround(self, chunks, shape):
        nChunks_to_create_file = \
            np.ceil(np.prod(np.array(shape)/np.array(chunks, dtype=np.float)))
        nProcesses = self.exp.meta_data.get('processes')
        dims = list(range(len(shape)))
        chunks = list(chunks)
        if nChunks_to_create_file < nProcesses:
            idx = [i for i in dims if shape[i] - chunks[i] > 0 and
                   chunks[i] > 1]
            idx = idx if idx else [i for i in dims if chunks[i] > 1]
            if idx:
                chunks[idx[0]] = int(np.ceil(chunks[idx[0]] / 2.0))
                return tuple(chunks)
            else:
                raise Exception('There is an error in the lustre workaround')

    def _calculate_chunking(self, shape, ttype, chunk_max=None):
        """
        Calculate appropriate chunk sizes for this dataset
        """
        self.chunk_max = chunk_max if chunk_max else self.default_chunk_max
        logging.debug("shape = %s", shape)
        if len(shape) < 3:
            return True

        chunks = [1]*len(shape)
        adjust = self.__set_adjust_params(shape)
        self.__set_chunks(chunks, shape, adjust)

        if 0 in chunks:
            return True
        else:
            chunks = self.__adjust_chunk_size(chunks, ttype, shape, adjust)
            # temporary work around for lustre
            if self.exp.meta_data.get('lustre') is True:
                chunks = self.__lustre_workaround(chunks, shape)

            logging.debug("chunk size %s", chunks)
            return tuple(chunks)

    def __set_adjust_params(self, shape):
        """
        Set adjustable dimension parameters (the dimension number, increment
        and max value)
        """
        adjust_dim = self.__get_adjustable_dims()
        array_len = len(adjust_dim)
        adjust_max = [1]*array_len

        for i in range(array_len):
            adjust_max[i] = shape[adjust_dim[i]]

        inc_dict = {'up': [1]*array_len, 'down': [1]*array_len}
        bounds = {'min': [1]*array_len, 'max': adjust_max}
        return {'dim': adjust_dim, 'inc': inc_dict, 'bounds': bounds}

    def __get_adjustable_dims(self):
        """
        Get all core dimensions and fastest changing slice dimension (all
        potentially adjustable)
        """
        self.core = \
            list(self.current['core_dims']) + list(self.next['core_dims'])
        c_sl = list(self.current['slice_dims'])
        n_sl = list(self.next['slice_dims'])
        self.slice1 = [c_sl[0]] + [n_sl[0]]
        self.other = c_sl[1:] + n_sl[1:]
        return list(set(self.core + self.slice1))

    def __set_chunks(self, chunks, shape, adjust):
        """
        Calculate initial chunk values
        """
        chunk_functions = {0: self.__slice_slice, 1: self.__slice_other,
                           2: self.__core_core, 3: self.__core_other,
                           4: self.__core_slice}
        adj_idx = 0
        for dim in adjust['dim']:
            count = (dim in self.core)*4 + (dim in self.slice1)*2 + \
                (dim in self.other) - 2
            chunks[dim] = chunk_functions[count](dim, adj_idx, adjust, shape)
#            if 'VOLUME' in self.next_pattern:
#                self.__set_volume_bounds(adjust, dim, chunks)
            adj_idx += 1
        return chunks

    def __set_volume_bounds(self, adjust, dim, chunks):
        adjust['bounds']['min'][dim] = \
            eval(str(62) + adjust['inc']['down'][dim])
        chunks[dim] = int(min(adjust['bounds']['max'][dim], 62))

    def __core_core(self, dim, adj_idx, adjust, shape):
        adjust['inc']['up'][adj_idx] = '+1'
        adjust['inc']['down'][adj_idx] = '/2'
        adjust['bounds']['max'][adj_idx] = shape[dim]
        return shape[dim]

    def __core_slice(self, dim, adj_idx, adjust, shape):
        max_frames = self.__get_max_frames_dict()[dim]
        adjust['inc']['up'][adj_idx] = '+' + str(max_frames)
        adjust['inc']['down'][adj_idx] = '/2'  # '-' + str(max_frames)

        # which is the slice dimension: current or next?
        ddict = self.current if dim in self.current['slice_dims'] else self.next
        shape, allslices = self.__get_shape(shape, ddict)

        adjust['bounds']['max'][adj_idx] = self.__max_frames_per_process(
                shape, max_frames, allslices=allslices)
        return min(max_frames, shape)

    def __core_other(self, dim, adj_idx, adjust, shape):
        adjust['inc']['up'][adj_idx] = '+1'
        adjust['inc']['down'][adj_idx] = '-1'
        adjust['bounds']['max'][adj_idx] = shape[dim]
        return 1

    def __slice_slice(self, dim, adj_idx, adjust, shape):
        max_frames = self.__get_max_frames_dict()[dim]
        adjust['inc']['up'][adj_idx] = '+' + str(max_frames)
        adjust['inc']['down'][adj_idx] = '/2'

        shape1 = np.prod([shape[s] for s in self.current['slice_dims']])
        shape2 = np.prod([shape[s] for s in self.next['slice_dims']])
        ddict = self.current if shape1 < shape2 else self.next
        shape, allslices = self.__get_shape(shape, ddict)
        adjust['bounds']['max'][adj_idx] = self.__max_frames_per_process(
                shape, max_frames, allslices=allslices)
        return min(max_frames, shape)

    def __slice_other(self, dim, adj_idx, adjust, shape):
        adjust['inc']['up'][adj_idx] = '+1'
        adjust['inc']['down'][adj_idx] = '-1'
        adjust['bounds']['max'][adj_idx] = shape[dim]
        return 1

    def __get_max_frames_dict(self):
        current_sdir = self.current['slice_dims'][0]
        next_sdir = self.next['slice_dims'][0]
        mft = 'max_frames_transfer'
        if current_sdir == next_sdir:
            c_max = self.current[mft]
            n_max = self.next[mft]
            least_common_multiple = (c_max*n_max) // gcd(c_max, n_max)
            ddict = {current_sdir: least_common_multiple}
        else:
            ddict = {self.current['slice_dims'][0]: self.current[mft],
                     self.next['slice_dims'][0]: self.next[mft]}
        return ddict

    def __get_shape(self, shape, ddict):
        """ Get shape taking into account padding. """
        shape = [shape[s] for s in ddict['slice_dims']]
        if 'transfer_shape' not in list(ddict.keys()):
            return shape[0], np.prod(shape)
        size_list = [ddict['transfer_shape'][s] for s in ddict['slice_dims']]
        trans_per_dim = np.ceil(np.array(shape)/np.array(
                size_list, dtype=np.float32))
        full_shape = np.prod(trans_per_dim*size_list)
        return shape[0], full_shape

    def __max_frames_per_process(self, shape, nFrames, allslices=None):
        """
        Calculate the max possible frames per process
        """
        nSlices = allslices if allslices else shape
        total_plugin_runs = np.ceil(float(nSlices) / nFrames)
        frame_list = np.arange(total_plugin_runs)
        nProcs = len(self.exp.meta_data.get('processes'))
        frame_list_per_proc = np.array_split(frame_list, nProcs)
        flist_len = [len(f) for f in frame_list_per_proc if len(f) > 0]
        runs_per_proc = int(np.median(np.array(flist_len)))
        return int(min(runs_per_proc*nFrames, shape))

    def __adjust_chunk_size(self, chunks, ttype, shape, adjust):
        """
        Adjust the chunk size to as close to 1MB as possible
        """
        chunks = np.array(chunks)
        chunk_size = np.prod(chunks)*np.dtype(ttype).itemsize
        cache_size = self.chunk_max
        if (chunk_size > cache_size):
            self.__decrease_chunks(chunks, ttype, adjust)
        else:
            chunks = self.__increase_chunks(chunks, ttype, shape, adjust)
        return tuple(chunks)

    def __decrease_chunks(self, chunks, ttype, adjust):
        """
        Decrease the chunk size to below but as close to 1MB as possible
        """
        while ((np.prod(chunks)*np.dtype(ttype).itemsize) > self.chunk_max):
            idx = self.__get_idx_decrease(chunks, adjust)
            dim = adjust['dim'].index(idx)
#            if idx == -1:
#                break
            chunks[idx] = int(np.ceil(eval(str(float(chunks[idx])) +
                              adjust['inc']['down'][dim])))

    def __increase_chunks(self, chunks, ttype, shape, adjust):
        """
        Increase the chunk size as close to 1MB as possible
        """
        next_chunks = copy.copy(chunks)
        while ((np.prod(next_chunks)*np.dtype(ttype).itemsize) <=
                self.chunk_max):
            chunks = copy.copy(next_chunks)
            idx = self.__get_idx_increase(next_chunks, adjust)
            if idx == -1:
                break
            dim = adjust['dim'].index(idx)
            next_chunks[idx] = \
                eval(str(next_chunks[idx]) + adjust['inc']['up'][dim])
        return chunks

    def __get_idx_decrease(self, chunks, adjust):
        """
        Determine the chunk dimension to decrease
        """
        self.check = lambda a, b, c, i: \
            True if (eval(str(a) + b[i])) < c['min'][i] else False
        self.__check_adjust_dims(adjust, chunks, 'down')
        return self.__get_idx_order(adjust, chunks, 'down')

    def __get_idx_increase(self, chunks, adjust):
        """
        Determine the chunk dimension to increase
        """
        self.check = lambda a, b, c, i: \
            True if (eval(str(a) + b[i])) > c['max'][i] else False
        self.__check_adjust_dims(adjust, chunks, 'up')
        return self.__get_idx_order(adjust, chunks, 'up')

    def __get_idx_order(self, adjust, chunks, direction):
        process_order = [self.slice1, self.core]
        sl = slice(None, None, -1)
        if direction == 'up':
            sl = slice(None, None, 1)
            process_order = process_order[::-1]

        avail = list(set(adjust['dim']).intersection(process_order[0]))
        idx_order = np.argsort(chunks[avail])[sl]

        if not idx_order.size:
            avail = list(set(adjust['dim']).intersection(process_order[1]))
            idx_order = np.argsort(chunks[avail])[sl]

        return avail[idx_order[0]] if idx_order.size else -1

    def __check_adjust_dims(self, adjust, chunks, up_down):
        nDel = 0
        for i in range(len(adjust['dim'])):
            i -= nDel
            dim = adjust['dim'][i]
#            if self.check(chunks[dim], adjust['inc'][up_down],
#                          adjust['bounds'], i):
#                adjust['inc']['down'][i] = '-1'
            if self.check(chunks[dim], adjust['inc'][up_down],
                          adjust['bounds'], i):
                del adjust['dim'][i]
                del adjust['inc']['up'][i]
                del adjust['inc']['down'][i]
                del adjust['bounds']['max'][i]
                del adjust['bounds']['min'][i]
                nDel += 1
