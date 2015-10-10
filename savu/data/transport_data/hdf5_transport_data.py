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

from savu.data.data_structures import Padding

NX_CLASS = 'NX_class'


class Hdf5TransportData(object):
    """
    The Hdf5TransportData class performs the loading and saving of data
    specific to a hdf5 transport mechanism.
    """

    def __init__(self):
        self.backing_file = None

    def load_data(self, plugin_runner):
        exp = self.exp
        plugin_list = exp.meta_data.plugin_list.plugin_list
        final_plugin = plugin_list[-1]
        saver_plugin = plugin_runner.load_plugin(final_plugin["id"])

        logging.debug("generating all output files")
        out_data_objects = []
        count = 0
        for plugin_dict in plugin_list[1:-1]:

            plugin_id = plugin_dict["id"]
            logging.debug("Loading plugin %s", plugin_id)

            exp.log("Point 1")

            plugin = plugin_runner.plugin_loader(plugin_dict)

            exp.log("Point 2")

            self.set_filenames(plugin, plugin_id, count)

            saver_plugin.setup(exp)

            out_data_objects.append(exp.index["out_data"].copy())
            #exp.clear_out_data_objects()
            exp.set_out_data_to_in()

            exp.log("Point 3")
            count += 1

        return out_data_objects

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
                group_name = "%i-%s" % (count, plugin.name)
                exp.barrier()
                logging.debug("(set_filenames) Creating output file after "
                              " barrier %s", filename)
                expInfo.set_meta_data(["filename", key], filename)
                expInfo.set_meta_data(["group_name", key], group_name)

    def add_data_link_and_attributes(self, linkType):

        nxs_filename = self.exp.meta_data.get_meta_data('nxs_filename')
        logging.debug("Adding link to file %s", nxs_filename)
        plugin_file = h5py.File(nxs_filename, 'a')

        if linkType is 'final_result':
            entry = plugin_file['entry'].create_group('final_result')
            entry.attrs[NX_CLASS] = 'NXdata'
            entry['final_result'] = self.external_link()
            entry = plugin_file['entry'].require_group('final_result')
        else:
            entry = plugin_file['entry'].require_group('intermediate')
            entry.attrs[NX_CLASS] = 'NXcollection'
            entry[self.group_name] = self.external_link()
        return plugin_file, entry

    def output_metadata(self, entry):
        axis_labels = self.meta_data.get_meta_data("axis_labels")
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
            temp = self.group.create_dataset(name, mData.shape, mData.dtype)
            temp[...] = mData[...]
            count += 1
        entry.attrs['axes'] = axes

    def save_data(self, link_type):
        process = self.exp.meta_data.get_meta_data('process')
        if process is 0:
            logging.info("PROCESS 0 is adding data link and metadata")
            plugin_file, entry = self.add_data_link_and_attributes(link_type)
            #self.output_metadata(entry)
            #plugin_file.close()

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
        sshape = [shape[sslice] for sslice in slice_dirs]
        chunk = []
        length = []
        repeat = []
        for dim in range(len(slice_dirs)):
            chunk.append(int(np.prod(shape[0:dim])))
            length.append(sshape[dim])
            repeat.append(int(np.prod(sshape[dim+1:])))

        return chunk, length, repeat

    def get_slice_dirs_index(self, slice_dirs, shape):
        # returns a list of arrays for each slice dimension , where each array
        # gives the indices for that slice dimension
        # create the indexing array
        [chunk, length, repeat] = self.chunk_length_repeat(slice_dirs, shape)
        idx_list = []
        for dim in range(len(slice_dirs)):
            c = chunk[dim]
            l = length[dim]
            r = repeat[dim]
            idx = np.ravel(np.kron(np.arange(l), np.ones((r, c))))
            idx_list.append(idx.astype(int))

        return np.array(idx_list)

    def single_slice_list(self):
        pData = self.get_plugin_data()
        slice_dirs = pData.get_slice_directions()
        [fix_dirs, value] = pData.get_fixed_directions()
        shape = self.get_shape()
        index = self.get_slice_dirs_index(slice_dirs, np.array(shape))
        nSlices = index.shape[1]
        nDims = len(shape)

        slice_list = []
        for i in range(nSlices):
            getitem = [slice(None)]*nDims
            for f in range(len(fix_dirs)):
                getitem[fix_dirs[f]] = slice(value[f], value[f] + 1, 1)
            for sdir in range(len(slice_dirs)):
                getitem[slice_dirs[sdir]] = slice(index[sdir, i],
                                                  index[sdir, i] + 1, 1)
            slice_list.append(tuple(getitem))

        return slice_list

    def banked_list(self, slice_list):
        shape = self.get_shape()
        slice_dirs = self.get_plugin_data().get_slice_directions()
        chunk, length, repeat = self.chunk_length_repeat(slice_dirs, shape)

        banked = []
        for rep in range(repeat[0]):
            start = rep*length[0]
            end = start + length[0]
            banked.append(slice_list[start:end])

        return banked, length[0], slice_dirs

    def grouped_slice_list(self, slice_list, max_frames):
        banked, length, slice_dir = self.banked_list(slice_list)
        grouped = []
        count = 0
        for group in banked:
            full_frames = int(length/float(max_frames))
            rem = 1 if (length % max_frames) else 0
            working_slice = list(group[0])

            for i in range(0, (full_frames*max_frames), max_frames):
                new_slice = slice(i, i+max_frames, 1)
                working_slice[slice_dir[0]] = new_slice
                grouped.append(tuple(working_slice))

            if rem:
                new_slice = slice(i+max_frames, len(group), 1)
                working_slice[slice_dir[0]] = new_slice
                grouped.append(tuple(working_slice))
            count += 1

        return grouped

    def get_grouped_slice_list(self):
        max_frames = self.get_plugin_data().get_frame_chunk()
        max_frames = (1 if max_frames is None else max_frames)

        sl = self.single_slice_list()

#        if isinstance(self, ds.TomoRaw):
#            sl = self.get_frame_raw(sl)

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
        padding = Padding(self.get_current_pattern())
        for key in self.padding.keys():
            getattr(padding, key)(self.padding[key])
        return padding.get_padding_directions()

    def get_padded_slice_data(self, input_slice_list):
        slice_list = list(input_slice_list)
        if self.get_plugin_data().padding is None:
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
