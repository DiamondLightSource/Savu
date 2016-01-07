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
.. module:: tomography_loader
   :platform: Unix
   :synopsis: A class for loading tomography data using the standard loaders
   library.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

from savu.plugins.loaders.base_multi_modal_loader import BaseMultiModalLoader

from savu.plugins.utils import register_plugin


@register_plugin
class NxfluoLoader(BaseMultiModalLoader):
    """
    A class to load tomography data from an NXFluo file
    """
    def __init__(self, name='NxfluoLoader'):
        super(NxfluoLoader, self).__init__(name)

    def setup(self):
        """
         Define the input nexus file

        :param path: The full path of the NeXus file to load.
        :type path: str
        """
        import numpy as np
        data_str = '/instrument/fluorescence/data'
        data_obj, fluo_entry = self.multi_modal_setup('NXfluo', data_str)
        # the application meta data
        mData = data_obj.meta_data
        average = np.mean(np.mean(np.mean(data_obj.data, axis=0), axis=0),
                          axis=0)
        # and the energy axis
        energy = data_obj.backing_file[fluo_entry.name+'/data/energy'][...]
        mono_energy = data_obj.backing_file[fluo_entry.name +
                                            '/instrument/monochromator/energy'
                                            ].value
        monitor = data_obj.backing_file[fluo_entry.name +
                                        '/monitor/data'
                                        ].value
        mData.set_meta_data("energy", energy)
        # global since it is to do with the beam
        mData.set_meta_data("mono_energy", mono_energy)
        mData.set_meta_data("monitor", monitor)
        mData.set_meta_data("average", average)
        #and get the mono energy

        self.set_motors(data_obj, fluo_entry, 'fluo')
        rotation_angle = \
            data_obj.backing_file[fluo_entry.name + '/sample/theta']
        data_obj.meta_data.set_meta_data('rotation_angle', rotation_angle[...])

#         data_obj.set_axis_labels('rotation_angle.degrees',
#                                  'x.mm',
# #                                  'y.mm',
#                                  'energy.eV')

        self.add_patterns_based_on_acquisition(data_obj, 'fluo')

        data_obj.add_pattern("SPECTRUM", core_dir=(-1,),
                             slice_dir=range(len(data_obj.data.shape)-1))

        self.set_data_reduction_params(data_obj)
