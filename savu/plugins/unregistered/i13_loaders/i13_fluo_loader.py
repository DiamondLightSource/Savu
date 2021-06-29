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
.. module:: i13_fluo_loader
   :platform: Unix
   :synopsis: A class for loading xrf data

.. moduleauthor:: Aaron Parsons <scientificsoftware@diamond.ac.uk>

"""

from savu.plugins.loaders.base_loader import BaseLoader
import numpy as np
from savu.plugins.utils import register_plugin
import logging
import h5py


@register_plugin
class I13FluoLoader(BaseLoader):
    def __init__(self, name='I13FluoLoader'):
        super(I13FluoLoader, self).__init__(name)

    def setup(self):
        """
         Define the input nexus file

        :param path: The full path of the NeXus file to load.
        :type path: str
        """

        data_str = 'entry1/instrument/xmapMca/fullSpectrum'
        exp = self.exp
        data_obj = exp.create_data_object("in_data", 'fluo')
        data_obj.backing_file = \
            h5py.File(exp.meta_data.get("data_file"), 'r')
        data_obj.data = data_obj.backing_file[data_str]
        data_obj.set_shape(data_obj.data.shape)
        npts = data_obj.data.shape[-1]
        gain = self.parameters["fluo_gain"]
        energy = np.arange(self.parameters["fluo_offset"], gain*npts, gain)
        data_obj.meta_data.set("energy", energy)
        labels = []
        ### set the x
        rotation_angle = None
        if self.parameters['is_tomo']:
            rotation_angle = np.arange(self.parameters['theta_start'],self.parameters['theta_end'], self.parameters['theta_step'])
            labels.append('rotation_angle.degrees')
            data_obj.meta_data.set('rotation_angle', rotation_angle)
        x = \
            data_obj.backing_file['entry1/instrument/lab_sxy/lab_sx'][()]
        data_obj.meta_data.set('x', x)
        # axis label

        ### set the y
        y = \
            data_obj.backing_file['entry1/instrument/lab_sxy/lab_sy'][()]
        pos = np.zeros((2,len(y[0])))
        pos[0,:] = x[0]
        pos[1,:] = y[0]
        data_obj.meta_data.set('xy', pos)
        # axis label
        labels.append('xy.microns')
        labels.append('idx.idx')
#         labels.append('y.microns')
        # now set them
        labels.extend(['spectra.counts'])
#         print "the labels are:"+str(labels)
        data_obj.set_axis_labels(*tuple(labels))


        dims = list(range(len(data_obj.get_shape())))
        spec_core = (-1,) # it will always be this
#         print spec_core

        spec_slice = tuple(dims[:-1])
#         print spec_slice
        logging.debug("is a spectrum")
        logging.debug("the spectrum cores are:"+str(spec_core))
        logging.debug("the spectrum slices are:"+str(spec_slice))
        data_obj.add_pattern("SPECTRUM", core_dims=spec_core,
                             slice_dims=spec_slice)
        logging.debug("the spectrum slices are:"+str(spec_slice))
        data_obj.add_pattern("SPECTRUM_STACK", core_dims=spec_core[:-1],
                             slice_dims=(-2,)+spec_slice)



        positions_label = (data_obj.get_data_dimension_by_axis_label('xy', contains=True),)
        rotation_label = (data_obj.get_data_dimension_by_axis_label('rotation_angle', contains=True),)

        data_obj.add_pattern("PROJECTION", core_dims=positions_label, slice_dims=tuple(set(dims)-set(positions_label)))
        sino_cores = rotation_label + positions_label
        data_obj.add_pattern("SINOGRAM", core_dims=sino_cores, slice_dims = tuple(set(dims)-set(sino_cores)))


        data_obj.add_pattern("4D_SCAN", core_dims=tuple(set(dims)-set(rotation_label)),
                        slice_dims=rotation_label)

#         data_obj.add_pattern("SINOGRAM", core_dir=(0,1),
#                      slice_dir=(2,3))
#         data_obj.add_pattern("PROJECTION", core_dir=(0,3),
#                      slice_dir=(1,2))
        self.set_data_reduction_params(data_obj)
