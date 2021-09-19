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
.. module:: base_tomophantom_loader
   :platform: Unix
   :synopsis: A loader that generates synthetic 3D projection full-field tomo data\
        as hdf5 dataset of any size.

.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""

import os
import h5py
import logging
import numpy as np

from savu.data.chunking import Chunking
from savu.plugins.utils import register_plugin
from savu.plugins.loaders.base_loader import BaseLoader
from savu.plugins.savers.utils.hdf5_utils import Hdf5Utils

import tomophantom
from tomophantom import TomoP2D, TomoP3D

@register_plugin
class BaseTomophantomLoader(BaseLoader):
    def __init__(self, name='BaseTomophantomLoader'):
        super(BaseTomophantomLoader, self).__init__(name)

    def setup(self):
        exp = self.exp
        data_obj = exp.create_data_object('in_data', 'synth_proj_data')

        data_obj.set_axis_labels(*self.parameters['axis_labels'])
        self.__convert_patterns(data_obj,'synth_proj_data')
        self.__parameter_checks(data_obj)

        self.tomo_model = self.parameters['tomo_model']
        # setting angles for parallel beam geometry
        self.angles = np.linspace(0.0,180.0-(1e-14), self.parameters['proj_data_dims'][0], dtype='float32')
        path = os.path.dirname(tomophantom.__file__)
        self.path_library3D = os.path.join(path, "Phantom3DLibrary.dat")

        data_obj.backing_file = self.__get_backing_file(data_obj, 'synth_proj_data')
        data_obj.data = data_obj.backing_file['/']['test']
        #data_obj.data.dtype # Need to do something to .data to keep the file open!

        # create a phantom file
        data_obj2 = exp.create_data_object('in_data', 'phantom')

        data_obj2.set_axis_labels(*self.parameters['axis_labels_phantom'])
        self.__convert_patterns(data_obj2, 'phantom')
        self.__parameter_checks(data_obj2)

        data_obj2.backing_file = self.__get_backing_file(data_obj2, 'phantom')
        data_obj2.data = data_obj2.backing_file['/']['test']
        #data_obj2.data.dtype # Need to do something to .data to keep the file open!

        data_obj.set_shape(data_obj.data.shape)
        self.n_entries = data_obj.get_shape()[0]
        cor_val=0.5*(self.parameters['proj_data_dims'][2])
        self.cor=np.linspace(cor_val, cor_val, self.parameters['proj_data_dims'][1], dtype='float32')
        self._set_metadata(data_obj, self._get_n_entries())
        return data_obj,data_obj2

    def __get_backing_file(self, data_obj, file_name):
        fname = '%s/%s.h5' % \
            (self.exp.get('out_path'), file_name)

        if os.path.exists(fname):
            return h5py.File(fname, 'r')

        self.hdf5 = Hdf5Utils(self.exp)

        dims_temp = self.parameters['proj_data_dims'].copy()
        proj_data_dims = tuple(dims_temp)
        if (file_name == 'phantom'):
            dims_temp[0]=dims_temp[1]
            dims_temp[2]=dims_temp[1]
            proj_data_dims = tuple(dims_temp)

        patterns = data_obj.get_data_patterns()
        p_name = list(patterns.keys())[0]
        p_dict = patterns[p_name]
        p_dict['max_frames_transfer'] = 1
        nnext = {p_name: p_dict}

        pattern_idx = {'current': nnext, 'next': nnext}
        chunking = Chunking(self.exp, pattern_idx)
        chunks = chunking._calculate_chunking(proj_data_dims, np.int16)

        h5file = self.hdf5._open_backing_h5(fname, 'w')
        dset = h5file.create_dataset('test', proj_data_dims, chunks=chunks)

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
            if (file_name == 'synth_proj_data'):
                #generate projection data
                gen_data = TomoP3D.ModelSinoSub(self.tomo_model, proj_data_dims[1], proj_data_dims[2], proj_data_dims[1], (i, i+1), -self.angles, self.path_library3D)
            else:
                #generate phantom data
                gen_data = TomoP3D.ModelSub(self.tomo_model, proj_data_dims[1], (i, i+1), self.path_library3D)
            dset[tuple(sl)] = np.swapaxes(gen_data,0,1)
            if sl[slice_dirs[idx]].stop == dset.shape[slice_dirs[idx]]:
                idx += 1
                if idx == len(slice_dirs):
                    break
            tmp = sl[slice_dirs[idx]]
            sl[slice_dirs[idx]] = slice(tmp.start+1, tmp.stop+1)

        self.exp._barrier()

        try:
            h5file.close()
        except IOError as exc:
            logging.debug('There was a problem trying to close the file in random_hdf5_loader')

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

    def __convert_patterns(self, data_obj, object_type):
        if (object_type == 'synth_proj_data'):
            pattern_list = self.parameters['patterns']
        else:
            pattern_list = self.parameters['patterns_tomo']
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

    def _set_metadata(self, data_obj, n_entries):
        n_angles = len(self.angles)
        data_angles = n_entries
        if data_angles != n_angles:
            raise Exception("The number of angles %s does not match the data "
                            "dimension length %s", n_angles, data_angles)
        data_obj.meta_data.set("rotation_angle", self.angles)
        data_obj.meta_data.set("centre_of_rotation", self.cor)

    def __parameter_checks(self, data_obj):
        if not self.parameters['proj_data_dims']:
            raise Exception(
                    'Please specifiy the dimensions of the dataset to create.')

    def _get_n_entries(self):
        return self.n_entries
