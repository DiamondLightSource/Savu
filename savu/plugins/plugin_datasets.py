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
.. module:: plugin_datasets
   :platform: Unix
   :synopsis: Base class of plugin containing all dataset related functions

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

from savu.data.data_structures import PluginData


class PluginDatasets(object):
    """
    The base class from which all plugins should inherit.
    """

    def __init__(self, name='PluginDatasets'):
        super(PluginDatasets, self).__init__()
        self.exp = None
        self.data_objs = {}
        self.variable_data_flag = False
        self.multi_params_dict = {}
        self.extra_dims = []

    def get_data_objects(self, dtype):
        data_list = self.parameters[dtype + 'sets']
        data_objs = []
        for data in data_list:
            data_objs.append(self.exp.index[dtype][data])
        return data_objs

    def set_in_datasets(self):
        return self.get_data_objects('in_data')

    def set_out_datasets(self):
        try:
            out_data = self.get_data_objects('out_data')
        except KeyError:
            out_data = []
            for data in self.parameters['out_datasets']:
                self.exp.create_data_object("out_data", data)
            out_data = self.get_data_objects('out_data')
        for data in out_data:
            data.extra_dims = self.extra_dims
        return out_data

    def get_plugin_data(self, data_list):
        pattern_list = []
        for data in data_list:
            pattern_list.append(PluginData(data))
            pattern_list[-1].extra_dims = self.extra_dims
            pattern_list[-1].multi_params_dict = self.multi_params_dict
        return pattern_list

    def set_plugin_datasets(self):
        """
        Convert in/out_dataset strings to objects and create PluginData objects
        for each.
        """
        self.parameters['in_datasets'] = self.set_in_datasets()
        self.parameters['out_datasets'] = self.set_out_datasets()
        self.parameters['plugin_in_datasets'] = \
            self.get_plugin_data(self.parameters['in_datasets'])
        self.parameters['plugin_out_datasets'] = \
            self.get_plugin_data(self.parameters['out_datasets'])

    def get_plugin_in_datasets(self):
        return self.parameters['plugin_in_datasets']

    def get_plugin_out_datasets(self):
        return self.parameters['plugin_out_datasets']

    def get_plugin_datasets(self):
        return self.get_plugin_in_datasets(), self.get_plugin_out_datasets()

    def get_in_datasets(self):
        return self.parameters['in_datasets']

    def get_out_datasets(self):
        return self.parameters['out_datasets']

    def get_datasets(self):
        return self.get_in_datasets(), self.get_out_datasets()

    def get_in_meta_data(self):
        return self.set_meta_data(self.parameters['in_datasets'], 'in_data')

    def get_out_meta_data(self):
        return self.set_meta_data(self.parameters['out_datasets'], 'out_data')

    def get_meta_data(self):
        return self.get_in_meta_data(), self.get_out_meta_data()

    def set_meta_data(self, data_list, dtype):
        meta_data = []
        for data in data_list:
            meta_data.append(data.meta_data)
        return meta_data

    def set_unknown_shape(self, data, key):
        try:
            return (len(data.meta_data.get_meta_data(key)),)
        except KeyError:
            return (0,)
