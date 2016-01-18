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

import numpy as np
from savu.plugins.utils import register_plugin

NX_CLASS = 'NX_class'


@register_plugin
class Chunking(object):
    """
    A class to save tomography data to a hdf5 file
    """

    def __init__(self, name='Chunking'):
        super(Chunking, self).__init__(name)

    def calculate_chunking(self, current_and_next, shape, ttype):
        print "shape = ", shape
        if len(shape) < 3:
            return True

        intersect_cores, remaining_cores = \
            self.separate_cores(current_and_next, shape)
        chunks = [1]*len(shape)
        adjust = [1]*len(shape)

        if 'VOLUME' in current_and_next['current'].keys()[0]:
            chunks, adjust = self.set_volume_chunks(shape, chunks, adjust)
        else:
            for dim in intersect_cores:
                chunks[dim] = shape[dim]
            for dim in remaining_cores:
                # require knowledge of all plugins using this dataset and their
                # max frames to set the number to replace 8.
                chunks[dim] = min(shape[dim], 8)

        if 0 in chunks:
            return True
        else:
            return self.adjust_chunk_size(chunks, ttype, shape, adjust)

    def adjust_chunk_size(self, chunks, ttype, shape, adjust):
        # increments e.g. (1, 1, self.plugin.get_max_frames)
        # max e.g. (shape, shape, n*self.get_max_frames)
        chunks = np.array(chunks)
        chunk_size = np.prod(chunks)*np.dtype(ttype).itemsize
        cache_size = 1000000
        if (chunk_size > cache_size):
            self.decrease_chunks(chunks, ttype, adjust)
        else:
            self.increase_chunks(chunks, ttype, shape, adjust)
        return tuple(chunks)

    def decrease_chunks(self, chunks, ttype):
        while ((np.prod(chunks)*np.dtype(ttype).itemsize) > 1000000):
            idx = np.argmax(chunks)
            chunks[idx] = chunks[idx]-1
        return chunks

    def increase_chunks(self, chunks, ttype, shape):
        next_chunks = chunks
        while (((np.prod(next_chunks)*np.dtype(ttype).itemsize) < 1000000)
                and not np.array_equal(chunks, np.array(shape))):
            chunks = copy.copy(next_chunks)
            idx = self.get_idx(next_chunks, shape)
            next_chunks[idx] = next_chunks[idx]+1
        return chunks

    def separate_cores(self, current_and_next, shape):
        current = current_and_next['current']
        current_cores = current[current.keys()[0]]['core_dir']
        nnext = current_and_next['next']

        next_cores = nnext[nnext.keys()[0]]['core_dir'] if nnext else \
            current_cores

        intersect = set(current_cores).intersection(set(next_cores))
        remaining = set(current_cores).difference(intersect).\
            union(set(next_cores).difference(intersect))
        return intersect, remaining

    def set_volume_chunks(self, shape, chunks, adjust):
        in_pData = self.plugin.get_plugin_in_datasets()[0]
        slice_dim = in_pData.get_pattern()['slice_dir'][0]
        for dim in range(3):
            chunks[dim] = min(shape[dim], 64)
        max_frames = self.plugin.get_max_frames()
        chunks[slice_dim] = min(shape[slice_dim], max_frames)
        adjust[slice_dim] = max_frames
        return chunks, adjust

    def get_idx(self, chunks, shape):
        idx_order = np.argsort(chunks)
        i = 0
        for i in range(len(shape)):
            if (chunks[idx_order[i]] < shape[idx_order[i]]):
                break

        return idx_order[i]
