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
.. module:: framework_citations
   :platform: Unix
   :synopsis: Contains all framework citations.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""


def get_framework_citations():
    """ return a dictionary of CitationInformation objects """
    tools = FrameworkCitations().get_plugin_tools()
    return tools.get_citations()

from savu.plugins.plugin import Plugin

class FrameworkCitations(Plugin):
    def __init__(self, name="FrameworkCitations"):
        super(FrameworkCitations, self).__init__(name)