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
              
              
    def correction(self, data, dark, flat):
        dark = np.tile(dark, (data.shape[0], 1))
        flat = np.tile(flat, (data.shape[0], 1))
        data = (data-dark)/flat  # flat = (flat-dark) already calculated for efficiency
        data[data <= 0.0] = 1.0;
        return data
              

    @logmethod
    def process(self, data, output, processes, process, transport):
        """
        """
        transport.process(self, data, output, processes, process, [], "timeseries_correction_set_up")


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
        return "nbn"

    def output_dist(self):
        """
        The output DistArray distribution for this plugin is "bnn"
        (i.e. block in the first dimension)

        :returns:  DistArray distribution
        """
        return "nbn"