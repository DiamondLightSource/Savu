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
.. module:: plugin_template3
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
class PluginTemplate3(Plugin, CpuPlugin):

    def __init__(self):
        super(PluginTemplate3, self).__init__('PluginTemplate3')

    def nInput_datasets(self):
        return 1

    def nOutput_datasets(self):
        return 1

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()

        #=================== populate output dataset ==========================
        # Due to the reduction in dimensions, the out_dataset will have
        # different axis_labels, patterns and shape to the in_dataset and
        # these will need to be defined.
        # For more information about the syntax used here see:
        # http://savu.readthedocs.io/en/latest/api_plugin/savu.data.data_structures.data_create

        # AMEND THE PATTERNS: The output dataset will have one dimension less
        # than the in_dataset, so remove the final slice dimension from any
        # patterns you want to keep.
        rm_dim = str(in_dataset[0].get_data_patterns()
                     ['SINOGRAM']['slice_dims'][-1])
        patterns = ['SINOGRAM.' + rm_dim, 'PROJECTION.' + rm_dim]

        # AMEND THE AXIS LABELS: Find the dimensions to remove using their
        # axis_labels to ensure the plugin is as generic as possible and will
        # work for data in all orientations.
        axis_labels = copy.copy(in_dataset[0].get_axis_labels())
        rm_labels = ['detector_x', 'detector_y']
        rm_dims = sorted([in_dataset[0].get_data_dimension_by_axis_label(a)
                          for a in rm_labels])[::-1]
        for d in rm_dims:
            del axis_labels[d]
        # Add a new axis label to the list
        axis_labels.append({'Q': 'Angstrom^-1'})

        # AMEND THE SHAPE: Remove the two unrequired dimensions from the
        # original shape and add a new dimension shape.
        shape = list(in_dataset[0].get_shape())
        for d in rm_dims:
            del shape[d]
        shape += (self.get_parameters('num_bins'),)

        # populate the output dataset
        out_dataset[0].create_dataset(
                patterns={in_dataset[0]: patterns},
                axis_labels=axis_labels,
                shape=tuple(shape))

        # ASSOCIATE AN EXTRA PATTERN WITH THE DATASET: SINOGRAM and PROJECTION
        # patterns are already asssociated with the output dataset, but add 
        # another one.
        spectrum = \
            {'core_dims': (-1,), 'slice_dims': tuple(range(len(shape)-1))}
        out_dataset[0].add_pattern("SPECTRUM", **spectrum)
        #======================================================================

        #================== populate plugin datasets ==========================
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('DIFFRACTION', 'single')
        out_pData[0].plugin_data_setup('SPECTRUM', 'single')
        #======================================================================

    def pre_process(self):
        pass

    def process_frames(self, data):
        # do some processing here
        return np.arange(self.parameters['num_bins'])

    def post_process(self):
        pass
