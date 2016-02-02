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
.. module:: dimension_adder
   :platform: Unix
   :synopsis: adds a dimension to the dataset of length 1
.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""
from savu.plugins.plugin import Plugin
from savu.plugins.utils import register_plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin


@register_plugin
class DimensionAdder(Plugin, CpuPlugin):
    """
    The base class from which all plugins should inherit.
    :param in_datasets: A list of the dataset(s) to process. Default: [].
    :param out_datasets: A list of the dataset(s) to process. Default: [].
    :param dimension: The position to add the dimension. Default: 0.
    :param add_pattern: pattern to add with core directions. Default: ['PROJECTION',(1,2)].
    """

    def __init__(self):
        super(DimensionAdder, self).__init__("DimensionAdder")

    def process_frames(self, data, frame_list):

        return data[0]

    def setup(self):
        """
        Initial setup of all datasets required as input and output to the
        plugin.  This method is called before the process method in the plugin
        chain.
        """
        in_dataset, out_dataset = self.get_datasets()
        sh = in_dataset[0].get_shape()
        # now to add the dimension
        position = self.parameters['dimension']
        new_sh = sh[:position] + (1,) + sh[position:]
        labels = in_dataset[0].data_info.get_meta_data('axis_labels')
        labels.insert(position, "idx.unit")
        old_patterns = in_dataset[0].get_data_patterns()
        pnames = old_patterns.keys()
        for i in pnames:
            print i
            curr_slicedir = old_patterns[i]['slice_dir']
            print "with slice dirs:"+str(curr_slicedir)+str(type(curr_slicedir))
            old_patterns[i]['slice_dir'] = curr_slicedir + (position,)

        out_dataset[0].create_dataset(patterns={in_dataset[0]: old_patterns},
                                      axis_labels=labels,
                                      shape=new_sh)
        pdims = self.parameters['add_pattern']
        slice_dir = tuple(set(range(len(new_sh))) - set(pdims[1]))
        new_pattern = {'core_dir': pdims[1], 'slice_dir': slice_dir}
        out_dataset[0].add_pattern(pdims[0], **new_pattern)
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('DIFFRACTION', self.get_max_frames())
        out_pData[0].plugin_data_setup('DIFFRACTION', self.get_max_frames())

    def nInput_datasets(self):
        return 1

    def nOutput_datasets(self):
        return 1

    def get_max_frames(self):
        return 1
