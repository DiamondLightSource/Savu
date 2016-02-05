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
   :synopsis: A data transport class that is inherited by Data class at
   runtime. It performs the movement of the data, including loading and saving.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""
import os
import logging
import h5py
import numpy as np

import savu.plugins.utils as pu
from savu.data.data_structures import Padding

NX_CLASS = 'NX_class'


class Hdf5TransportData(object):
    """
    The Hdf5TransportData class performs the loading and saving of data
    specific to a hdf5 transport mechanism.
    """

    def __init__(self):
        self.backing_file = None

    def load_data(self, start):
        exp = self.exp
        plugin_list = exp.meta_data.plugin_list.plugin_list
        final_plugin = plugin_list[-1]
        saver_plugin = pu.plugin_loader(exp, final_plugin)

        logging.debug("generating all output files")
        out_data_objects = []
        count = start
        datasets_list = pu.datasets_list

        for plugin_dict in plugin_list[start:-1]:

            self.get_current_and_next_patterns(datasets_list[count-1:])
            plugin_id = plugin_dict["id"]
            logging.info("Loading plugin %s", plugin_id)
            plugin = pu.plugin_loader(exp, plugin_dict)
            plugin.revert_preview(plugin.get_in_datasets())
            self.set_filenames(plugin, plugin_id, count)
            saver_plugin.setup()

            out_data_objects.append(exp.index["out_data"].copy())
            if self.variable_data_check(plugin):
                return out_data_objects, count
            exp.merge_out_data_to_in()
            count += 1

        del self.exp.meta_data.get_dictionary()['current_and_next']
        return out_data_objects, count

    def variable_data_check(self, plugin):
        out_datasets = plugin.get_out_datasets()
        flag = False
        for data in out_datasets:
            if data.get_variable_flag():
                flag = True
        return flag

    def set_filenames(self, plugin, plugin_id, count):
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
            exp.barrier()
            logging.debug("(set_filenames) Creating output file after "
                          " barrier %s", filename)
            expInfo.set_meta_data(["filename", key], filename)
            expInfo.set_meta_data(["group_name", key], group_name)

    def add_data_links(self, linkType):
        nxs_filename = self.exp.meta_data.get_meta_data('nxs_filename')
        logging.info("Adding link to file %s", nxs_filename)

        nxs_file = self.exp.nxs_file
        entry = nxs_file['entry']
        group_name = self.data_info.get_meta_data('group_name')
        self.output_metadata(self.backing_file[group_name])

        if linkType is 'final_result':
            name = 'final_result_' + self.get_name()
            entry[name] = self.external_link()

        elif linkType is 'intermediate':
            name = self.group_name + '_' + self.data_info.get_meta_data('name')
            entry = entry.require_group('intermediate')
            entry.attrs['NX_class'] = 'NXcollection'
            entry[name] = self.external_link()
        else:
            raise Exception("The link type is not known")

    def output_metadata(self, entry):
        logging.info("before outputting axis labels")
        self.output_axis_labels(entry)
        logging.info("after outputting axis labels")
        # output remaining metadata *** implement this

    def output_axis_labels(self, entry):
        axis_labels = self.data_info.get_meta_data("axis_labels")
        print "***********", axis_labels
        axes = []
        count = 0
        for labels in axis_labels:
            name = labels.keys()[0]
            axes.append(name)
            logging.info(name + '_indices')
            entry.attrs[name + '_indices'] = count

            try:
                mData = self.meta_data.get_meta_data(name)
            except KeyError:
                mData = np.arange(self.get_shape()[count])
            temp = self.group.create_dataset(name, mData.shape, mData.dtype)
            temp[...] = mData[...]
            count += 1
        entry.attrs['axes'] = axes

    def save_data(self, link_type):
        self.add_data_links(link_type)
        logging.info('save_data barrier')
        self.exp.barrier()

    def close_file(self):
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

    def chunk_length_repeat(self, slice_dirs, shape):
        """
        For each slice dimension, determine 3 values relevant to the slicing.

        :returns: chunk, length, repeat
            chunk: how many repeats of the same index value before an increment
            length: the slice dimension length (sequence length)
            repeat: how many times does the sequence of chunked numbers repeat
        :rtype: [int, int, int]
        """
        sshape = self.get_shape_of_slice_dirs(slice_dirs, shape)
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

    def get_shape_of_slice_dirs(self, slice_dirs, shape):
        sshape = [shape[sslice] for sslice in slice_dirs]
        if 'var' in sshape:
            shape = list(shape)
            for index, value in enumerate(shape):
                if isinstance(value, str):
                    shape[index] = \
                        len(self.data_info.get_meta_data('axis_labels')[index])
                    #self.unravel_array(index)
            shape = tuple(shape)
            sshape = [shape[sslice] for sslice in slice_dirs]
        return sshape

