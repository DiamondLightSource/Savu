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
.. module:: utils
   :platform: Unix
   :synopsis: Utilities for managing data

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""

import numpy as np


def get_slice_list(data, frame_type):
    if frame_type in data.core_directions.keys():
        it = np.nditer(data.data, flags=['multi_index'])
        dirs_to_remove = list(data.core_directions[frame_type])
        dirs_to_remove.sort(reverse=True)
        for direction in dirs_to_remove:
            it.remove_axis(direction)
        mapping_list = range(len(it.multi_index))
        dirs_to_remove.sort()
        for direction in dirs_to_remove:
            mapping_list.insert(direction, -1)
        mapping_array = np.array(mapping_list)
        slice_list = []
        while not it.finished:
            tup = it.multi_index + (slice(None),)
            slice_list.append(tuple(np.array(tup)[mapping_array]))
            it.iternext()
        return slice_list
    return None


def calc_step(slice_a, slice_b):
    result = []
    for i in range(len(slice_a)):
        if slice_a[i] == slice_b[i]:
            result.append(0)
        else:
            result.append(slice_b[i] - slice_a[i])
    return result


def group_slice_list(slice_list, max_frames):
    banked = []
    batch = []
    step = -1
    for sl in slice_list:
        if len(batch) == 0:
            batch.append(sl)
            step = -1
        elif step == -1:
            new_step = calc_step(batch[-1], sl)
            # check stepping in 1 direction
            if (np.array(new_step) > 0).sum() > 1:
                # we are stepping in multiple directions, end the batch
                banked.append((step, batch))
                batch = []
                batch.append(sl)
                step = -1
            else:
                batch.append(sl)
                step = new_step
        else:
            new_step = calc_step(batch[-1], sl)
            if new_step == step:
                batch.append(sl)
            else:
                banked.append((step, batch))
                batch = []
                batch.append(sl)
                step = -1
    banked.append((step, batch))

    # now combine the groups into single slices
    grouped = []
    for step, group in banked:
        working_slice = list(group[0])
        step_dir = step.index(max(step))
        start = group[0][step_dir]
        stop = group[-1][step_dir]
        for i in range(start, stop, max_frames):
            new_slice = slice(i, i+max_frames, step[step_dir])
            working_slice[step_dir] = new_slice
            grouped.append(tuple(working_slice))
    return grouped


def get_grouped_slice_list(data, frame_type, max_frames):
    sl = get_slice_list(data, frame_type)
    if sl is None:
        raise Exception("data type %s does not support slicing in the "
                        "%s direction" % (type(data), frame_type))
    gsl = group_slice_list(sl, max_frames)
    return gsl


def get_slice_list_per_process(slice_list, plugin, processes):
    frame_index = np.arange(len(slice_list))
    frames = np.array_split(frame_index, processes)[plugin]
    return slice_list[frames[0]:frames[-1]+1]


def calculate_slice_padding(in_slice, pad_ammount, data_stop):
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
        maxpad = (maxval-data_stop) - 1
        maxval = data_stop + 1

    out_slice = slice(minval, maxval, sl.step)

    return (out_slice, (minpad, maxpad))


def get_pad_data(slice_tup, pad_tup, data):
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

    data_slice = data[tuple(slice_list)]
    data_slice = np.pad(data_slice, tuple(pad_list), mode='edge')
    return data_slice


def get_padded_slice_data(input_slice_list, padding_dict, data):
    slice_list = list(input_slice_list)
    pad_list = []
    for i in range(len(slice_list)):
        pad_list.append((0, 0))

    for key in padding_dict.keys():
        if key in data.core_directions.keys():
            for direction in data.core_directions[key]:
                slice_list[direction], pad_list[direction] = \
                    calculate_slice_padding(slice_list[direction],
                                            padding_dict[key],
                                            data.data.shape[direction])

    return get_pad_data(tuple(slice_list), tuple(pad_list), data.data)


def get_unpadded_slice_data(input_slice_list, padding_dict, data,
                            padded_dataset):
    slice_list = list(input_slice_list)
    pad_list = []
    expand_list = []
    for i in range(len(slice_list)):
        pad_list.append((0, 0))
        expand_list.append(0)
    for key in padding_dict.keys():
        if key in data.core_directions.keys():
            for direction in data.core_directions[key]:
                slice_list[direction], pad_list[direction] = \
                    calculate_slice_padding(slice_list[direction],
                                            padding_dict[key],
                                            padded_dataset.shape[direction])
                expand_list[direction] = padding_dict[key]

    slice_list_2 = []
    pad_list_2 = []
    for i in range(len(slice_list)):
        if type(slice_list[i]) == slice:
            slice_list_2.append(slice_list[i])
            pad_list_2.append(pad_list[i])
        else:
            if pad_list[i][0] == 0 and pad_list[i][0] == 0:
                slice_list_2.append(slice_list[i])
            else:
                slice_list_2.append(slice(slice_list[i], slice_list[i]+1, 1))
                pad_list_2.append(pad_list[i])

    slice_list_3 = []
    for i in range(len(padded_dataset.shape)):
        start = None
        stop = None
        if expand_list[i] > 0:
            start = expand_list[i]
            stop = -expand_list[i]
        sl = slice(start, stop, None)
        slice_list_3.append(sl)

    result = padded_dataset[tuple(slice_list_3)]
    return result


def get_orthogonal_slice(full_slice, core_direction):
    dirs = range(len(full_slice))
    for direction in core_direction:
        dirs.remove(direction)
    result = []
    for direction in dirs:
        result.append(full_slice[direction])
    return result
