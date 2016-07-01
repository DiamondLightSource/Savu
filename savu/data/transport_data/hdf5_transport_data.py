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
.. module:: hdf5_transport_data
   :platform: Unix
   :synopsis: A data transport class that is inherited by Data class at \
   runtime. It performs the movement of the data, including loading and saving.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""
import os
import h5py
import logging
import copy
import numpy as np

import savu.plugins.utils as pu
from savu.data.data_structures.data_add_ons import Padding

NX_CLASS = 'NX_class'


class Hdf5TransportData(object):
    """
    The Hdf5TransportData class performs the loading and saving of data
    specific to a hdf5 transport mechanism.
    """

#    def __init__(self):
#        self.end_pad = True

    def _load_data(self, start):
        exp = self.exp
        n_loaders = exp.meta_data.plugin_list._get_n_loaders()
        plugin_list = exp.meta_data.plugin_list.plugin_list
        final_plugin = plugin_list[-1]
        saver_plugin = pu.plugin_loader(exp, final_plugin)

        logging.debug("generating all output files")
        out_data_objects = []
        count = start
        datasets_list = exp.meta_data.plugin_list._get_datasets_list()

        for plugin_dict in plugin_list[start:-1]:

            self._get_current_and_next_patterns(
                datasets_list[count-n_loaders:])
            plugin_id = plugin_dict["id"]
            logging.info("Loading plugin %s", plugin_id)
            plugin = pu.plugin_loader(exp, plugin_dict)
            plugin._revert_preview(plugin.get_in_datasets())
            self.__set_filenames(plugin, plugin_id, count)
            saver_plugin.setup()

            out_data_objects.append(exp.index["out_data"].copy())
            exp._merge_out_data_to_in()
            count += 1

        self.exp.meta_data.delete('current_and_next')
        return out_data_objects, count

    def __set_filenames(self, plugin, plugin_id, count):
        exp = self.exp
        expInfo = exp.meta_data
        nPlugins = \
            expInfo.plugin_list.n_plugins - expInfo.plugin_list.n_loaders - 1
        expInfo.set_meta_data("filename", {})
        expInfo.set_meta_data("group_name", {})
        for key in exp.index["out_data"].keys():
            name = key + '_p' + str(count) + '_' + \
                plugin_id.split('.')[-1] + '.h5'
            if count is nPlugins:
                out_path = expInfo.get_meta_data('out_path')
            else:
                out_path = expInfo.get_meta_data('inter_path')
            filename = os.path.join(out_path, name)
            group_name = "%i-%s-%s" % (count, plugin.name, key)
            exp._barrier()
            logging.debug("(set_filenames) Creating output file after "
                          " _barrier %s", filename)
            expInfo.set_meta_data(["filename", key], filename)
            expInfo.set_meta_data(["group_name", key], group_name)

    def __add_data_links(self, linkType):
        nxs_filename = self.exp.meta_data.get_meta_data('nxs_filename')
        logging.info("Adding link to file %s", nxs_filename)

        nxs_file = self.exp.nxs_file
        entry = nxs_file['entry']
        group_name = self.data_info.get_meta_data('group_name')
        self.__output_metadata(self.backing_file[group_name])
        filename = self.backing_file.filename.split('/')[-1]

        if linkType is 'final_result':
            name = 'final_result_' + self.get_name()
            entry[name] = \
                h5py.ExternalLink(filename, self.group_name)
        elif linkType is 'intermediate':
            name = self.group_name + '_' + self.data_info.get_meta_data('name')
            entry = entry.require_group('intermediate')
            entry.attrs['NX_class'] = 'NXcollection'
            entry[name] = \
                h5py.ExternalLink(filename, self.group_name)
        else:
            raise Exception("The link type is not known")

    def __output_metadata(self, entry):
        self.__output_axis_labels(entry)
        self.__output_data_patterns(entry)
        self.__output_metadata_dict(entry)

    def __output_axis_labels(self, entry):
        axis_labels = self.data_info.get_meta_data("axis_labels")
        axes = []
        count = 0
        for labels in axis_labels:
            name = labels.keys()[0]
            axes.append(name)
            entry.attrs[name + '_indices'] = count

            try:
                mData = self.meta_data.get_meta_data(name)
            except KeyError:
                mData = np.arange(self.get_shape()[count])

            if isinstance(mData, list):
                mData = np.array(mData)

            temp = self.group.create_dataset(name, mData.shape, mData.dtype)
            temp[...] = mData[...]
            temp.attrs['units'] = labels.values()[0]
            count += 1
        entry.attrs['axes'] = axes

    def __output_data_patterns(self, entry):
        data_patterns = self.data_info.get_meta_data("data_patterns")
        entry = entry.create_group('patterns')
        entry.attrs['NX_class'] = 'NXcollection'
        for pattern in data_patterns:
            nx_data = entry.create_group(pattern)
            nx_data.attrs[NX_CLASS] = 'NXparameters'
            values = data_patterns[pattern]
            nx_data.create_dataset('core_dir', data=values['core_dir'])
            nx_data.create_dataset('slice_dir', data=values['slice_dir'])

    def __output_metadata_dict(self, entry):
        meta_data = self.meta_data.get_dictionary()
        entry = entry.create_group('meta_data')
        entry.attrs['NX_class'] = 'NXcollection'
        for mData in meta_data:
            nx_data = entry.create_group(mData)
            nx_data.attrs[NX_CLASS] = 'NXdata'
            nx_data.create_dataset(mData, data=meta_data[mData])

    def _save_data(self, link_type):
        self.__add_data_links(link_type)
        logging.info('save_data _barrier')
        self.exp._barrier()

    def _close_file(self):
        """
        Closes the backing file and completes work
        """
        self.exp._barrier()
        logging.debug("Completing file %s", self.backing_file.filename)
        self.backing_file.close()
        self.backing_file = None

    def __chunk_length_repeat(self, slice_dirs, shape):
        """
        For each slice dimension, determine 3 values relevant to the slicing.

        :returns: chunk, length, repeat
            chunk: how many repeats of the same index value before an increment
            length: the slice dimension length (sequence length)
            repeat: how many times does the sequence of chunked numbers repeat
        :rtype: [int, int, int]
        """
        sshape = self.__get_shape_of_slice_dirs(slice_dirs, shape)
        if not slice_dirs:
            return [1], [1], [1]

        chunk = []
        length = []
        repeat = []
        for dim in range(len(slice_dirs)):
            chunk.append(int(np.prod(sshape[0:dim])))
            length.append(sshape[dim])
            repeat.append(int(np.prod(sshape[dim+1:])))

        return chunk, length, repeat

    def __get_shape_of_slice_dirs(self, slice_dirs, shape):
        sshape = [shape[sslice] for sslice in slice_dirs]
        if 'var' in sshape:
            shape = list(shape)
            for index, value in enumerate(shape):
                if isinstance(value, str):
                    shape[index] = \
                        len(self.data_info.get_meta_data('axis_labels')[index])
            shape = tuple(shape)
            sshape = [shape[sslice] for sslice in slice_dirs]
        return sshape

    def __get_slice_dirs_index(self, slice_dirs, shape):
        """
        returns a list of arrays for each slice dimension, where each array
        gives the indices for that slice dimension.
        """
        # create the indexing array
        chunk, length, repeat = self.__chunk_length_repeat(slice_dirs, shape)
        idx_list = []
        for i in range(len(slice_dirs)):
            c = chunk[i]
            r = repeat[i]
            values = self.__get_slice_dir_index(slice_dirs[i])
            idx = np.ravel(np.kron(values, np.ones((r, c))))
            idx_list.append(idx.astype(int))
        return np.array(idx_list)

    def __get_slice_dir_index(self, dim, boolean=False):
        starts, stops, steps, chunks = \
            self.get_preview().get_starts_stops_steps()
        if chunks[dim] > 1:
            dir_idx = np.ravel(np.transpose(self._get_slice_dir_matrix(dim)))
            if boolean:
                return self.__get_bool_slice_dir_index(dim, dir_idx)
            return dir_idx
        else:
            fix_dirs, value = self._get_plugin_data()._get_fixed_directions()
            if dim in fix_dirs:
                return value[fix_dirs.index(dim)]
            else:
                return np.arange(starts[dim], stops[dim], steps[dim])

    def __get_bool_slice_dir_index(self, dim, dir_idx):
        shape = self.data_info.get_meta_data('orig_shape')[dim]
        bool_idx = np.ones(shape, dtype=bool)
        bool_idx[dir_idx] = True
        return bool_idx

    def _get_slice_dir_matrix(self, dim):
        starts, stops, steps, chunks = \
            self.get_preview().get_starts_stops_steps()
        chunk = chunks[dim]
        a = np.tile(np.arange(starts[dim], stops[dim], steps[dim]), (chunk, 1))
        b = np.transpose(np.tile(np.arange(chunk)-chunk/2, (a.shape[1], 1)))
        dim_idx = a + b
        if dim_idx[dim_idx < 0].size:
            raise Exception('Cannot have a negative value in the slice list.')
        return dim_idx

    def _single_slice_list(self):
        pData = self._get_plugin_data()
        slice_dirs = pData.get_slice_directions()
        core_dirs = np.array(pData.get_core_directions())
        shape = self.get_shape()
        index = self.__get_slice_dirs_index(slice_dirs, shape)
        fix_dirs, value = pData._get_fixed_directions()

        nSlices = index.shape[1] if index.size else len(fix_dirs)
        nDims = len(shape)
        core_slice = self.__get_core_slices(core_dirs)

        slice_list = []
        for i in range(nSlices):
            getitem = np.array([slice(None)]*nDims)
            getitem[core_dirs] = core_slice[np.arange(len(core_dirs))]
            for f in range(len(fix_dirs)):
                getitem[fix_dirs[f]] = slice(value[f], value[f] + 1, 1)
            for sdir in range(len(slice_dirs)):
                getitem[slice_dirs[sdir]] = slice(index[sdir, i],
                                                  index[sdir, i] + 1, 1)
            slice_list.append(tuple(getitem))

        slice_list = self.__remove_var_length_dimension(slice_list)
        return slice_list

    def __get_core_slices(self, core_dirs):
        core_slice = []
        starts, stops, steps, chunks = \
            self.get_preview().get_starts_stops_steps()
        for c in core_dirs:
            if (chunks[c]) > 1:
                if (stops[c] - starts[c] == 1):
                    start = starts[c] - int(chunks[c]/2)
                    if start < 0:
                        raise Exception('Cannot have a negative value in the '
                                        'slice list.')
                    stop = starts[c] + (chunks[c] - int(chunks[c]/2))
                    core_slice.append(slice(start, stop, 1))
                else:
                    raise Exception("The core dimension does not support "
                                    "multiple chunks.")
            else:
                core_slice.append(slice(starts[c], stops[c], steps[c]))
        return np.array(core_slice)

    def __remove_var_length_dimension(self, slice_list):
        shape = self.get_shape()
        if 'var' in shape:
            var_dim = list(shape).index('var')
            for i in range(len(slice_list)):
                sl = list(slice_list[i])
                del sl[var_dim]
                slice_list[i] = sl
        return slice_list

    def __banked_list(self, slice_list):
        shape = self.get_shape()
        slice_dirs = self._get_plugin_data().get_slice_directions()
        chunk, length, repeat = self.__chunk_length_repeat(slice_dirs, shape)
        banked = self.__split_list(slice_list, length[0])
        return banked, length, slice_dirs

    def __grouped_slice_list(self, slice_list, max_frames):
        banked, length, slice_dir = self.__banked_list(slice_list)
        starts, stops, steps, chunks = \
            self.get_preview().get_starts_stops_steps()
        group_dim = self._get_plugin_data().get_slice_directions()[0]

        grouped = []
        for group in banked:
            sub_groups = self.__split_list(group, max_frames)

            for sub in sub_groups:
                start = sub[0][group_dim].start
                stop = sub[-1][group_dim].stop
                step = steps[group_dim]
                working_slice = list(sub[0])
                working_slice[group_dim] = slice(start, stop, step)
                grouped.append(tuple(working_slice))
        return grouped

    def __split_list(self, the_list, size):
            return [the_list[x:x+size] for x in xrange(0, len(the_list), size)]

    def _get_grouped_slice_list(self):
        max_frames = self._get_plugin_data()._get_frame_chunk()
        max_frames = (1 if max_frames is None else max_frames)

        sl = self._single_slice_list()
        if sl is None:
            raise Exception("Data type", self.get_current_pattern_name(),
                            "does not support slicing in directions",
                            self.get_slice_directions())
        return self.__grouped_slice_list(sl, max_frames)

    def _get_slice_list_per_process(self, expInfo):
        processes = expInfo.get_meta_data("processes")
        process = expInfo.get_meta_data("process")
        self.__set_padding_dict()
        slice_list = self._get_grouped_slice_list()

        frame_index = np.arange(len(slice_list))
        try:
            frames = np.array_split(frame_index, len(processes))[process]
            process_slice_list = slice_list[frames[0]:frames[-1]+1]
        except IndexError:
            process_slice_list = []

        return process_slice_list

    def __calculate_slice_padding(self, in_slice, pad, data_stop, **kwargs):
        pad = [pad['before'], pad['after']]
        sl = in_slice
        if not type(sl) == slice:
            # turn the value into a slice and pad it
            sl = slice(sl, sl+1, 1)

        minval = sl.start-pad[0] if sl.start is not None else None
        maxval = sl.stop+pad[1] if sl.stop is not None else None

        minpad = pad[0] if minval is None else 0
        maxpad = pad[1] if maxval is None else 0
        if minval < 0:
            minpad = 0 - minval
            minval = 0
        if maxval > data_stop:
            maxpad = maxval - data_stop
            maxval = data_stop

        out_slice = slice(minval, maxval, sl.step)
        return (out_slice, (minpad, maxpad))

    def __get_pad_data(self, slice_tup, pad_tup):
        slice_list = []
        pad_list = []
        for i in range(len(slice_tup)):
            if type(slice_tup[i]) == slice:
                slice_list.append(slice_tup[i])
                pad_list.append(pad_tup[i])
            else:
                if pad_tup[i][0] == 0 and pad_tup[i][0] == 0:
                    slice_list.append(slice_tup[i])
                else:
                    slice_list.append(slice(slice_tup[i], slice_tup[i]+1, 1))
                    pad_list.append(pad_tup[i])

        data_slice = self.data[tuple(slice_list)]
        data_slice = np.pad(data_slice, tuple(pad_list), mode='edge')

        return data_slice

    def __set_padding_dict(self):
        pData = self._get_plugin_data()
        if pData.padding and not isinstance(pData.padding, Padding):
            pData.pad_dict = copy.deepcopy(pData.padding)
            pData.padding = Padding(pData.get_pattern())
            for key in pData.pad_dict.keys():
                getattr(pData.padding, key)(pData.pad_dict[key])

    def _get_padded_slice_data(self, input_slice_list):
        slice_list = list(input_slice_list)
        pData = self._get_plugin_data()

        if pData.fixed_dims is True:
            self.__matching_dims(pData, input_slice_list)

        if not pData.padding:
            return self.data[tuple(slice_list)]

        padding_dict = pData.padding._get_padding_directions()
        pad_list = []
        for i in range(len(slice_list)):
            pad_list.append((0, 0))

        shape = self.orig_shape if self.orig_shape else self.get_shape()
        for ddir in padding_dict.keys():
            pDict = padding_dict[ddir]
            slice_list[ddir], pad_list[ddir] = self.__calculate_slice_padding(
                slice_list[ddir], pDict, shape[ddir])

        if pData.end_pad is True:
            self.correct_pad(pData)
        return self.__get_pad_data(tuple(slice_list), tuple(pad_list))

    def __matching_dims(self, pData, slice_list):
        """ Ensure each chunk of frames passed to the plugin has the same \
        (max_frames) size.
        """
        pData.end_pad = True
        slice_dir = pData.get_slice_directions()[0]
        sl = slice_list[slice_dir]
        max_frames = self._get_plugin_data()._get_frame_chunk()
        diff = max_frames - len(range(sl.start, sl.stop, sl.step))
        if diff:
            if not pData.padding:
                pData.padding = Padding(pData.get_pattern())
            pad_str = str(slice_dir)+'.after.'+str(diff)
            pData.padding._pad_direction(pad_str)

    def _get_unpadded_slice_data(self, input_slice_list, padded_data):
        pData = self._get_plugin_data()

        if pData.fixed_dims is True:
            self.__matching_dims(pData, input_slice_list)

        if not pData.padding:
            return padded_data

        padding_dict = pData.padding._get_padding_directions()
        new_slice = [slice(None)]*len(self.get_shape())
        for ddir in padding_dict.keys():
            end = padded_data.shape[ddir] if padding_dict[ddir]['after'] is 0\
                else -padding_dict[ddir]['after']
            new_slice[ddir] = slice(padding_dict[ddir]['before'], end, 1)

        if pData.end_pad is True:
            self.correct_pad(pData)
        return padded_data[tuple(new_slice)]

    def correct_pad(self, pData):
        if pData.pad_dict:
            pData.padding = pData.pad_dict
            self.__set_padding_dict()
        else:
            pData.padding = None
        pData.end_pad = False
