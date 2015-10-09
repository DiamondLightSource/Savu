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
.. module:: base_multi_modal_loader
   :platform: Unix
   :synopsis: Contains a base class from which all multi-modal loaders are
   derived.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import h5py
import logging
import savu.data.data_structures as ds

from savu.plugins.base_loader import BaseLoader


class BaseMultiModalLoader(BaseLoader):
    """
    This class provides a base for all multi-modal loaders
    """

    def multi_modal_setup(self, ltype, data_str):
        print "*** in the BaseMultiModalLoader setup method!"
        # set up the file handles
        exp = self.exp
        data_obj = exp.create_data_object("in_data", ltype)
        data_obj.backing_file = \
            h5py.File(exp.meta_data.get_meta_data("data_file"), 'r')
        logging.debug("Creating file '%s' '%s'_entry",
                      data_obj.backing_file.filename, ltype)
        # now lets extract the entry so we can figure out our geometries!
        entry = self.get_NXapp(ltype, data_obj.backing_file, 'entry1/')[0]
        #lets get the data out
        data_obj.data = data_obj.backing_file[entry.name + data_str]
        data_obj.set_shape(data_obj.data.shape)
        #Now the beam fluctuations
        # the ion chamber "normalisation"
        control = data_obj.backing_file[entry.name+'/monitor/data']
        # this is global since it is to do with the beam
        exp.meta_data.set_meta_data("control", control)
        return data_obj, entry

    def set_motors(self, data_obj, entry, ltype):
        # now lets extract the map, if there is one!
        # to begin with
        data_obj.data_mapping = ds.DataMapping()

        axes = entry['data'].attrs['axes']
        if ltype is 'stxm':
            nAxes = len(axes)
        else:
            # the -1 here comes as data is the last axis only
            nAxes = len(axes)-1

        cts = 0
        motors = []
        motor_type = []
        for ii in range(nAxes):
            # find the rotation axis
            data_axis = 'data/' + entry['data'].attrs["axes"][ii]
            entry_axis = entry[data_axis]
            if (entry_axis.attrs['transformation_type'] == "rotation"):
                #what axis is this? Could we store it?
                print entry.name + '/' + data_axis
                motors.append(data_obj.backing_file[entry.name + '/' +
                                                    data_axis])
                data_obj.data_mapping.is_tomo = True
                motor_type.append('rotation')
                logging.debug(ltype + " reader: '%s'", "is a tomo scan")
            elif (entry_axis.attrs['transformation_type'] == "translation"):
                cts += 1  # increase the order of the map
                # what axes are these? Would be good to have for the
                # pattern stuff
                # attach this to the scan map
                motors.append(data_obj.backing_file[entry.name + '/' +
                                                    data_axis])
                motor_type.append('translation')

        if not motors:
            logging.debug("'%s' reader: No maps found!", ltype)

        data_obj.data_mapping.set_motors(motors)
        data_obj.data_mapping.set_motor_type(motor_type)
        if (cts):
            # set the map counts to be the number of linear scan dimensions
            data_obj.data_mapping.is_map = cts
            # chuck to meta
        else:
            logging.debug("'%s' reader: No translations found!", ltype)
            pass

    def add_patterns_based_on_acquisition(self, data_obj, ltype):
        motor_type = data_obj.data_mapping.get_motor_type()
        # now we will set up the core directions that we need for processing
        projection = []
        projection_slice = []
        for item, key in enumerate(motor_type):
            if key == 'translation':
                projection.append(item)
            elif key != 'translation':
                projection_slice.append(item)
            if key == 'rotation':
                # we will assume one rotation for now to save my headache
                rotation = item
        projdir = tuple(projection)
        projsli = tuple(projection_slice)

        print "projdir", projdir, "projsli", projsli

        end = -2 if ltype is 'xrd' else -1

        if data_obj.data_mapping.is_map:
            print "ADDING THE PROJECTION PATTERN", ltype
            # two translation axes
            data_obj.add_pattern("PROJECTION", core_dir=projdir,
                                 slice_dir=projsli)

        if data_obj.data_mapping.is_tomo:
            print "ADDING THE SINOGRAM PATTERN", ltype
            #rotation and fast axis
            data_obj.add_pattern("SINOGRAM", core_dir=(rotation, projdir[-1]),
                                 slice_dir = projdir[:end])
