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
.. module:: temp_loader
   :platform: Unix
   :synopsis: A loader that creates a random number generated hdf5 dataset of\
       any size.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import os
import h5py
import logging
import numpy as np

from savu.data.chunking import Chunking
from savu.plugins.utils import register_plugin
from savu.plugins.loaders.base_loader import BaseLoader
from savu.plugins.savers.utils.hdf5_utils import Hdf5Utils


@register_plugin
class RandomHdf5Loader(BaseLoader):
    """
    A hdf5 dataset of a specified size is created at runtime using numpy\
    random sampling (numpy.random) and saved to file. This created dataset\
    will be used as the input file, and the input file path passed to Savu\
    will be ignored (use a dummy).

    :u*param size: A list specifiying the required data size. Default: [].
    :u*param axis_labels: A list of the axis labels to be associated with each\
    dimension, of the form ['name1.unit1', 'name2.unit2',...]. Default: [].
    :u*param patterns: A list of data access patterns e.g.\
    [SINOGRAM.0c.1s.2c, PROJECTION.0s.1c.2s], where 'c' and 's' represent core\
    and slice dimensions respectively and every dimension must be\
    specified.  Default: [].
    :u*param file_name: Assign a name to the created h5\
    file. Default: 'input_array'.
    :param dtype: A numpy array data type.  Default: 'int16'.
    :param dataset_name: The name assigned to the dataset. Default: 'tomo'.
    :param angles: A python statement to be evaluated or a file - if the value\
    is None, values will be in the interval [0, 180]. Default: None.
    :param pattern: Pattern used to create and store the hdf5 dataset - \
    default is the first pattern in the pattern dictionary. Default: None.
    :param range: Set the distribution interval. Default: [1, 10].
    """

    def __init__(self, name='RandomHdf5Loader'):
        super(RandomHdf5Loader, self).__init__(name)

    def setup(self):
        exp = self.exp
        data_obj = exp.create_data_object('in_data',
                                          self.parameters['dataset_name'])

        data_obj.set_axis_labels(*self.parameters['axis_labels'])
        self.__convert_patterns(data_obj)
        self.__parameter_checks(data_obj)

        data_obj.backing_file = self.__get_backing_file(data_obj)
        data_obj.data = data_obj.backing_file['/']['test']
        data_obj.data.dtype # Need to do something to .data to keep the file open!

        data_obj.set_shape(data_obj.data.shape)
        self.n_entries = data_obj.get_shape()[0]
        self._set_rotation_angles(data_obj, self._get_n_entries())
        return data_obj

    def __get_backing_file(self, data_obj):
        fname = '%s/%s.h5' % \
            (self.exp.get('out_path'), self.parameters['file_name'])

        if os.path.exists(fname):
            return h5py.File(fname, 'r')

        self.hdf5 = Hdf5Utils(self.exp)

        size = tuple(self.parameters['size'])

        patterns = data_obj.get_data_patterns()
        p_name = patterns[self.parameters['pattern']] if \
            self.parameters['pattern'] is not None else list(patterns.keys())[0]
        p_name = list(patterns.keys())[0]
        p_dict = patterns[p_name]
        p_dict['max_frames_transfer'] = 1
        nnext = {p_name: p_dict}

        pattern_idx = {'current': nnext, 'next': nnext}
        chunking = Chunking(self.exp, pattern_idx)
        chunks = chunking._calculate_chunking(size, np.int16)

        h5file = self.hdf5._open_backing_h5(fname, 'w')
        dset = h5file.create_dataset('test', size, chunks=chunks)

        self.exp._barrier()

        slice_dirs = list(nnext.values())[0]['slice_dims']
        nDims = len(dset.shape)
        total_frames = np.prod([dset.shape[i] for i in slice_dirs])
        sub_size = \
            [1 if i in slice_dirs else dset.shape[i] for i in range(nDims)]

        # need an mpi barrier after creating the file before populating it
        idx = 0
        sl, total_frames = \
            self.__get_start_slice_list(slice_dirs, dset.shape, total_frames)
        # calculate the first slice
        for i in range(total_frames):
            low, high = self.parameters['range']
            dset[tuple(sl)] = np.random.randint(
                low, high=high, size=sub_size, dtype=self.parameters['dtype'])
            if sl[slice_dirs[idx]].stop == dset.shape[slice_dirs[idx]]:
                idx += 1
                if idx == len(slice_dirs):
                    break
            tmp = sl[slice_dirs[idx]]
            sl[slice_dirs[idx]] = slice(tmp.start+1, tmp.stop+1)

        self.exp._barrier()

#        try:
#            h5file.close()
#        except:
#            logging.debug('There was a problem trying to close the file in random_hdf5_loader')

        return self.hdf5._open_backing_h5(fname, 'r')

    def __get_start_slice_list(self, slice_dirs, shape, n_frames):
        n_processes = len(self.exp.get('processes'))
        rank = self.exp.get('process')
        frames = np.array_split(np.arange(n_frames), n_processes)[rank]
        f_range = list(range(0, frames[0])) if len(frames) else []
        sl = [slice(0, 1) if i in slice_dirs else slice(None)
              for i in range(len(shape))]
        idx = 0
        for i in f_range:
            if sl[slice_dirs[idx]] == shape[slice_dirs[idx]]-1:
                idx += 1
            tmp = sl[slice_dirs[idx]]
            sl[slice_dirs[idx]] = slice(tmp.start+1, tmp.stop+1)

        return sl, len(frames)

    def __convert_patterns(self, data_obj):
        pattern_list = self.parameters['patterns']
        for p in pattern_list:
            p_split = p.split('.')
            name = p_split[0]
            dims = p_split[1:]
            core_dims = tuple([int(i[0]) for i in [d.split('c') for d in dims]
                              if len(i) == 2])
            slice_dims = tuple([int(i[0]) for i in [d.split('s') for d in dims]
                               if len(i) == 2])
            data_obj.add_pattern(
                    name, core_dims=core_dims, slice_dims=slice_dims)

    def _set_rotation_angles(self, data_obj, n_entries):
        angles = self.parameters['angles']

        if angles is None:
            angles = np.linspace(0, 180, n_entries)
        else:
            try:
                exec("angles = " + angles)
            except:
                raise Exception('Cannot set angles in loader.')

        n_angles = len(angles)
        data_angles = n_entries
        if data_angles != n_angles:
            raise Exception("The number of angles %s does not match the data "
                            "dimension length %s", n_angles, data_angles)
        data_obj.meta_data.set("rotation_angle", angles)

    def __parameter_checks(self, data_obj):
        if not self.parameters['size']:
            raise Exception(
                    'Please specifiy the size of the dataset to create.')

    def _get_n_entries(self):
        return self.n_entries