#    def unravel_array(self, index):
#        self.unravel = lambda x: self.unravel(x[0]) if isinstance(x, list) \
#            else x

    def get_slice_dirs_index(self, slice_dirs, shape):
        """
        returns a list of arrays for each slice dimension, where each array
        gives the indices for that slice dimension.
        """
        # create the indexing array
        chunk, length, repeat = self.chunk_length_repeat(slice_dirs, shape)
        idx_list = []
        for i in range(len(slice_dirs)):
            c = chunk[i]
            r = repeat[i]
            values = self.get_slice_dir_index(slice_dirs[i])
            idx = np.ravel(np.kron(values, np.ones((r, c))))
            idx_list.append(idx.astype(int))

        return np.array(idx_list)

    def get_slice_dir_index(self, dim, boolean=False):
        starts, stops, steps, chunks = self.get_starts_stops_steps()
        if chunks[dim] > 1:
            dir_idx = np.ravel(np.transpose(self.get_slice_dir_matrix(dim)))
            if boolean:
                return self.get_bool_slice_dir_index(dim, dir_idx)
            return dir_idx
        else:
            fix_dirs, value = self.get_plugin_data().get_fixed_directions()
            if dim in fix_dirs:
                return value[fix_dirs.index(dim)]
            else:
                return np.arange(starts[dim], stops[dim], steps[dim])

    def get_bool_slice_dir_index(self, dim, dir_idx):
        shape = self.data_info.get_meta_data('orig_shape')[dim]
        bool_idx = np.ones(shape, dtype=bool)
        bool_idx[dir_idx] = True
        return bool_idx

    def get_slice_dir_matrix(self, dim):
        starts, stops, steps, chunks = self.get_starts_stops_steps()
        if 'var' in stops:
            return np.array([0])
        chunk = chunks[dim]
        a = np.tile(np.arange(starts[dim], stops[dim], steps[dim]), (chunk, 1))
        b = np.transpose(np.tile(np.arange(chunk)-chunk/2, (a.shape[1], 1)))
        dim_idx = a + b
        if dim_idx[dim_idx < 0]:
            raise Exception('Cannot have a negative value in the slice list.')
        return dim_idx

    def single_slice_list(self):
        pData = self.get_plugin_data()
        slice_dirs = pData.get_slice_directions()
        core_dirs = np.array(pData.get_core_directions())
        shape = self.get_shape()
        index = self.get_slice_dirs_index(slice_dirs, shape)
#        if 'var' not in [shape[i] for i in slice_dirs]:
#            shape = [s for s in list(shape) if isinstance(s, int)]
        fix_dirs, value = pData.get_fixed_directions()
        nSlices = index.shape[1] if index.size else len(fix_dirs)
        nDims = len(shape)

        core_slice = self.get_core_slices(core_dirs)

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

        slice_list = self.remove_var_length_dimension(slice_list)
        return slice_list

    def get_core_slices(self, core_dirs):
        core_slice = []
        starts, stops, steps, chunks = self.get_starts_stops_steps()
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

    def remove_var_length_dimension(self, slice_list):
        shape = self.get_shape()
        if 'var' in shape:
            var_dim = list(shape).index('var')
            for i in range(len(slice_list)):
                sl = list(slice_list[i])
                del sl[var_dim]
                slice_list[i] = sl
        return slice_list

    def banked_list(self, slice_list):
        shape = self.get_shape()
        slice_dirs = self.get_plugin_data().get_slice_directions()
        chunk, length, repeat = self.chunk_length_repeat(slice_dirs, shape)

        if self.mapping:
            map_obj = self.exp.index['mapping'][self.get_name()]
            new_length = map_obj.data_info.get_meta_data('map_dim_len')

        repeat = length[0]/new_length if self.mapping else repeat[0]
        length = new_length if self.mapping else length[0]

        banked = []
        for rep in range(repeat):
            start = rep*length
            end = start + length
            banked.append(slice_list[start:end])

        return banked, length, slice_dirs

    def grouped_slice_list(self, slice_list, max_frames):
