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
.. module:: plugin_template7
   :platform: Unix
   :synopsis: A template to create a plugin that reduces the data dimensions.

.. moduleauthor:: Developer Name <email@address.ac.uk>

"""

import copy
import numpy as np

from savu.plugins.plugin import Plugin
from savu.plugins.utils import register_plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin


@register_plugin
class PluginTemplate7(Plugin, CpuPlugin):

    def __init__(self):
        super(PluginTemplate7, self).__init__('PluginTemplate7')

    def nInput_datasets(self):
        return 1

    def nOutput_datasets(self):
        return 1

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()

        #=================== populate output dataset ==========================
        # Due to the increase in dimensions, the out_dataset will have
        # different axis_labels, patterns and shape to the in_dataset and
        # these will need to be defined.
        # For more information about the syntax used here see:
        # http://savu.readthedocs.io/en/latest/api_plugin/savu.data.data_structures.data_create

        # AMEND THE PATTERNS: The output dataset will have one dimension more
        # than the in_dataset, so add another slice dimensions the patterns
        add_dim = str(len(in_dataset[0].get_shape()))
        patterns = {in_dataset[0]: ['.'.join(['*', add_dim])]}

        # AMEND THE AXIS LABELS: Add an extra slice dim to all axis labels
        axis_list = ['.'.join(['~' + add_dim, self.parameters['axis_label'],
                            self.parameters['axis_unit']])]
        axis_labels = {in_dataset[0]: axis_list}

        # AMEND THE SHAPE: Remove the two unrequired dimensions from the
        # original shape and add a new dimension shape.
        self.rep = self.parameters['axis_len']
        shape = list(in_dataset[0].get_shape())
        shape.append(self.rep)

        # populate the output dataset
        out_dataset[0].create_dataset(
                patterns=patterns,
                axis_labels=axis_labels,
                shape=tuple(shape))

        slice_dim = (out_dataset[0].get_data_dimension_by_axis_label(
                'detector_y'),)
        core_dims = set(range(0, len(shape))).difference(set(slice_dim))
        sinomovie = {'core_dims': tuple(core_dims), 'slice_dims': slice_dim}
        out_dataset[0].add_pattern("SINOMOVIE", **sinomovie)
        print(out_dataset[0].get_data_patterns()['SINOMOVIE'])

        #================== populate plugin datasets ==========================
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('PROJECTION', 'single')
        out_pData[0].plugin_data_setup('PROJECTION', self.rep,
                 slice_axis=self.parameters['axis_label'])
        #======================================================================

    def pre_process(self):
        self.ndims = len(self.get_plugin_in_datasets()[0].get_shape())

    def process_frames(self, data):
        rep_mat = np.repeat(
                np.expand_dims(data[0], self.ndims), self.rep, axis=self.ndims)
        return rep_mat

    def post_process(self):
        pass