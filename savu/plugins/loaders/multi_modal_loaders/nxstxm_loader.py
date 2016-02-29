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
.. module:: nxstxm_loader
   :platform: Unix
   :synopsis: A class for loading nxstxm data

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

from savu.plugins.loaders.base_multi_modal_loader import BaseMultiModalLoader

from savu.plugins.utils import register_plugin


@register_plugin
class NxstxmLoader(BaseMultiModalLoader):
    """
    A class to load tomography data from an NXstxm file
    """

    def __init__(self, name='NxstxmLoader'):
        super(NxstxmLoader, self).__init__(name)

    def setup(self):
        """
         Define the input nexus file

        :param path: The full path of the NeXus file to load.
        :type path: str
        """

        data_str = '/instrument/detector/data'
        data_obj, stxm_entry = self.multi_modal_setup('NXstxm', data_str)
        mono_energy = data_obj.backing_file[
            stxm_entry.name + '/instrument/monochromator/energy']
        self.exp.meta_data.set_meta_data("mono_energy", mono_energy)
        self.set_motors(data_obj, stxm_entry, 'stxm')
        rotation_angle = \
            data_obj.backing_file[stxm_entry.name + '/sample/theta'].value
        if rotation_angle.ndim > 1:
            rotation_angle = rotation_angle[:, 0]
        data_obj.meta_data.set_meta_data('rotation_angle', rotation_angle)
 
        data_obj.set_axis_labels('rotation_angle.degrees',
                                 'y.mm',
                                 'x.mm'
                                    )
        print "NXstxm"
        self.add_patterns_based_on_acquisition(data_obj, 'stxm')
        self.set_data_reduction_params(data_obj)
