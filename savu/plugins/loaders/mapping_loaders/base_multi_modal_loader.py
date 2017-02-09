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
   :synopsis: Contains a base class from which all multi-modal loaders are \
   derived.
.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>
"""

import h5py
import logging
from savu.data.data_structures.data_add_ons import DataMapping

from savu.plugins.loaders.base_loader import BaseLoader


class BaseMultiModalLoader(BaseLoader):
    """
    This class provides a base for all multi-modal loaders
    :param fast_axis: what is the fast axis called. Default:"x"
    """

    def multi_modal_setup(self, ltype, data_str):
        # set up the file handles
        exp = self.exp
        data_obj = exp.create_data_object("in_data", ltype)
        data_obj.backing_file = \
            h5py.File(exp.meta_data.get_meta_data("data_file"), 'r')
        logging.debug("Creating file '%s' '%s'_entry",
                      data_obj.backing_file.filename, ltype)
        # now lets extract the entry so we can figure out our geometries!
        if ltype == 'NXmonitor':
            entry = self.get_NXapp('NXstxm', data_obj.backing_file, 'entry1/')[0]
        else:
            entry = self.get_NXapp(ltype, data_obj.backing_file, 'entry1/')[0]
        logging.debug(str(entry))

        #lets get the data out
        data_obj.data = data_obj.backing_file[entry.name + data_str]
        data_obj.set_shape(data_obj.data.shape)
        #Now the beam fluctuations
        # the ion chamber "normalisation"
        try:
            control = data_obj.backing_file[entry.name+'/monitor/data']
        # this is global since it is to do with the beam
            exp.meta_data.set_meta_data("control", control)
            logging.debug('adding the ion chamber to the meta data')
        except:
            logging.warn('No ion chamber information. Leaving this blank')
        return data_obj, entry
    

    def set_motors(self, data_obj, entry, ltype):
        # now lets extract the map, if there is one!
        # to begin with
        data_obj.data_mapping = DataMapping()
        logging.debug("========="+ltype+"=========")
        axes = entry['data'].attrs['axes']
        data_obj.data_mapping.set_axes(axes)
        nAxes = len(axes)
        #logging.debug nAxes
        cts = 0
        motors = []
        motor_type = []
        labels = []
        fast_axis = self.parameters["fast_axis"]
        axes_slice_list = [slice(0,1,1)]*nAxes
        logging.debug("axes in the file are:"+str(str(entry['data'].attrs["axes"])))
        for ii in range(nAxes):
            # find the rotation axis
            data_axis = 'data/' + entry['data'].attrs["axes"][ii]
            logging.debug("the data axis is %s" % str(data_axis))
            entry_axis = entry[data_axis]
            try:
                units = entry_axis.attrs['units']
            except KeyError:
                logging.debug('leaving the units out for axis %s', str(ii))
                units = 'unit'
            
            try:
                mType = entry_axis.attrs['transformation_type']
                if (mType == "rotation"):
                    #what axis is this? Could we store it?
                    motors.append(data_obj.backing_file[entry.name + '/' +
                                                        data_axis])
                    data_obj.data_mapping._is_tomo = True
                    motor_type.append('rotation')
                    label = 'rotation_angle'
                    rotation_angle = \
                        data_obj.backing_file[entry.name + '/' +data_axis].value
                    if rotation_angle.ndim > 1:
#                         idx = axes_slice_list[:]# make a copy
#                         idx[ii] = slice(0,rotation_angle.shape[ii],1)
                        rotation_angle = rotation_angle[:,0]
#                         rotation_angle = rotation_angle[idx].squeeze()

                    data_obj.meta_data.set_meta_data('rotation_angle', rotation_angle)
                    logging.debug(ltype + " reader: %s", "is a tomo scan")
                elif (mType == "translation"):
                    # increase the order of the map
                    # what axes are these? Would be good to have for the
                    # pattern stuff
                    # attach this to the scan map
                    motors.append(data_obj.backing_file[entry.name + '/' +
                                                        data_axis])
                    motor_type.append('translation')
                    if (str(entry['data'].attrs["axes"][ii])==fast_axis):
                        label='x'
                        x = \
                            data_obj.backing_file[entry.name + '/' +data_axis].value
                        if x.ndim > 1:
                            print "xshape is:"+str(x.shape)
#                             idx = axes_slice_list[:]# make a copy
#                             idx[ii] = slice(0,x.shape[ii],1)
#                             x = x[idx].squeeze()
                            x = x[0,:]
                        data_obj.meta_data.set_meta_data('x', x)
                    else:
                        label='y'
                        y = \
                            data_obj.backing_file[entry.name + '/' +data_axis].value
                        if y.ndim > 1:
#                             idx = axes_slice_list[:]# make a copy
#                             idx[ii] = slice(0,y.shape[ii],1)
#                             print "yshape is:"+str(y.shape)
#                             y = y[idx].squeeze()
                            y = y[:,0]
                        data_obj.meta_data.set_meta_data('y', y)
                    cts += 1
                    
            except KeyError:
                motor_type.append('None')
                label = str(entry['data'].attrs["axes"][ii])
            labels.append(label+'.'+units)

        if not motors:
            logging.debug("%s reader: No maps found!", ltype)
        #logging.debug labels
        data_obj.set_axis_labels(*tuple(labels))
        data_obj.data_mapping.set_motors(motors)
        data_obj.data_mapping.set_motor_type(motor_type)
        if (cts):
            # set the map counts to be the number of linear scan dimensions
            data_obj.data_mapping._is_map = cts
            # chuck to meta
        else:
            logging.debug("'%s' reader: No translations found!", ltype)
            pass
        logging.debug("axis labels:"+str(labels))
        logging.debug("motor_type:"+str(motor_type))

    def add_patterns_based_on_acquisition(self, data_obj, ltype):
        motor_type = data_obj.data_mapping.get_motor_type()
        dims = range(len(motor_type))
        projection = []
        for item, key in enumerate(motor_type):
            if key == 'translation':
                projection.append(item)
#                 logging.debug projection
            elif key == 'rotation':
                rotation = item

        if data_obj.data_mapping._is_map:
            logging.debug("%s is map %s" % (ltype,data_obj.data_mapping._is_map))
            proj_dir = tuple(projection)
            logging.debug("is a map")
            logging.debug("the proj cores are"+str(proj_dir))
            logging.debug("the proj slices are"+str(tuple(set(dims) - set(proj_dir))))
            data_obj.add_pattern("PROJECTION", core_dir=proj_dir,
                                 slice_dir=tuple(set(dims) - set(proj_dir)))

        if data_obj.data_mapping._is_tomo:
            logging.debug("%s is tomo", ltype)
            logging.debug("I am adding a sinogram")
            #rotation and fast axis
            sino_dir = (rotation, proj_dir[-1])
            logging.debug("is a tomo")
            logging.debug("the sino cores are:"+str(sino_dir))
            logging.debug("the sino slices are:"+str(tuple(set(dims) - set(sino_dir))))
            sino_slice_dir = tuple(set(dims) - set(sino_dir))
            data_obj.add_pattern("SINOGRAM", core_dir=sino_dir,
                                 slice_dir=sino_slice_dir)
            
        # I don't think this is needed anymore
#         if data_obj.data_mapping._is_tomo and (data_obj.data_mapping._is_map==1) and len(sino_slice_dir)<2:
#             print "I'm here"
#             data_obj.add_pattern("PROJECTION", core_dir=(0,),
#                         slice_dir=(1,))
        
        if ltype is 'xrd':
            diff_core = (-2,-1) # it will always be this
            diff_slice = tuple(dims[:-2])
            logging.debug("is a diffraction")
            logging.debug("the diffraction cores are:"+str(diff_core))
            logging.debug("the diffraction slices are:"+str(diff_slice))
            data_obj.add_pattern("DIFFRACTION", core_dir=diff_core,
                                 slice_dir=diff_slice)
