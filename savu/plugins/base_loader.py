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
.. module:: base_loader
   :platform: Unix
   :synopsis: A base class for loading data

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

from savu.plugins.plugin import Plugin


class BaseLoader(Plugin):
    """
    A base plugin from which all data loader plugins should inherit.
    """

    def __init__(self, name='BaseLoader'):
        self.hits = []
        self.application = None
        super(BaseLoader, self).__init__(name)

    def get_NXapp(self, ltype, nx_file, entry):
        self.application = ltype
        print "***Application is ", ltype
        nx_file[entry].visititems(self._visit_NXapp)
        return self.hits

    def _visit_NXapp(self, name, obj):
        if "NX_class" in obj.attrs.keys():
            if obj.attrs["NX_class"] in ["NXentry", "NXsubentry"]:
                if "definition" in obj.keys():
                    if obj["definition"].value == self.application:
                        self.hits.append(obj)
