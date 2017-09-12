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
# $Id: dezing_filter.py 467 2016-02-16 11:40:42Z kny48981 $


"""
.. module:: plugin_template
   :platform: Unix
   :synopsis: A template to create a plugin

.. moduleauthor:: Developer Name <email@address.ac.uk>

"""

from savu.plugins.base_filter import BaseFilter
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin


#@register_plugin
class PluginTemplate(BaseFilter, CpuPlugin):
    """
    A plugin template

    :param example: Example of a plugin parameter. Default: None.

    """

    def __init__(self):
        super(PluginTemplate, self).__init__('PluginTemplate')