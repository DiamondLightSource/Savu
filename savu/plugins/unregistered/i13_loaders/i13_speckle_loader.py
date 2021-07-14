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
.. module:: i13_speckle_loader
   :platform: Unix
   :synopsis: A class for loading I13's speckle tracking data

.. moduleauthor:: Aaron Parsons <scientificsoftware@diamond.ac.uk>

"""

from savu.plugins.loaders.base_loader import BaseLoader
from savu.plugins.utils import register_plugin
import h5py

#@register_plugin
class I13SpeckleLoader(BaseLoader):
    """
    A class to load tomography data from an NXstxm file
    :param signal_key: Path to the signals.Default:'/entry/sample'.
    :param reference_key: Path to the reference.Default:'/entry/reference'.
    :param angle_key: Path to the reference.Default:'/entry/theta'.
    :param dataset_names: the output sets.Default: ['signal','reference'].
    """

    def __init__(self, name='I13SpeckleLoader'):
        super(I13SpeckleLoader, self).__init__(name)

    def setup(self):
        """

        """
        name_signal, name_reference = self.parameters['dataset_names']

        exp = self.exp
        signal = exp.create_data_object("in_data", name_signal)
        signal.backing_file = h5py.File(exp.meta_data.get("data_file"), 'r')

        reference = exp.create_data_object("in_data", name_reference)
        reference.backing_file = h5py.File(exp.meta_data.get("data_file"), 'r')

        signal.data = signal.backing_file[self.parameters['signal_key']]
        signal.set_shape(signal.data.shape)
        reference.data = signal.backing_file[self.parameters['reference_key']]
        reference.set_shape(signal.data.shape)

        signal.set_axis_labels('rotation_angle.degrees',
                               'idx.units',
                               'detector_y.pixel',
                               'detector_x.pixel')

        reference.set_axis_labels('rotation_angle.degrees',
                                  'idx.units',
                                  'detector_y.pixel',
                                  'detector_x.pixel')

        theta = signal.backing_file[self.parameters['angle_key']][0]
        signal.meta_data.set('rotation_angle', theta)

        ## hard code this stuff for now since it's probably going to change anyway
        signal.add_pattern("PROJECTION", core_dims=(-2,-1), slice_dims=(0,1))

        signal.add_pattern("SINOGRAM", core_dims=(0,-2), slice_dims=(1,-1))

        signal.add_pattern("4D_SCAN", core_dims=(1,-2,-1),
                        slice_dims=(0,))
  
        reference.add_pattern("PROJECTION", core_dims=(-2,-1), slice_dims=(0,1))

        reference.add_pattern("SINOGRAM", core_dims=(0,-1), slice_dims=(1,-1))

        reference.add_pattern("4D_SCAN", core_dims=(1,-2,-1),
                        slice_dims=(0,))
        self.set_data_reduction_params(signal)
        self.set_data_reduction_params(reference)
