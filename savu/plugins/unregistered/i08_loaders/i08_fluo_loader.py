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
.. module:: i08_fluo_loader
   :platform: Unix
   :synopsis: A class for loading I08s xrf data

.. moduleauthor:: Aaron Parsons <scientificsoftware@diamond.ac.uk>

"""

from savu.plugins.loaders.base_loader import BaseLoader
import numpy as np
from savu.plugins.utils import register_plugin
import logging
import h5py as h5

#@register_plugin
class I08FluoLoader(BaseLoader):
    def __init__(self, name='I08FluoLoader'):
        super(I08FluoLoader, self).__init__(name)

    def setup(self):
        """
         Define the input nexus file

        :param path: The full path of the NeXus file to load.
        :type path: str
        """

        det_path = 'entry/xmapMca/'
        exp = self.exp
        data_obj = exp.create_data_object("in_data", 'fluo')
        data_obj.backing_file = \
            h5.File(exp.meta_data.get("data_file"), 'r')
        data_obj.data = data_obj.backing_file[det_path+'/data']
        data_obj.set_shape(data_obj.data.shape)
        entry = h5.File(exp.meta_data.get("data_file"),'r')[det_path]
        scan_axis = entry.attrs['axes']
        scan_axis = [str(ix) for ix in scan_axis]
        if list(scan_axis).count('.')>1:
            logging.debug("Detector channels not summed.")

            for axis in scan_axis:
                if axis != '.':
                    axis_data = entry[str(axis)][...]
                    data_obj.meta_data.set(axis,axis_data)
            scan_axis[-2] = 'idx'
            scan_axis[-1] = 'energy'
            scan_axis = [ix +'.units' for ix in scan_axis]

        else:
            logging.debug("Detector channels summed.")
            for axis in scan_axis:
                if axis != '.':
                    axis_data = entry[str(axis)][...]

                    data_obj.meta_data.set(axis,axis_data)
            scan_axis[-1] = 'energy'
            scan_axis = [ix +'.units' for ix in scan_axis]

        mono_energy = h5.File(exp.meta_data.get("data_file"))[self.parameters['mono_path']][...]

        data_obj.meta_data.set('mono_energy',mono_energy)
        # axis label
#         print "the labels are:"+str(labels)
        data_obj.set_axis_labels(*tuple(scan_axis))

        dims = list(range(len(data_obj.get_shape())))
        spec_core = (-1,) # it will always be this
#         print spec_core

        spec_slice = tuple(dims[:-1])

        logging.debug("is a spectrum")
        logging.debug("the spectrum cores are:"+str(spec_core))
        logging.debug("the spectrum slices are:"+str(spec_slice))
        data_obj.add_pattern("SPECTRUM", core_dims=spec_core,
                             slice_dims=spec_slice)


        positions_label = (data_obj.get_data_dimension_by_axis_label('X', contains=True),data_obj.get_data_dimension_by_axis_label('Y', contains=True))

        data_obj.add_pattern("PROJECTION", core_dims=positions_label, slice_dims=tuple(set(dims)-set(positions_label)))

        self.set_data_reduction_params(data_obj)
