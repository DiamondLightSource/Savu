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
import numpy as np

import savu.plugins.utils as pu
from savu.data.data_structures.data_add_ons import Padding

NX_CLASS = 'NX_class'


class Hdf5TransportData(object):
    """
    The Hdf5TransportData class performs the loading and saving of data
    specific to a hdf5 transport mechanism.
    """

    def __init__(self):
        self.backing_file = None

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
        expInfo.set_meta_data("filename", {})
        expInfo.set_meta_data("group_name", {})
        for key in exp.index["out_data"].keys():
            filename = \
                os.path.join(expInfo.get_meta_data("out_path"), "%s%02i_%s"
                             % (os.path.basename(
                                expInfo.get_meta_data("process_file")),
                                count, plugin_id))
            filename = filename + "_" + key + ".h5"
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

        if linkType is 'final_result':
            name = 'final_result_' + self.get_name()
            entry[name] = \
                h5py.ExternalLink(self.backing_file.filename, self.group_name)
        elif linkType is 'intermediate':
            name = self.group_name + '_' + self.data_info.get_meta_data('name')
            entry = entry.require_group('intermediate')
            entry.attrs['NX_class'] = 'NXcollection'
            entry[name] = \
                h5py.ExternalLink(self.backing_file.filename, self.group_name)
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
        if self.backing_file is not None:
            try:
                logging.debug("Completing file %s", self.backing_file.filename)
                self.backing_file.close()
                self.backing_file = None
            except:
                pass

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

        if self.mapping:
            map_obj = self.exp.index['mapping'][self.get_name()]
            new_length = map_obj.data_info.get_meta_data('map_dim_len')

        length = new_length if self.mapping else length[0]
        banked = self.__split_list(slice_list, length)
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

        if self._get_plugin_data().selected_data is True:
            sl = self.get_tomo_raw()._get_frame_raw(sl)

        if sl is None:
            raise Exception("Data type", self.get_current_pattern_name(),
                            "does not support slicing in directions",
                            self.get_slice_directions())
        return self.__grouped_slice_list(sl, max_frames)

    def _get_slice_list_per_process(self, expInfo):
        processes = expInfo.get_meta_data("processes")
        process = expInfo.get_meta_data("process")
        slice_list = self._get_grouped_slice_list()

        frame_index = np.arange(len(slice_list))
        try:
            frames = np.array_split(frame_index, len(processes))[process]
            process_slice_list = slice_list[frames[0]:frames[-1]+1]
        except IndexError:
            process_slice_list = []

        return process_slice_list

    def __calculate_slice_padding(self, in_slice, pad_ammount, data_stop):
        sl = in_slice

        if not type(sl) == slice:
            # turn the value into a slice and pad it
            sl = slice(sl, sl+1, 1)

        minval = None
        maxval = None

        if sl.start is not None:
            minval = sl.start-pad_ammount
        if sl.stop is not None:
            maxval = sl.stop+pad_ammount

        minpad = 0
        maxpad = 0
        if minval is None:
            minpad = pad_ammount
        elif minval < 0:
            minpad = 0 - minval
            minval = 0
        if maxval is None:
            maxpad = pad_ammount
        if maxval > data_stop:
            maxpad = (maxval-data_stop)
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

    def __get_padding_dict(self):
        pData = self._get_plugin_data()
        padding = Padding(pData.get_pattern())
        for key in pData.padding.keys():
            getattr(padding, key)(pData.padding[key])
        return padding._get_padding_directions()

    def _get_padded_slice_data(self, input_slice_list):
        slice_list = list(input_slice_list)
        pData = self._get_plugin_data()
        if pData.padding is None:
            return self.data[tuple(slice_list)]

        padding_dict = self.__get_padding_dict()
        pad_list = []
        for i in range(len(slice_list)):
            pad_list.append((0, 0))

        for direction in padding_dict.keys():
            slice_list[direction], pad_list[direction] = \
                self.__calculate_slice_padding(slice_list[direction],
                                               padding_dict[direction],
                                               self.get_shape()[direction])

        temp = self.__get_pad_data(tuple(slice_list), tuple(pad_list))
        return temp

    def _get_unpadded_slice_data(self, input_slice_list, padded_dataset):
        padding_dict = self._get_plugin_data().padding
        if padding_dict is None:
            return padded_dataset

        padding_dict = self.__get_padding_dict()

        slice_list = list(input_slice_list)
        pad_list = []
        expand_list = []

        for i in range(len(slice_list)):
            pad_list.append((0, 0))
            expand_list.append(0)

        for direction in padding_dict.keys():
            slice_list[direction], pad_list[direction] = \
                self.__calculate_slice_padding(slice_list[direction],
                                               padding_dict[direction],
                                               padded_dataset.shape[direction])
            expand_list[direction] = padding_dict[direction]

        slice_list_2 = []
        for i in range(len(padded_dataset.shape)):
            start = None
            stop = None
            if expand_list[i] > 0:
                start = expand_list[i]
                stop = -expand_list[i]
            sl = slice(start, stop, None)
            slice_list_2.append(sl)

        return padded_dataset[tuple(slice_list_2)]
