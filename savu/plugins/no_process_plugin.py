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
.. module:: no_process_plugin
   :platform: Unix
   :synopsis: Plugin to test loading and saving without processing
.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""
from savu.plugins.plugin import Plugin
from savu.plugins.utils import register_plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin


@register_plugin
class NoProcessPlugin(Plugin, CpuPlugin):
    """
    The base class from which all plugins should inherit.
    :param in_datasets: A list of the dataset(s) to process. Default: [].
    :param out_datasets: A list of the dataset(s) to process. Default: [].
    """

    def __init__(self):
        super(NoProcessPlugin, self).__init__("NoProcessPlugin")

    def process(self, exp, transport, params):

        in_data = self.get_data_objects(exp.index, "in_data")
        out_data = self.get_data_objects(exp.index, "out_data")

        in_data = in_data[0]
        out_data = out_data[0]

        print "performing the processing"
        slice_list = in_data.single_slice_list() #  I changed this to single_slice_list, from get_slice_list since for some reason get_slice_list wasn't found. adp 
        for sl in slice_list:
            temp = in_data.data[sl]
            out_data.data[sl] = temp

        print in_data.data.shape, out_data.data.shape

    def setup(self, experiment):
        """
        Initial setup of all datasets required as input and output to the 
        plugin.  This method is called before the process method in the plugin
        chain.  
        """

        chunk_size = self.get_max_frames()

        # get all input dataset objects
        in_data = experiment.index["in_data"]
        for key, data in in_data.iteritems():  # [in_data_list[0]]
            # set all input data patterns
            # have changed this to work on the first element of the pattern
            # list rather SINOGRAM, since some datasets don't have a singoram
            # adp
            data.set_current_pattern_name(data.get_patterns().keys()[0])
            # set frame chunk
            data.set_nFrames(chunk_size)

            out_data = experiment.create_data_object("out_data", key)

            out_data.copy_patterns(data.get_patterns())

            out_data.meta_data.copy_dictionary(data.meta_data.get_dictionary(),
                                               rawFlag=True)

            out_data.set_current_pattern_name(data.get_patterns().keys()[0])
            out_data.set_shape(data.get_shape())
            # set frame chunk
            out_data.set_nFrames(chunk_size)

    def nInput_datasets(self):
        return 1

    def nOutput_datasets(self):
        return 1

    def get_max_frames(self):
        return 8
