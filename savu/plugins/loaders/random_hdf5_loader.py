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
import copy
import h5py
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
    """

    def __init__(self, name='RandomHdf5Loader'):
        super(RandomHdf5Loader, self).__init__(name)

    def setup(self):
        exp = self.exp
        data_obj = exp.create_data_object('in_data',
                                          self.parameters['dataset_name'])

        data_obj.set_axis_labels(*self.parameters['axis_labels'])
        self.__convert_patterns(data_obj)

        data_obj.backing_file = self.__get_backing_file(data_obj)
        data_obj.data = data_obj.backing_file['/']['test']

        data_obj.set_shape(data_obj.data.shape)
        self.__set_rotation_angles(data_obj)
        self.set_data_reduction_params(data_obj)

    def __get_backing_file(self, data_obj):
        fname = '%s/%s.h5' % \
            (self.exp.get('out_path'), self.parameters['file_name'])

        if os.path.exists(fname):
            f = h5py.File(fname, 'r')
            return f

        self.hdf5 = Hdf5Utils(self.exp)

        size = tuple(self.parameters['size'])

        patterns = data_obj.get_data_patterns()
        p_name = self.parameters['pattern'] if self.parameters['pattern'] is \
            not None else patterns.keys()[0]
        p_name = patterns.keys()[0]
        p_dict = patterns[p_name]
        p_dict['max_frames_transfer'] = 1
        nnext = {p_name: p_dict}

        pattern_idx = {'current': nnext, 'next': nnext}
        chunking = Chunking(self.exp, pattern_idx)
        chunks = chunking._calculate_chunking(size, np.int16)

        h5file = self.hdf5._open_backing_h5(fname, 'w')
        dset = h5file.create_dataset('test', size, chunks=chunks)

        slice_dirs = nnext.values()[0]['slice_dir']
        nDims = len(dset.shape)
        total_frames = np.prod([dset.shape[i] for i in slice_dirs])
        sub_size = \
            [1 if i in slice_dirs else dset.shape[i] for i in range(nDims)]

        idx = 0
        sl = [slice(0, 1) if i in slice_dirs else slice(None)
              for i in range(nDims)]
        for i in range(total_frames):
            dset[tuple(sl)] = np.random.randint(
                1, high=10, size=sub_size, dtype=self.parameters['dtype'])
            if sl[slice_dirs[idx]].stop == dset.shape[slice_dirs[idx]]:
                idx += 1
                if idx == len(slice_dirs):
                    break
            tmp = sl[slice_dirs[idx]]
            sl[slice_dirs[idx]] = slice(tmp.start+1, tmp.stop+1)

        h5file.close()
        return self.hdf5._open_backing_h5(fname, 'r')
        # create an image key as well? # add this as an extension for 3D full-field tomography data        

    def __convert_patterns(self, data_obj):
        pattern_list = self.parameters['patterns']
        for p in pattern_list:
            p_split = p.split('.')
            name = p_split[0]
            dims = p_split[1:]
            core_dir = tuple([int(i[0]) for i in [d.split('c') for d in dims]
                              if len(i) == 2])
            slice_dir = tuple([int(i[0]) for i in [d.split('s') for d in dims]
                               if len(i) == 2])
            data_obj.add_pattern(name, core_dir=core_dir, slice_dir=slice_dir)

    def __set_rotation_angles(self, data_obj):
        angles = self.parameters['angles']

        if angles is None:
            angles = np.linspace(0, 180, data_obj.get_shape()[0])
        else:
            try:
                exec("angles = " + angles)
            except:
                try:
                    angles = np.loadtxt(angles)
                except:
                    raise Exception('Cannot set angles in loader.')

        n_angles = len(angles)
        data_angles = data_obj.get_shape()[0]
        if data_angles != n_angles:
            raise Exception("The number of angles %s does not match the data "
                            "dimension length %s", n_angles, data_angles)
        data_obj.meta_data.set("rotation_angle", angles)
