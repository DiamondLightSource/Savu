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

import numpy as np

import savu.data.data_structures as ds
from savu.core.utils import logmethod

class Hdf5TransportData(object):
    """
    The Hdf5TransportData class performs the loading and saving of data 
    specific to a hdf5 transport mechanism.
    """
            
    def __init__(self):
        self.backing_file = None

    
    def load_data(self, plugin_runner, exp):

        plugin_list = exp.meta_data.plugin_list.plugin_list
        final_plugin = plugin_list[-1]
        saver_plugin = plugin_runner.load_plugin(final_plugin["id"])

        logging.debug("generating all output files")
        out_data_objects = []
        count = 0
        for plugin_dict in plugin_list[1:-1]:
            
            plugin_id = plugin_dict["id"]
            logging.debug("Loading plugin %s", plugin_id)
            
            plugin = plugin_runner.plugin_loader(exp, plugin_dict)
            
            self.set_filenames(exp, plugin, plugin_id, count)
            
            saver_plugin.setup(exp)
            
            out_data_objects.append(exp.index["out_data"].copy())
            exp.clear_out_data_objects()
         
            count += 1
            
        return out_data_objects

    
    def set_filenames(self, exp, plugin, plugin_id, count):
        expInfo = exp.meta_data
        expInfo.set_meta_data("filename", {})
        expInfo.set_meta_data("group_name", {})
        for key in exp.index["out_data"].keys():
            filename = os.path.join(expInfo.get_meta_data("out_path"),"%s%02i_%s" % \
                                    (os.path.basename(expInfo.get_meta_data("process_file")),
                                    count, plugin_id))
            filename = filename + "_" + key + ".h5"
            group_name = "%i-%s" % (count, plugin.name)
            logging.debug("Creating output file %s", filename)
            expInfo.set_meta_data(["filename", key], filename)
            expInfo.set_meta_data(["group_name", key], group_name)

        
    def save_data(self):
        """
        Closes the backing file and completes work
        """
        if self.backing_file is not None:
            try:
                logging.debug("Completing file %s",self.backing_file.filename)
                self.backing_file.close()
                self.backing_file = None
            except:
                pass
                

    def get_slice_dirs_index(self, slice_dirs, shape):
        # create the indexing array 
        sshape = [shape[sslice] for sslice in slice_dirs]
    
        idx_list= []
        for dim in range(len(slice_dirs)):
            chunk = np.prod(shape[0:dim])
            length = sshape[dim]
            repeat = np.prod(sshape[dim+1:])
            idx = np.ravel(np.kron(np.arange(length), np.ones((repeat, chunk))))
            idx_list.append(idx.astype(int))
                    
        return np.array(idx_list)


    def empty_array_slice_list(self):
        slice_dirs = self.get_slice_directions()
        shape = self.get_shape()
        nDims = len(shape)
        index = self.get_slice_dirs_index(slice_dirs, np.array(shape))
        nSlices = index.shape[1]

        slice_list = []
        for i in range(nSlices):
            getitem = [slice(None)]*nDims
            for sdir in range(len(slice_dirs)):
                getitem[slice_dirs[sdir]] = slice(index[sdir, i], index[sdir, i] + 1, 1)
            slice_list.append(tuple(getitem))

        return slice_list

        

    def get_slice_list(self):
        it = np.nditer(self.data, flags=['multi_index', 'refs_ok']) # what does this mean?
        dirs_to_remove = list(self.get_core_directions())

        if it.ndim is 0:
            slice_list = self.empty_array_slice_list()
        else:
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

    
    def calc_step(self, slice_a, slice_b):
        result = []
        for i in range(len(slice_a)):
            if slice_a[i] == slice_b[i]:
                result.append(0)
            else:
                result.append(slice_b[i] - slice_a[i])
                
        return result


    def group_slice_list(self, slice_list, max_frames):
        banked = []
        batch = []
        step = -1
        for sl in slice_list:
            # set up for the first slice or after a batch has been appended
            if len(batch) == 0:
                batch.append(sl)
                step = -1
            # there is an unknown step size so find out what the step is
            elif step == -1:
                new_step = self.calc_step(batch[-1], sl)
                # check stepping in 1 direction
                if (np.array(new_step) > 0).sum() > 1:
                    # we are stepping in multiple directions, end the batch
                    # append it to the banked batches
                    banked.append((step, batch))
                    # reset the batch to an empty list
                    batch = []
                    # add the current slice to the batch
                    batch.append(sl)
                    # set the step as we dont know it
                    step = -1
                else:
                    # we are stepping in one dimention so add this slice to the
                    # batch and set the step size correctly
                    batch.append(sl)
                    step = new_step
            else:
                # we know the step size, so carry on with getting a batch of 
                # data
                new_step = self.calc_step(batch[-1], sl)
                # make sure the steps are the same                
                if new_step == step:
                    # if so append the slice to the batch
                    batch.append(sl)
                else:
                    # somthing has changed so add this step and batch to the 
                    # banked list as before
                    banked.append((step, batch))
                    batch = []
                    batch.append(sl)
                    step = -1
        banked.append((step, batch))
    
        # now combine the groups into single slices
        grouped = []
        for step, group in banked:
            # get the group of slices and the slice step ready
            working_slice = list(group[0])
            step_dir = step.index(max(step))
            start = group[0][step_dir]
            stop = group[-1][step_dir]
            # using the start and stop points, step through in steps of 
            # max_slice
            #******************************************************************
            # FIXME THIS IS ALMOST CERTAINLY WRONG AS IT DOSE NOT WORK FOR 
            # LISTS WHICH ARE NOT MULTIPLES OF MAX_FRAMES
            #******************************************************************
            for i in range(start, stop, max_frames):
                new_slice = slice(i, i+max_frames, step[step_dir])
                working_slice[step_dir] = new_slice
                grouped.append(tuple(working_slice))
        return grouped
    
    
    def get_grouped_slice_list(self):
        max_frames = self.get_nFrames()
        max_frames = (1 if max_frames is None else max_frames)

        sl = self.get_slice_list()

        if isinstance(self, ds.TomoRaw):
            sl = self.get_frame_raw(sl)
      
        if sl is None:
            raise Exception("Data type", self.get_current_pattern_name(), 
                            "does not support slicing in directions", 
                            self.get_slice_directions())
                            
        gsl = self.group_slice_list(sl, max_frames)
 
        return gsl


    def get_slice_list_per_process(self, expInfo):
        processes = expInfo.get_meta_data("processes")
        process = expInfo.get_meta_data("process")
        #slice_list = self.get_grouped_slice_list()

        # *** The next 3 lines are temporary to remove group slicing until fixed.
        # Using empty_array_slice_list() because get_slice_list() doesn't return 
        # dimensions of length 1 and it was easier for me to adapt my version to do this.
        slice_list = self.empty_array_slice_list()
        if isinstance(self, ds.TomoRaw):
            slice_list = self.get_frame_raw(slice_list)

        
        frame_index = np.arange(len(slice_list))
        frames = np.array_split(frame_index, len(processes))[process]
        return [ slice_list[frames[0]:frames[-1]+1], frame_index ]
        


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
            maxpad = (maxval-data_stop) - 1
            maxval = data_stop + 1
    
        out_slice = slice(minval, maxval, sl.step)
    
        return (out_slice, (minpad, maxpad))
    
    
    def get_pad_data(self, slice_tup, pad_tup, data):
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
    
    
    def get_padded_slice_data(self, input_slice_list, padding_dict, data):
        slice_list = list(input_slice_list)
        pad_list = []
        for i in range(len(slice_list)):
            pad_list.append((0, 0))
    
        for key in padding_dict.keys():
            if key in data.core_directions.keys():
                for direction in data.core_directions[key]:
                    slice_list[direction], pad_list[direction] = \
                        self.calculate_slice_padding(slice_list[direction],
                                                padding_dict[key],
                                                self.data.shape[direction])
    
        return self.get_pad_data(tuple(slice_list), tuple(pad_list), data.data)        


    def get_unpadded_slice_data(self, input_slice_list, padding_dict, data,
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
                        self.calculate_slice_padding(slice_list[direction],
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


