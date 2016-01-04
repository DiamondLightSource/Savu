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
import logging
import h5py

@register_plugin
class NxmonitorLoader(BaseMultiModalLoader):
    """
    A class to load tomography data from an NXmonitor file
    """

    def __init__(self, name='NxmonitorLoader'):
        super(NxmonitorLoader, self).__init__(name)

    def setup(self):
        """
         Define the input nexus file

        :param path: The full path of the NeXus file to load.
        :type path: str
        """

        data_str = '/monitor/data'
        data_obj, stxm_entry = self.multi_modal_setup('NXstxm', data_str)
        mono_energy = data_obj.backing_file[
            stxm_entry.name + '/instrument/monochromator/energy']
        self.exp.meta_data.set_meta_data("mono_energy", mono_energy)
        self.set_motors(data_obj, stxm_entry, 'stxm')
        rotation_angle = \
            data_obj.backing_file[stxm_entry.name + '/sample/theta']
        data_obj.meta_data.set_meta_data('rotation_angle', rotation_angle[...])
        data_obj.set_axis_labels('rotation_angle.degrees',
                                 'x.mm')#,
#                                  'y.mm')
        self.add_patterns_based_on_acquisition(data_obj, 'stxm')

    def multi_modal_setup(self, ltype, data_str):
        # Im overloading this, purely because I want to change the name- fix this in the future
        exp = self.exp
        data_obj = exp.create_data_object("in_data", "NXmonitor")
        data_obj.backing_file = \
            h5py.File(exp.meta_data.get_meta_data("data_file"), 'r')
        logging.debug("Creating file '%s' '%s'_entry",
                      data_obj.backing_file.filename, ltype)
        # now lets extract the entry so we can figure out our geometries!
        entry = self.get_NXapp(ltype, data_obj.backing_file, 'entry1/')[0]
        logging.debug(str(entry))

        data_obj.data = data_obj.backing_file[entry.name + data_str]
        data_obj.set_shape(data_obj.data.shape)
        return data_obj, entry
