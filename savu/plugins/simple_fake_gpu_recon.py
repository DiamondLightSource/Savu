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
from savu.plugins.plugin import Plugin

"""
.. module:: simple_fake_gpu_recon
   :platform: Unix
   :synopsis: A simple implementation a reconstruction routine for testing
       purposes

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""
from savu.plugins.gpu_plugin import GpuPlugin
from savu.plugins.simple_recon import SimpleRecon


class SimpleFakeGpuRecon(Plugin, GpuPlugin):
    """
    A Plugin to apply a simple reconstruction with no dependancies
    """

    def __init__(self):
        super(SimpleFakeGpuRecon, self).__init__("SimpleFakeGpuRecon")
        self.sr = SimpleRecon()

    def populate_default_parameters(self):
        self.sr.populate_default_parameters()
        self.parameters = self.sr.parameters

    def process(self, data, output, processes, process):
        """
        """
        return self.sr.process(data, output, processes, process)

    def required_data_type(self):
        """
        The input for this plugin is ProjectionData

        :returns:  ProjectionData
        """
        return self.sr.required_data_type()

    def output_data_type(self):
        """
        The output of this plugin is VolumeData

        :returns:  VolumeData
        """
        return self.sr.output_data_type()

    def get_citation_inforamtion(self):
        return self.sr.get_citation_inforamtion()
