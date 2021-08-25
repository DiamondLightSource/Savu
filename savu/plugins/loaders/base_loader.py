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
   :synopsis: A base class for loader plugins

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

from savu.plugins.plugin import Plugin

class BaseLoader(Plugin):
    def __init__(self, name='BaseLoader'):
        super(BaseLoader, self).__init__(name)
        self.hits = []
        self.application = None
        self.reduction_flag = False

    def _main_setup(self):
        """
        Overwrites the main_setup function in plugin.py as the loader is a
        special case of plugin that doesn't require setup of in/out_datasets
        """
        data_obj = self.setup()
        if data_obj and not self.reduction_flag:
            self.set_data_reduction_params(data_obj)

    def get_experiment(self):
        return self.exp

    def set_data_reduction_params(self, data_obj):
        pDict = self.parameters
        self.data_mapping()
        data_obj.get_preview().set_preview(pDict['preview'], load=True)
        # update axis labels
        #data_obj.amend_axis_label_values()
        # set previewing for Related datasets
        #for data in data_obj.related.values():
            # find common axes
        #    pass
        # update axis labels for Related datasets
        self.reduction_flag = True

    def get_NXapp(self, ltype, nx_file, entry):
        '''
        finds an application definition in a nexus file
        '''
        self.application = ltype
        nx_file[entry].visititems(self._visit_NXapp)
        return self.hits

    def _visit_NXapp(self, name, obj):
        if "NX_class" in list(obj.attrs.keys()):
            if obj.attrs["NX_class"].decode("ascii") in ["NXentry", "NXsubentry"]:
                if "definition" in list(obj.keys()):
                    if obj["definition"][()].decode("ascii") == self.application:
                        self.hits.append(obj)

    def get_NXdata(self, nx_file, detector_list):
        nx_file['/'].visititems(self._visit_NXdata)
        for detector in detector_list:
            for nxdata in self.nxdata:
                if detector in list(nxdata.keys()) or detector in \
                        str(nxdata.name).split('/'):
                    self.hits.append(nxdata)
        return self.hits

    def _visit_NXdata(self, name, obj):
        if "NX_class" in list(obj.attrs.keys()):
            if obj.attrs["NX_class"].decode("ascii") in ["NXdata"]:
                self.hits.append(obj)

    def data_mapping(self):
        pass
