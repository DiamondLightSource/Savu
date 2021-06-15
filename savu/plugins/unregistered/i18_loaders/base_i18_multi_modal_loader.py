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
.. module:: base_i18_multi_modal_loader
   :platform: Unix
   :synopsis: Contains a base class from which all multi-modal loaders are \
   derived.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import h5py
import logging
from savu.data.data_structures.data_add_ons import DataMapping

from savu.plugins.loaders.mapping_loaders.base_multi_modal_loader \
    import BaseMultiModalLoader


class BaseI18MultiModalLoader(BaseMultiModalLoader):
    def __init__(self, name='BaseI18MultiModalLoader'):
        super(BaseI18MultiModalLoader, self).__init__(name)

    def multi_modal_setup(self, ltype, name):
        # set up the file handles
        exp = self.exp
        data_obj = exp.create_data_object("in_data", name)
        data_obj.backing_file = \
            h5py.File(exp.meta_data.get("data_file"), 'r')
        f = data_obj.backing_file
        logging.debug("Creating file '%s' '%s'_entry",
                      data_obj.backing_file.filename, ltype)

        data_obj.meta_data.set(
            "mono_energy", f[self.parameters['monochromator']][()]/1e3)
        x = f[self.parameters['x']][()]

        if self.parameters['x'] is not None:
            if x.ndim > 1:
                data_obj.meta_data.set("x", x[0, :])
            else:
                data_obj.meta_data.set("x", x)

        if self.parameters['y'] is not None:
            y = f[self.parameters['y']][()]
            data_obj.meta_data.set("y", y)
        if self.parameters['rotation'] is not None:
            rotation_angle = f[self.parameters['rotation']][()]
            if rotation_angle.ndim > 1:
                rotation_angle = rotation_angle[:, 0]

            data_obj.meta_data.set("rotation_angle", rotation_angle)
        return data_obj

    def set_motors(self, data_obj, ltype):
        # now lets extract the map, if there is one!
        # to begin with
        data_obj.data_mapping = DataMapping()
        logging.debug("========="+ltype+"=========")
        motors = self.parameters['scan_pattern']
        data_obj.data_mapping.set_axes(self.parameters['scan_pattern'])
        nAxes = len(data_obj.get_shape())
        #logging.debug nAxes
        cts = 0
        chk = 0
        chk1 = 0
        motor_type = []
        labels = []
        fast_axis = self.parameters["fast_axis"]
        logging.debug("axes input are:"+str(motors))
        unknown_count = 0
        for ii in range(nAxes):
            # find the rotation axis
            try:
                data_axis = self.parameters[motors[ii]]# get that out the file
                logging.debug("the data axis is %s" % str(data_axis))
                if motors[ii]=="rotation":
                    data_obj.data_mapping._is_tomo = True
                    motor_type.append('rotation')
                    label = 'rotation_angle'
                    units = 'degrees'
                    logging.debug(ltype + " reader: %s", "is a tomo scan")
                elif motors[ii] in ["x","y"]:
                    cts += 1  # increase the order of the map
                    motor_type.append('translation')
                    if (motors[ii]==fast_axis):
                        label='x'
                    else:
                        label='y'
                    units = 'mm'
            except KeyError as e:
                #print("exception was ",str(e))
                #print("found no motor")
                motor_type.append('None')
                #now the detector axes
                if ltype =='fluo':
                    label = 'energy'
                    units = 'counts'
                elif ltype =='xrd':
                    if chk==0:
                        label = 'detector_x'
                    elif chk==1:
                        label = 'detector_y'
                    units = 'index'
                    chk=chk+1

            except IndexError:
                '''
                some additional singleton dimensions have been added in the latest mapping project stuff on I18
                This fixes that.
                '''
                if ltype =='xrd':
                    if chk1 == 0:
                        label = 'detector_x'
                    elif chk1 == 1:
                        label = 'detector_y'
                    units = 'pixels'
                    chk1=chk1+1
                else:
                    label = 'unknown_%s' % unknown_count
                    units = 'unknown'
                    unknown_count += 1
            except:
                raise

            labels.append(label+'.'+units)
        if not motors:
            logging.debug("%s reader: No maps found!", ltype)
        #logging.debug labels
        data_obj.set_axis_labels(*tuple(labels))
        data_obj.data_mapping.set_motors(motors)
        data_obj.data_mapping.set_motor_type(motor_type)
        if (cts):
            data_obj.data_mapping._is_map = cts
        else:
            logging.debug("'%s' reader: No translations found!", ltype)
            pass
        logging.debug("axis labels:"+str(labels))
        logging.debug("motor_type:"+str(motor_type))

    def add_patterns_based_on_acquisition(self, data_obj, ltype):
        motor_type = data_obj.data_mapping.get_motor_type()
        projection = []
        for item, key in enumerate(motor_type):
            if key == 'translation':
                projection.append(item)
#                 logging.debug projection
            elif key == 'rotation':
                rotation = item
        dims = list(range(len(data_obj.get_shape())))
        if data_obj.data_mapping._is_map:
            proj_dir = tuple(projection)
            data_obj.add_pattern("PROJECTION", core_dims=proj_dir,
                                 slice_dims=tuple(set(dims) - set(proj_dir)))

        if data_obj.data_mapping._is_tomo:
            #rotation and fast axis
            sino_dir = (rotation, proj_dir[-1])
            slice_dims = tuple(set(dims) - set(sino_dir))
            if slice_dims:
                data_obj.add_pattern("SINOGRAM", core_dims=sino_dir,
                                     slice_dims=slice_dims)

        if ltype == 'fluo':
            spec_core = (-1,) # it will always be this
            spec_slice = tuple(dims[:-1])
            data_obj.add_pattern("SPECTRUM", core_dims=spec_core,
                                 slice_dims=spec_slice)


        if ltype == 'xrd':
            diff_core = (-2,-1) # it will always be this
            diff_slice = tuple(dims[:-2])
            data_obj.add_pattern("DIFFRACTION", core_dims=diff_core,
                                 slice_dims=diff_slice)

        if ltype == 'monitor':
            # this is needed for I0 corrections of single sinogram ND data
            channel_core = (dims[-1],)
            channel_slice = tuple(dims[:-1])
            data_obj.add_pattern("CHANNEL", core_dims=channel_core,
                        slice_dims=channel_slice)

