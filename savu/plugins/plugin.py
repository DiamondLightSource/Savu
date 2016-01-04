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
.. module:: plugin
   :platform: Unix
   :synopsis: Base class for all plugins used by Savu

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""

import logging
import inspect

from savu.plugins import utils as pu
from savu.plugins.plugin_datasets import PluginDatasets


class Plugin(PluginDatasets):
    """
    The base class from which all plugins should inherit.
    """

    def __init__(self, name='Plugin'):
        super(Plugin, self).__init__()
        self.name = name
        self.parameters = {}
        self.parameters_types = {}

    def main_setup(self, exp, params):
        self.exp = exp
        self.set_parameters(params)
        self.set_plugin_datasets()
        self.setup()

        in_datasets, out_datasets = self.get_datasets()
        for data in in_datasets + out_datasets:
            data.finalise_patterns()

    def set_parameters_this_instance(self, indices):
        dims = set(self.multi_params_dict.keys())
        count = 0
        for dim in dims:
            info = self.multi_params_dict[dim]
            name = info['label'].split('_param')[0]
            self.parameters[name] = info['values'][indices[count]]
            count += 1

    def setup(self):
        """
        This method is first to be called after the plugin has been created.

        :param in_data: Input data object(set to "None" if this is a loader)
        :type in_data: savu.data.experiment
        :param out_data: The output data object
        :type out_data: savu.data.experiment
        """
        logging.error("set_up needs to be implemented")
        raise NotImplementedError("setup needs to be implemented")

    def populate_default_parameters(self):
        """
        This method should populate all the required parameters with default
        values.  it is used for checking to see if new parameter values are
        appropriate

        It makes use of the classes including parameter information in the
        class docstring such as this

        :param error_threshold: Convergence threshold. Default: 0.001.
        """
        for clazz in inspect.getmro(self.__class__)[::-1]:
            if clazz != object:
                full_description = pu.find_args(clazz)
                for item in full_description:
                    self.parameters[item['name']] = item['default']
                    self.parameters_types[item['name']] = item['dtype']

    def set_parameters(self, parameters):
        """
        This method is called after the plugin has been created by the
        pipeline framework

        :param parameters: A dictionary of the parameters for this plugin, or
            None if no customisation is required
        :type parameters: dict
        """
        self.parameters = {}
        self.parameters_types = {}
        self.populate_default_parameters()
        for key in parameters.keys():
            if key in self.parameters.keys():
                value = self.convert_multi_params(parameters[key], key)
                self.parameters[key] = value
            else:
                raise ValueError("Parameter " + key +
                                 "is not a valid parameter for plugin " +
                                 self.name)

    def convert_multi_params(self, value, key):
        dtype = self.parameters_types[key]
        if isinstance(value, unicode):
            if ';' in value:
                value = value.split(';')
                if type(value[0]) != dtype:
                    value = map(dtype, value)
                if len(value) > 1:
                    label = key + '_params.' + type(value[0]).__name__
                    self.multi_params_dict[len(self.multi_params_dict)] = \
                        {'label': label, 'values': value}
                    self.extra_dims.append(len(value))
        return value

    def get_parameters(self, name):
        return self.parameters[name]

    def pre_process(self):
        """
        This method is called after the plugin has been created by the
        pipeline framework as a pre-processing step

        :param exp: An experiment object, holding input and output datasets
        :type exp: experiment class instance
        """
        pass

    def process_frames(self, data, frame_list):
        """
        This method is called after the plugin has been created by the
        pipeline framework and forms the main processing step

        :param data: The input data object.
        :type data: savu.data.data_structures
        :param data: The output data object
        :type data: savu.data.data_structures
        :param processes: The number of processes which will be doing the work
        :type path: int
        :param path: The specific process which we are
        :type path: int
        """

        logging.error("process frames needs to be implemented")
        raise NotImplementedError("process needs to be implemented")

    def post_process(self):
        """
        This method is called after the process function in the pipeline
        framework as a post-processing step. All processes will have finished
        performing the main processing at this stage.

        :param exp: An experiment object, holding input and output datasets
        :type exp: experiment class instance
        """
        pass

    def clean_up(self):
        #self.organise_metadata()
        self.copy_meta_data()
        self.clean_up_plugin_data()
        #delete mapping dataset here
        self.delete_mappings()

    def delete_mappings(self):
        in_datasets = self.get_in_datasets()
        for data in in_datasets:
            if data.mapping:
                del self.exp.index['mapping'][data.get_name()]
                self.mapping = False

    def copy_meta_data(self):
        """
        Copy all metadata from input datasets to output datasets, except axis
        # data that is no longer valid.
        """
        remove_keys = self.remove_axis_data()
        in_meta_data, out_meta_data = self.get_meta_data()
        copy_dict = {}
        for mData in in_meta_data:
            temp = mData.get_dictionary().copy()
            copy_dict.update(temp)

        for i in range(len(out_meta_data)):
            temp = copy_dict.copy()
            for key in remove_keys[i]:
                if temp.get(key, None) is not None:
                    del temp[key]
            out_meta_data[i].get_dictionary().update(temp)

    def remove_axis_data(self):
        """
        Returns a list of meta_data entries corresponding to axis labels that
        are not copied over to the output datasets
        """
        in_datasets, out_datasets = self.get_datasets()
        all_in_labels = []
        for data in in_datasets:
            axis_keys = data.get_axis_label_keys()
            all_in_labels = all_in_labels + axis_keys

        remove_keys = []
        for data in out_datasets:
            axis_keys = data.get_axis_label_keys()
            remove_keys.append(set(all_in_labels).difference(set(axis_keys)))

        return remove_keys

    def clean_up_plugin_data(self):
        in_data, out_data = self.get_datasets()
        data_object_list = in_data + out_data
        for data in data_object_list:
            data.clear_plugin_data()

    def nInput_datasets(self):
        """
        The number of datasets required as input to the plugin

        :returns:  Number of input datasets

        """
        raise NotImplementedError("nInput_datasets needs to be implemented")

    def nOutput_datasets(self):
        """
        The number of datasets created by the plugin

        :returns:  Number of output datasets

        """
        raise NotImplementedError("nOutput_datasets needs to be implemented")

    def get_citation_information(self):
        """Gets the Citation Information for a plugin

        :returns:  A populated savu.data.plugin_info.CitationInfomration

        """
        return None
