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
   :synopsis: Utilitits for managing data

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""


import numpy as np

def get_slice_list(data, frame_type):
    if frame_type in data.core_directions.keys():
        it = np.nditer(data.data, flags=['multi_index'])
        dirs_to_remove = list(data.core_directions[frame_type])
        dirs_to_remove.sort(reverse=True)
        for direction in dirs_to_remove:
            it.remove_axis(direction);
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
            if (np.array(new_step)>0).sum() > 1:
                # we are stepping in multiple directions, end the batch
                banked.append((step, batch))
                batch = []
                batch.append(sl)
                step = -1
            else :
                batch.append(sl)
                step = new_step
        else :
            new_step = calc_step(batch[-1], sl)
            if new_step == step :
                batch.append(sl)
            else :
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
    gsl = group_slice_list(sl, max_frames)
    return gsl

def get_slice_list_per_process(slice_list, process, processes):
    frame_index = np.arange(len(slice_list))
    frames = np.array_split(frame_index, processes)[process]
    return slice_list[frames[0]:frames[-1]+1]

def get_orthogonal_slice(full_slice, core_direction):
    dirs = range(len(full_slice))
    for direction in core_direction:
        dirs.remove(direction)
    result = []
    for direction in dirs:
        result.append(full_slice[direction])
    return result
