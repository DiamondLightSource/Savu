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
import numpy as np

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
        self.chunk = False

    def _main_setup(self, exp, params):
        """ Performs all the required plugin setup.

        It sets the experiment, then the parameters and replaces the
        in/out_dataset strings in ``self.parameters`` with the relevant data
        objects. It then creates PluginData objects for each of these datasets.

        :param Experiment exp: The current Experiment object.
        :params dict params: Parameter values.
        """
        self.exp = exp
        self._set_parameters(params)
        self._set_plugin_datasets()
        self.setup()

        in_datasets, out_datasets = self.get_datasets()
        for data in in_datasets + out_datasets:
            data._finalise_patterns()

    def _set_parameters_this_instance(self, indices):
        """ Determines the parameters for this instance of the plugin, in the
        case of parameter tuning.

        param np.ndarray indices: the index of the current value in the
            parameter tuning list.
        """
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
        It determines input/output datasets and plugin specific dataset
        information such as the pattern (e.g. sinogram/projection).
        """
        logging.error("set_up needs to be implemented")
        raise NotImplementedError("setup needs to be implemented")

    def _populate_default_parameters(self):
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

    def _set_parameters(self, parameters):
        """
        This method is called after the plugin has been created by the
        pipeline framework.  It replaces ``self.parameters`` default values
        with those given in the input process list.

        :param dict parameters: A dictionary of the parameters for this plugin,
        or None if no customisation is required.
        """
        self.parameters = {}
        self.parameters_types = {}
        self._populate_default_parameters()
        for key in parameters.keys():
            if key in self.parameters.keys():
                value = self.__convert_multi_params(parameters[key], key)
                self.parameters[key] = value
            else:
                raise ValueError("Parameter " + key +
                                 "is not a valid parameter for plugin " +
                                 self.name)

    def __convert_multi_params(self, value, key):
        """ Set up parameter tuning.

        Convert parameter value to a list if it uses parameter tuning and set
        associated parameters, so the framework knows the new size of the data
        and which plugins to re-run.
        """
        dtype = self.parameters_types[key]
        if isinstance(value, str) and ';' in value:
            value = value.split(';')
            if ":" in value[0]:
                seq = value[0].split(':')
                seq = [eval(s) for s in seq]
                value = list(np.arange(seq[0], seq[1], seq[2]))
            if type(value[0]) != dtype:
                value = map(dtype, value)
            if len(value) > 1:
                label = key + '_params.' + type(value[0]).__name__
                self.multi_params_dict[len(self.multi_params_dict)] = \
                    {'label': label, 'values': value}
                self.extra_dims.append(len(value))
        return value

    def get_parameters(self, name):
        """ Return the a plugin parameter

        :params str name: parameter name (dictionary key)
        :returns: the associated value in ``self.parameters``
        :rtype: dict value
        """
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

    def _clean_up(self):
        """ Perform necessary plugin clean up after the plugin has completed.
        """
        self.__copy_meta_data()
        self.__clean_up_plugin_data()
        self.__delete_mappings()

    def __delete_mappings(self):
        """ Delete mapping datasets and set mapping flag to False.
        """
        in_datasets = self.get_in_datasets()
        for data in in_datasets:
            if data.mapping:
                del self.exp.index['mapping'][data.get_name()]
                self.mapping = False

    def __copy_meta_data(self):
        """
        Copy all metadata from input datasets to output datasets, except axis
        # data that is no longer valid.
        """
        remove_keys = self.__remove_axis_data()
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

    def __remove_axis_data(self):
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

    def __clean_up_plugin_data(self):
        """ Remove pluginData object encapsulated in a dataset after plugin
        completion.
        """
        in_data, out_data = self.get_datasets()
        data_object_list = in_data + out_data
        for data in data_object_list:
            data._clear_plugin_data()

    def _revert_preview(self, in_data):
        """ Revert dataset back to original shape if previewing was used in a
        plugin to reduce the data shape but the original data shape should be
        used thereafter.
        """
        for data in in_data:
            if data.get_preview().revert_shape:
                data.get_preview()._unset_preview()

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
        """
        Gets the Citation Information for a plugin

        :returns:  A populated savu.data.plugin_info.CitationInfomration

        """
        return None

    def executive_summary(self):
        """
        Provide a summary to the user for the result of the plugin
        e.g.
         - Warning, the sample may have shifted during data collection
         - Filter operated normally
        :returns:  A list of string summaries
        """
        return ["Nothing to Report"]