#         if isinstance(max_frames, tuple):
#             max_frames = max_frames[0] # aarons "fix"
        banked, length, slice_dir = self.banked_list(slice_list)
        starts, stops, steps, chunks = self.get_starts_stops_steps()
        group_dim = self.get_plugin_data().get_slice_directions()[0]
        chunk = chunks[group_dim]
        start = starts[group_dim]
        start = start if chunk == 1 else start-chunk/2
        step = steps[group_dim] if chunk == 1 else 1
        jump = max_frames*step

        if self.mapping:
            map_obj = self.exp.index['mapping'][self.get_name()]
            map_len = map_obj.data_info.get_meta_data('full_map_dim_len')[0]

        grouped = []
        for group in banked:
            full_frames = int((length)/max_frames)
            full_frames_end = start + full_frames*step*max_frames
            end = start+(len(group)-1)*step+1
            rem = 1 if (length % max_frames) else 0

            working_slice = list(group[0])
            i = start - jump
            for i in range(start, full_frames_end, jump):
                new_slice = slice(i, i+jump, step)
                working_slice[slice_dir[0]] = new_slice
                grouped.append(tuple(working_slice))
            if rem:
                new_slice = slice(i+jump, end, step)
                working_slice[slice_dir[0]] = new_slice
                grouped.append(tuple(working_slice))

            if self.mapping:
                start = start + map_len

        return grouped

    def get_grouped_slice_list(self):
        max_frames = self.get_plugin_data().get_frame_chunk()
        max_frames = (1 if max_frames is None else max_frames)

        sl = self.single_slice_list()

        if self.get_plugin_data().selected_data is True:
            sl = self.get_tomo_raw().get_frame_raw(sl)

        if sl is None:
            raise Exception("Data type", self.get_current_pattern_name(),
                            "does not support slicing in directions",
                            self.get_slice_directions())

        return self.grouped_slice_list(sl, max_frames)

    def get_slice_list_per_process(self, expInfo):
        processes = expInfo.get_meta_data("processes")
        process = expInfo.get_meta_data("process")
        slice_list = self.get_grouped_slice_list()

        frame_index = np.arange(len(slice_list))
        try:
            frames = np.array_split(frame_index, len(processes))[process]
            process_slice_list = slice_list[frames[0]:frames[-1]+1]
        except IndexError:
            process_slice_list = []

        return process_slice_list

    def calculate_slice_padding(self, in_slice, pad_ammount, data_stop):
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
            maxval = data_stop + 1

        out_slice = slice(minval, maxval, sl.step)

        return (out_slice, (minpad, maxpad))

    def get_pad_data(self, slice_tup, pad_tup):
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

    def get_padding_dict(self):
        pData = self.get_plugin_data()
        padding = Padding(pData.get_pattern())
        for key in pData.padding.keys():
            getattr(padding, key)(pData.padding[key])
        return padding.get_padding_directions()

    def get_padded_slice_data(self, input_slice_list):
        slice_list = list(input_slice_list)
        pData = self.get_plugin_data()
        if pData.padding is None:
            return self.data[tuple(slice_list)]

        padding_dict = self.get_padding_dict()
        pad_list = []
        for i in range(len(slice_list)):
            pad_list.append((0, 0))

        for direction in padding_dict.keys():
            slice_list[direction], pad_list[direction] = \
                self.calculate_slice_padding(slice_list[direction],
                                             padding_dict[direction],
                                             self.get_shape()[direction])

        return self.get_pad_data(tuple(slice_list), tuple(pad_list))

    def get_unpadded_slice_data(self, input_slice_list, padded_dataset):
        padding_dict = self.get_plugin_data().padding
        if padding_dict is None:
            return padded_dataset

        padding_dict = self.get_padding_dict()

        slice_list = list(input_slice_list)
        pad_list = []
        expand_list = []

        for i in range(len(slice_list)):
            pad_list.append((0, 0))
            expand_list.append(0)

        for direction in padding_dict.keys():
            slice_list[direction], pad_list[direction] = \
                self.calculate_slice_padding(slice_list[direction],
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

    def get_orthogonal_slice(self, full_slice, core_direction):
        dirs = range(len(full_slice))
        for direction in core_direction:
            dirs.remove(direction)
        result = []
        for direction in dirs:
            result.append(full_slice[direction])
        return result
