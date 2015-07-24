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
.. module:: Timeseries_field_corrections
   :platform: Unix
   :synopsis: A Plugin to apply a simple dark and flatfield correction to some
       raw timeseries data

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""
from savu.data.structures import RawTimeseriesData, ProjectionData
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.plugin import Plugin
from savu.core.utils import logmethod

import numpy as np

from savu.plugins.utils import register_plugin


@register_plugin
class TimeseriesFieldCorrections(Plugin, CpuPlugin):
    """
    A Plugin to apply a simple dark and flatfield correction to some
    raw timeseries data
    """

    def __init__(self):
        super(TimeseriesFieldCorrections,
              self).__init__("TimeseriesFieldCorrections")

    @logmethod
    def process(self, data, output, processes, process, transport):
        """
        """
        image_key = data.image_key[...]
        # pull out the average dark and flat data
        dark = None
        try:
            dark = np.mean(data.data[image_key == 2, :, :], 0)
        except:
            dark = np.zeros((data.data.shape[1], data.data.shape[2]))
        flat = None
        try:
            flat = np.mean(data.data[image_key == 1, :, :], 0)
        except:
            flat = np.ones((data.data.shape[1], data.data.shape[2]))
        # shortcut to reduce processing
        flat = flat - dark        
        flat[flat == 0.0] = 1
        
        params = [dark, flat]
        transport.process(self, data, output, processes, process, 
                          params, "timeseries_correction_set_up")


    def required_data_type(self):
        """
        The input for this plugin is RawTimeseriesData

        :returns:  RawTimeseriesData
        """
        return RawTimeseriesData

    def output_data_type(self):
        """
        The output of this plugin is ProjectionData

        :returns:  ProjectionData
        """
        return ProjectionData

    def input_dist(self):
        """
        The input DistArray distribution for this plugin is "bnn"
        (i.e. block in the first dimension)

        :returns:  DistArray distribution
        """
        return "bnn"

    def output_dist(self):
        """
        The output DistArray distribution for this plugin is "bnn"
        (i.e. block in the first dimension)

        :returns:  DistArray distribution
        """
        return "bnn"