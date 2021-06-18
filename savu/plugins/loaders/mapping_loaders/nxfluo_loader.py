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
.. module:: nxfluo_loader
   :platform: Unix
   :synopsis: A class for loading nxfluo data

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import numpy as np

from savu.plugins.loaders.mapping_loaders.base_multi_modal_loader \
    import BaseMultiModalLoader

from savu.plugins.utils import register_plugin


@register_plugin
class NxfluoLoader(BaseMultiModalLoader):
    def __init__(self, name='NxfluoLoader'):
        super(NxfluoLoader, self).__init__(name)

    def setup(self):
        path = 'instrument/fluorescence/data'
        data_obj, fluo_entry = \
            self.multi_modal_setup('NXfluo', path, self.parameters['name'])

        npts = data_obj.data.shape[self.get_motor_dims('None')[0]]
        gain = self.parameters["fluo_gain"]
        energy = np.arange(self.parameters["fluo_offset"], gain*npts, gain)
        mono_path = fluo_entry.name + '/instrument/monochromator/energy'
        mono_energy = data_obj.backing_file[mono_path][()]
        monitor_path = fluo_entry.name + '/monitor/data'
        monitor = data_obj.backing_file[monitor_path][()]

        data_obj.meta_data.set("energy", energy)
        data_obj.meta_data.set("mono_energy", mono_energy)
        data_obj.meta_data.set("monitor", monitor)
        data_obj.meta_data.set("average", np.ones(npts))

        slice_dir = tuple(range(len(data_obj.data.shape)-1))
        data_obj.add_pattern("SPECTRUM", core_dims=(-1,), slice_dims=slice_dir)

        self.set_data_reduction_params(data_obj)
