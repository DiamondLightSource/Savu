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
.. module:: base_ptycho
   :platform: Unix
   :synopsis: A base class for all ptychographic analysis methods

.. moduleauthor:: Aaron Parsons <scientificsoftware@diamond.ac.uk>

"""
from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
import logging
import numpy as np


class BasePtycho(Plugin, CpuPlugin):  # also make one for gpu
    def __init__(self, name):
        super(BasePtycho, self).__init__(name)

    def setup(self):
        self.exp.log(self.name + " Setting up the ptycho")
        in_dataset, out_dataset = self.get_datasets()

        in_meta_data = in_dataset[0].meta_data# grab the positions from the metadata
        logging.debug('getting the positions...')
        self.positions = in_meta_data.get('xy') # get the positions and bind them

        # lets set up the axis labels for output datasets
        position_labels, probe_labels, object_labels, self.sh = self.setup_axis_labels(in_dataset)
#        print "probe labels are:"+str(probe_labels)
#        print "object labels are:"+str(object_labels)
#        print "position labels are:"+str(position_labels)
        # Now create the datasets and work out the patterns
        ### PROBE ###
        probe = out_dataset[0]
#         probe_shape = in_dataset[0].get_shape()[-2:] + (self.get_num_probe_modes(),)

        self.set_size_probe(in_dataset[0].get_shape()[-2:])
        logging.debug("##### PROBE #####")
        #print("probe shape is:%s",str(self.get_size_probe()))
        probe.create_dataset(axis_labels=probe_labels,
                            shape=self.get_size_probe()) # create the dataset
        self.probe_pattern_setup(probe_labels, probe)

        ### OBJECT ####
        self.set_size_object(in_dataset[0], self.get_positions(),
                             self.get_pixel_size())
        object_trans = out_dataset[1]
        object_shape = self.sh + self.get_size_object()
        logging.debug("##### OBJECT #####")
        #print("object shape is:%s",str(object_shape))
#         print object_labels

        object_trans.create_dataset(axis_labels=object_labels,
                                    shape=object_shape) # create the dataset

        self.object_pattern_setup(object_labels, object_trans)

        ### POSITIONS ###
        logging.debug('##### POSITIONS #####')
        positions = out_dataset[2]
        #print self.sh, self.get_positions().shape
        positions_shape = self.sh + self.get_positions().shape[-2:]
        logging.debug('positions shape is:%s',str(positions_shape))
        #print "positions shape",positions_shape
        positions.create_dataset(axis_labels=position_labels,
                                 shape=positions_shape)

        rest_pos = list(range(len(position_labels)))

        pos_md = \
            {'core_dims':tuple(set(rest_pos) - set([0])), 'slice_dims':(0,)}
        positions.add_pattern("CHANNEL", **pos_md)
        '''
        now we need to tell the setup what we want as input shapes, output shapes, and the number of each of them in one go.
        '''
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup(self.get_plugin_pattern(), self.get_max_frames())
        out_pData[0].plugin_data_setup("PROJECTION", self.get_num_probe_modes())
        out_pData[1].plugin_data_setup("PROJECTION", self.get_num_object_modes())
        out_pData[2].plugin_data_setup("CHANNEL", self.get_max_frames())
        self.exp.log(self.name + " End")

    '''
    The below methods influence the set-up and can be over-ridden depending on which software package we are using

    '''

    def get_plugin_pattern(self):
        '''
        sets the pattern to work in. In this case we consider a ptycho scan to be a 4D_SCAN.
        '''
        return "4D_SCAN"

    def nInput_datasets(self):
        return 1

    def nOutput_datasets(self):
        return 3

    def get_num_probe_modes(self):
        return 1

    def get_num_object_modes(self):
        return 1

    def get_positions(self):
        return self.positions

    def get_pixel_size(self):
        return 30e-9

    def set_size_object(self, dataset,positions, pobj=33e-9):
        '''
        returns tuple
        '''
#         print "positions is "+str(self.get_positions().shape)
        x,y = self.get_positions()[0],self.get_positions()[1]
        probe_size = self.get_size_probe()
        x_fov = np.max(x)-np.min(x)
        y_fov = np.max(y)-np.min(y)
        xsize = int(x_fov//pobj) + probe_size[0]
        ysize = int(y_fov//pobj) + probe_size[1]
        self.obj_shape = xsize,ysize,self.get_num_object_modes()

    def get_size_object(self):
        return self.obj_shape

    def set_size_probe(self,val):
        self.probe_size = (1,)+val + (self.get_num_probe_modes(),)

    def get_size_probe(self):
        '''
        returns tuple
        '''
        return self.probe_size

    def get_max_frames(self):
        return 'single'

    def get_output_axis_units(self):
        return 'nm'

    def probe_pattern_setup(self, probe_labels, probe):
        '''
        This is where we set up the patterns, we need to add, PROJECTIONS, SINOGRAMS, TIMESERIES and SPECTRA
        I've created the TIMESERIES because we could in theory have a time series of spectra
        probe_patterns: PROJECTION, TIMESERIES (for each projection), SPECTRUM (for each energy)
        object_patterns: PROJECTION, SINOGRAM, SPECTRUM (for each energy)
        position_patterns: 1D_METADATA

        '''
        probe_dims = len(probe_labels) # the number of dimensions from the axis labels
        rest_probe = list(range(probe_dims)) # all the dimensions we have
        self.set_projection_pattern(probe, rest_probe)
        self.set_probe_rotation_patterns(probe, rest_probe)
        self.set_probe_energy_patterns(probe, rest_probe)

    def object_pattern_setup(self, object_labels, object_trans):
        '''
        This is where we set up the patterns, we need to add, PROJECTIONS, SINOGRAMS, TIMESERIES and SPECTRA
        I've created the TIMESERIES because we could in theory have a time series of spectra
        probe_patterns: PROJECTION, TIMESERIES (for each projection), SPECTRUM (for each energy)
        object_patterns: PROJECTION, SINOGRAM, SPECTRUM (for each energy)
        position_patterns: 1D_METADATA

        '''
        obj_dims = len(object_labels) # the number of dimensions from the axis labels
#         print "object has "+str(obj_dims)+"dimensions"
        rest_obj = list(range(obj_dims)) # all the dimensions we have
        self.set_projection_pattern(object_trans, rest_obj)
        self.set_object_rotation_patterns(object_trans, rest_obj)
        self.set_object_energy_patterns(object_trans, rest_obj)

    def setup_axis_labels(self, in_dataset):
        '''
        This is where we set up the axis labels
        the 4D scan will contain labels that are: 'xy', 'detectorX', 'detectorY', but the data
        itself may be scanned in energy or rotation or something else. We want to remove all the above,
        and amend them to be the following (preferably with additional scan axes at the front):
        probe: 'x','y','mode_idx'
        object: 'x','y','mode_idx'
        positions: 'xy'
        '''
        PATTERN_LABELS = ['xy', 'detectorX', 'detectorY']
        in_labels = in_dataset[0].data_info.get('axis_labels') # this is a list of dictionarys
        existing_labels = [list(d.keys())[0] for d in in_labels] # this just gets the axes names
        logging.debug('The existing labels are:%s, we will remove:%s' % (existing_labels, PATTERN_LABELS))
        logging.debug('removing these labels from the list')
        core_labels_raw = [l for l in existing_labels if l not in PATTERN_LABELS] # removes them from the list
        core_labels = [l + '.' + in_labels[0][l] for l in core_labels_raw] # add the units in for the ones we are keeping
        # now we just have to add the new ones to this.
        trans_units = self.get_output_axis_units()

        probe_labels = list(core_labels) # take a copy
        probe_labels.extend(['mode_idx.number','x.' + trans_units, 'y.' + trans_units, ])
        logging.debug('the labels for the probe are:%s' % str(probe_labels))
        object_labels = list(core_labels)
        object_labels.extend(['mode_idx.number','x.' + trans_units, 'y.' + trans_units])
        logging.debug('the labels for the object are:%s' % str(object_labels))
        position_labels = list(core_labels)
        position_labels.extend(['xy.m','idx'])
        logging.debug('the labels for the positions are:%s' % str(position_labels))
        # now we also need this part of the shape of the data so...
        md = in_dataset[0].meta_data
        sh = tuple([len(md.get(l)) for l in core_labels_raw])
        return position_labels, probe_labels, object_labels, sh

    def set_probe_rotation_patterns(self, probe, rest_probe):
        try:
            rot_axis = probe.get_data_dimension_by_axis_label('rotation_angle', contains=True) # get the rotation axis
        except Exception as e:
            logging.warning(str(e) + 'we were looking for "rotation_angle"')
            logging.debug('This is not a tomography, so no time series for the probe')
        else:
            # print('the rotation axis is:%s' % str(rot_axis))
            probe_ts = {'core_dims':(rot_axis,),
                        'slice_dims':tuple(set(rest_probe) - set([rot_axis]))}
            probe.add_pattern("TIMESERIES", **probe_ts) # so we can FT the wiggles etc...
            # print('This is a tomography so I have added a TIMESERIES pattern to the probe') # the probe oscillates in time for each projection, set this as a time series pattern

    def set_probe_energy_patterns(self, probe, rest_probe):
        try:
            energy_axis = probe.get_data_dimension_by_axis_label('energy', contains=True) # get an energy axis
        except Exception as e:
            logging.warning(str(e) + 'we were looking for "energy"')
            logging.debug('This is not spectro-microscopy, so no spectrum/timeseries for the probe')
        else:
            probe_spec = {'core_dims':tuple(energy_axis), 'slice_dims':tuple(set(rest_probe) - set([energy_axis]))}
            probe.add_pattern("SPECTRUM", **probe_spec)
            probe.add_pattern("TIMESERIES", **probe_spec)
            logging.debug('This is probably spectro-microscopy so I have added a SPECTRUM pattern to the probe')
            logging.debug('I have also added a TIMESERIES pattern on the same axis, but be careful with what this means!') # the probe oscillates in time for each projection, set this as a time series pattern


    def set_projection_pattern(self, probe, rest_probe):
        probe_proj_core = tuple([rest_probe[idx] for idx in (-3, -2)]) # hard coded since we set them just above
        probe_slice = tuple(set(rest_probe) - set(probe_proj_core))
        probe_proj = {'core_dims':probe_proj_core, 'slice_dims':probe_slice}
        probe.add_pattern("PROJECTION", **probe_proj)
        logging.debug('have added a PROJECTION pattern')

    def set_object_energy_patterns(self, object_trans, rest_obj):
        try:
            energy_axis = object_trans.get_data_dimension_by_axis_label('energy', contains=True) # get an energy axis
        except Exception as e:
            logging.warning(str(e) + 'we were looking for "energy"')
            logging.debug('This is not spectro-microscopy, so no spectrum for the object')
        else:
            obj_spec = {'core_dims':tuple(energy_axis), 'slice_dims':tuple(set(rest_obj) - set([energy_axis]))}
            object_trans.add_pattern("SPECTRUM", **obj_spec)
            logging.debug('This is probably spectro-microscopy so I have added a SPECTRUM pattern to the object') # the probe oscillates in time for each projection, set this as a time series pattern


    def set_object_rotation_patterns(self, object_trans, rest_obj):
        try:
            rot_axis = object_trans.get_data_dimension_by_axis_label('rotation_angle', contains=True) # get the rotation axis
        except Exception as e:
            logging.warning(str(e) + 'we were looking for "rotation_angle"')
            logging.debug('This is not a tomography, so no sinograms for the object transmission')
        else:
            x_axis = object_trans.get_data_dimension_by_axis_label('x', contains=True) # get the x axis
            obj_sino = {'core_dims':(rot_axis, x_axis), 'slice_dims':tuple(set(rest_obj) - set((rot_axis, x_axis)))}
            object_trans.add_pattern("SINOGRAM", **obj_sino) # for the tomography
            logging.debug('This is a tomography so I have added a SINOGRAM pattern to the object transmission') # the probe oscillates in time for each projection, set this as a time series pattern
