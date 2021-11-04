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

from savu.data.meta_data import MetaData
from savu.core.transports.base_transport import BaseTransport

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
        data_obj.data = data_obj.backing_file['/']['entry1']['tomo_entry']['data']['data']
        #data_obj.data.dtype # Need to do something to .data to keep the file open!

        # create a phantom file
        data_obj2 = exp.create_data_object('in_data', 'phantom')
        data_obj2.set_axis_labels(*['voxel_x.voxel', 'voxel_y.voxel', 'voxel_z.voxel'])
        self.__convert_patterns(data_obj2, 'phantom')
        self.__parameter_checks(data_obj2)

        data_obj2.backing_file = self.__get_backing_file(data_obj2, 'phantom')
        data_obj2.data = data_obj2.backing_file['/']['phantom']['data']
        #data_obj2.data.dtype # Need to do something to .data to keep the file open!
        data_obj.set_shape(data_obj.data.shape)
        group_name = '1-TomoPhantomLoader-phantom'

        self.n_entries = data_obj.get_shape()[0]
        cor_val=0.5*(self.parameters['proj_data_dims'][2])
        self.cor=np.linspace(cor_val, cor_val, self.parameters['proj_data_dims'][1], dtype='float32')
        self._set_metadata(data_obj, self._get_n_entries())

        self._link_nexus_file(data_obj, 'synth_proj_data')
        self._link_nexus_file(data_obj2, 'phantom')
        return data_obj, data_obj2

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

        if file_name == 'phantom':
            group = h5file.create_group('/phantom', track_order=None)
        else:
            group = h5file.create_group('/entry1/tomo_entry/data', track_order=None)

        dset = self.hdf5.create_dataset_nofill(group, "data", proj_data_dims, data_obj.dtype, chunks = chunks)

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
            #nxsfile = NXdata(h5file)
            #nxsfile.save(file_name + ".nxs")

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
        data_obj.meta_data.set(['rotation_angle'], self.angles)
        data_obj.meta_data.set(['centre_of_rotation'], self.cor)

    def __parameter_checks(self, data_obj):
        if not self.parameters['proj_data_dims']:
            raise Exception(
                    'Please specifiy the dimensions of the dataset to create.')

    def _get_n_entries(self):
        return self.n_entries

    def _link_nexus_file(self, data_obj, name):
        filename = self.exp.meta_data.get('nxs_filename')
        fsplit = filename.split('/')
        plugin_number = len(self.exp.meta_data.plugin_list.plugin_list)
        if plugin_number == 1:
            fsplit[-1] = 'synthetic_data.nxs'
        else:
            fsplit[-1] = 'synthetic_data_processed.nxs'
        filename = '/'.join(fsplit)
        self.exp.meta_data.set('nxs_filename', filename)
        if name == 'phantom':
            data_obj.exp.meta_data.set(['group_name', 'phantom'], 'phantom')
            data_obj.exp.meta_data.set(['link_type', 'phantom'], 'final_result')
            data_obj.meta_data.set(["meta_data", "PLACEHOLDER", "VOLUME_XZ"], [10])

        else:
            data_obj.exp.meta_data.set(['group_name', 'synth_proj_data'], 'entry1/tomo_entry/data')
            data_obj.exp.meta_data.set(['link_type', 'synth_proj_data'], 'entry1')

        self._populate_nexus_file(data_obj)
        self._link_datafile_to_nexus_file(data_obj)


    def _populate_nexus_file(self, data):
        filename = self.exp.meta_data.get('nxs_filename')
        name = data.data_info.get('name')
        with h5py.File(filename, 'a') as nxs_file:

            group_name = self.exp.meta_data.get(['group_name', name])
            link_type = self.exp.meta_data.get(['link_type', name])

            if name == 'phantom':
                nxs_entry = nxs_file.create_group('entry')
                if link_type == 'final_result':
                    group_name = 'final_result_' + data.get_name()
                else:
                    link = nxs_entry.require_group(link_type.encode("ascii"))
                    link.attrs['NX_class'] = 'NXcollection'
                    nxs_entry = link

                # delete the group if it already exists
                if group_name in nxs_entry:
                    del nxs_entry[group_name]

                plugin_entry = nxs_entry.require_group(group_name)

            else:
                plugin_entry = nxs_file.create_group(f'/{group_name}')

            self.__output_data_patterns(data, plugin_entry)
            self._output_metadata_dict(plugin_entry, data.meta_data.get_dictionary())
            self.__output_axis_labels(data, plugin_entry)


            plugin_entry.attrs['NX_class'] = 'NXdata'


    def __output_axis_labels(self, data, entry):
        axis_labels = data.data_info.get("axis_labels")
        ddict = data.meta_data.get_dictionary()

        axes = []
        count = 0
        for labels in axis_labels:
            name = list(labels.keys())[0]
            axes.append(name)
            entry.attrs[name + '_indices'] = count

            mData = ddict[name] if name in list(ddict.keys()) \
                else np.arange(self.parameters['proj_data_dims'][count])
            if isinstance(mData, list):
                mData = np.array(mData)

            if 'U' in str(mData.dtype):
                mData = mData.astype(np.string_)
            if name not in list(entry.keys()):
                axis_entry = entry.require_dataset(name, mData.shape, mData.dtype)
                axis_entry[...] = mData[...]
                axis_entry.attrs['units'] = list(labels.values())[0]
            count += 1
        entry.attrs['axes'] = axes

    def __output_data_patterns(self, data, entry):
        data_patterns = data.data_info.get("data_patterns")
        entry = entry.require_group('patterns')
        entry.attrs['NX_class'] = 'NXcollection'
        for pattern in data_patterns:
            nx_data = entry.require_group(pattern)
            nx_data.attrs['NX_class'] = 'NXparameters'
            values = data_patterns[pattern]
            self.__output_data(nx_data, values['core_dims'], 'core_dims')
            self.__output_data(nx_data, values['slice_dims'], 'slice_dims')

    def _output_metadata_dict(self, entry, mData):
        entry.attrs['NX_class'] = 'NXcollection'
        for key, value in mData.items():
            if key != 'rotation_angle':
                nx_data = entry.require_group(key)
                if isinstance(value, dict):
                    self._output_metadata_dict(nx_data, value)
                else:
                    nx_data.attrs['NX_class'] = 'NXdata'
                    self.__output_data(nx_data, value, key)

    def __output_data(self, entry, data, name):
        if isinstance(data, dict):
            entry = entry.require_group(name)
            entry.attrs['NX_class'] = 'NXcollection'
            for key, value in data.items():
                self.__output_data(entry, value, key)
        else:
            try:
                self.__create_dataset(entry, name, data)
            except Exception:
                try:
                    import json
                    data = np.array([json.dumps(data).encode("ascii")])
                    self.__create_dataset(entry, name, data)
                except Exception:
                    try:
                        self.__create_dataset(entry, name, data)
                    except:
                        raise Exception('Unable to output %s to file.' % name)

    def __create_dataset(self, entry, name, data):
        if name not in list(entry.keys()):
            entry.create_dataset(name, data=data)
        else:
            entry[name][...] = data

    def _link_datafile_to_nexus_file(self, data):
        filename = self.exp.meta_data.get('nxs_filename')

        with h5py.File(filename, 'a') as nxs_file:
            # entry path in nexus file
            name = data.get_name()
            group_name = self.exp.meta_data.get(['group_name', name])
            link = self.exp.meta_data.get(['link_type', name])
            name = data.get_name(orig=True)
            nxs_entry = self.__add_nxs_entry(nxs_file, link, group_name, name)
            self.__add_nxs_data(nxs_file, nxs_entry, link, group_name, data)

    def __add_nxs_entry(self, nxs_file, link, group_name, name):
        if name == 'phantom':
            nxs_entry = '/entry/' + link
        else:
            nxs_entry = ''
        nxs_entry += '_' + name if link == 'final_result' else "/" + group_name
        nxs_entry = nxs_file[nxs_entry]
        nxs_entry.attrs['signal'] = 'data'
        return nxs_entry

    def __add_nxs_data(self, nxs_file, nxs_entry, link, group_name, data):
        data_entry = nxs_entry.name + '/data'
        # output file path
        h5file = data.backing_file.filename

        if link == 'input_data':
            dataset = self.__is_h5dataset(data)
            if dataset:
                nxs_file[data_entry] = \
                    h5py.ExternalLink(os.path.abspath(h5file), dataset.name)
        else:
            # entry path in output file path
            m_data = self.exp.meta_data.get
            if not (link == 'intermediate' and
                    m_data('inter_path') != m_data('out_path')):
                h5file = h5file.split(m_data('out_folder') + '/')[-1]
            nxs_file[data_entry] = \
                h5py.ExternalLink(h5file, group_name + '/data')
