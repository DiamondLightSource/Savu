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
import sys
import os
import re
import ast
import copy
import h5py
import logging
import inspect
import numpy as np
from collections import OrderedDict

from savu.data.meta_data import MetaData
import savu.plugins.docstring_parser as doc
from savu.plugins.base_tools import BaseTools
from savu.plugins.plugin_datasets import PluginDatasets

class Plugin(PluginDatasets):
    """
    """
    def __init__(self, name='Plugin'):
        super(Plugin, self).__init__()
        self.name = name
        self.parameters = OrderedDict()
        self.chunk = False
        self.docstring_info = {}
        self.slice_list = None
        self.global_index = None
        self.pcount = 0
        self.exp = None
        self.tools_dict = OrderedDict()
        self.p_dict = OrderedDict()
        self.tools = BaseTools()

    def _main_setup(self, exp, params):
        """ Performs all the required plugin setup.

        It sets the experiment, then the parameters and replaces the
        in/out_dataset strings in ``self.parameters`` with the relevant data
        objects. It then creates PluginData objects for each of these datasets.

        :param Experiment exp: The current Experiment object.
        :params dict params: Parameter values.
        """
        self._reset_process_frames_counter()
        self._set_parameters(params)
        self._set_plugin_datasets()
        self.setup()
        self.set_filter_padding(*(self.get_plugin_datasets()))
        self._finalise_datasets()
        self._finalise_plugin_datasets()

    def _reset_process_frames_counter(self):
        self.pcount = 0

    def get_process_frames_counter(self):
        return self.pcount

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

    def load_param_tools(self):
        return self.tools

    def load_doc(self):
        return self.__doc__

    def base_dynamic_data_info(self):
        """ Provides an opportunity to override the number and name of input
        and output datasets before they are created in the base classes. """
        pass

    def dynamic_data_info(self):
        """ Provides an opportunity to override the number and name of input
        and output datasets before they are created. """
        pass

    def set_filter_padding(self, in_data, out_data):
        """
        Should be overridden to define how wide the frame should be for each
        input data set
        """
        return {}

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

        """
        # Test Plugins are: 'RemoveAllRings' 'TomobarRecon' 'Hdf5saver'
        # 'NxtomoLoader' 'DarkFlatFieldCorrection' 'NoProcess' 'Astra' 'Vocentering'

        p_tools = self.load_param_tools()
        all_params = p_tools.plugin_tools.get('param')
        verbose = p_tools.plugin_tools.get('doc').get('verbose')

        self.check_required_keys(all_params)
        # This key check will be moved to another section

        self.set_docstring(verbose)
        self.tools_dict = p_tools.plugin_tools
        self.p_dict = all_params
        self.parameters = OrderedDict([(k, v['default']) for k, v in all_params.items()])


    def _add_item(self, item_list, not_list):
        true_list = [i for i in item_list if i['name'] not in not_list]
        for item in true_list:
            self.parameters[item['name']] = item['default']

    def check_required_keys(self, all_params):
        required_keys = ['dtype', 'description', 'visibility', 'default']
        for p_key, p in all_params.items():
            all_keys = p.keys()
            if p.get('visibility') == 'hidden':
                required_keys = ['default']

            if not all(d in all_keys for d in required_keys):
                print('The missing required keys for ' + str(p_key) + ' are: ')
                print(', '.join(set(required_keys) - set(all_keys)))

    def set_docstring(self, verbose):
        desc = doc.find_args(self)
        self.docstring_info['warn'] = desc['warn']
        self.docstring_info['synopsis'] = desc['synopsis']
        self.docstring_info['info'] = verbose

    def delete_parameter_entry(self, param):
        if param in self.parameters.keys():
            del self.parameters[param]

    def initialise_parameters(self):
        self.parameters = {}
        self._populate_default_parameters()
        self.multi_params_dict = {}
        self.extra_dims = []

    def _set_parameters(self, parameters):
        """
        This method is called after the plugin has been created by the
        pipeline framework.  It replaces ``self.parameters`` default values
        with those given in the input process list.

        :param dict parameters: A dictionary of the parameters for this \
        plugin, or None if no customisation is required.
        """
        self.initialise_parameters()
        for key in parameters.keys():
            if key in self.parameters.keys():
                value = self.__convert_multi_params(parameters[key], key)
                self.parameters[key] = value
            else:
                error = ("Parameter '%s' is not valid for plugin %s. \nTry "
                         "opening and re-saving the process list in the "
                         "configurator to auto remove \nobsolete parameters."
                         % (key, self.name))
                raise ValueError(error)

    def __convert_multi_params(self, value, key):
        """ Set up parameter tuning.

        Convert parameter value to a list if it uses parameter tuning and set
        associated parameters, so the framework knows the new size of the data
        and which plugins to re-run.
        """
        dtype = self.plugin_info[key].get('dtype')

        if isinstance(value, str) and ';' in value:
            value = value.split(';')
            if ":" in value[0]:
                seq = value[0].split(':')
                seq = [eval(s) for s in seq]
                value = list(np.arange(seq[0], seq[1], seq[2]))
                if len(value) == 0:
                    raise RuntimeError(
                        'No values for tuned parameter "{}", '
                        'ensure start:stop:step; values are valid.'.format(key))
            if type(value[0]) != dtype:
                try:
                    value.remove('')
                except:
                    pass
                if isinstance(value[0], str):
                    value = [ast.literal_eval(i) for i in value]
                value = map(dtype, value)
            label = key + '_params.' + type(value[0]).__name__
            self.multi_params_dict[len(self.multi_params_dict)] = \
                {'label': label, 'values': value}
            self.extra_dims.append(len(value))
        return value

    def get_parameters(self, name):
        """ Return a plugin parameter

        :params str name: parameter name (dictionary key)
        :returns: the associated value in ``self.parameters``
        :rtype: dict value
        """
        return self.parameters[name]

    def base_pre_process(self):
        """ This method is called after the plugin has been created by the
        pipeline framework as a pre-processing step.
        """
        pass

    def pre_process(self):
        """ This method is called immediately after base_pre_process(). """
        pass

    def base_process_frames_before(self, data):
        """ This method is called before each call to process frames """
        return data

    def base_process_frames_after(self, data):
        """ This method is called directly after each call to process frames \
        and before returning the data to file."""
        return data

    def plugin_process_frames(self, data):
        frames = self.base_process_frames_after(self.process_frames(
            self.base_process_frames_before(data)))
        self.pcount += 1
        return frames

    def process_frames(self, data):
        """
        This method is called after the plugin has been created by the
        pipeline framework and forms the main processing step

        :param data: A list of numpy arrays for each input dataset.
        :type data: list(np.array)
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

    def base_post_process(self):
        """ This method is called immediately after post_process(). """
        pass

    def set_preview(self, data, params):
        if not params:
            return True
        preview = data.get_preview()
        orig_indices = preview.get_starts_stops_steps()
        nDims = len(orig_indices[0])
        no_preview = [[0] * nDims, data.get_shape(), [1] * nDims, [1] * nDims]

        # Set previewing params if previewing has not already been applied to
        # the dataset.
        if no_preview == orig_indices:
            data.get_preview().revert_shape = data.get_shape()
            data.get_preview().set_preview(params)
            return True
        return False

    def _clean_up(self):
        """ Perform necessary plugin clean up after the plugin has completed.
        """
        self._clone_datasets()
        self.__copy_meta_data()
        self.__set_previous_patterns()
        self.__clean_up_plugin_data()

    def __copy_meta_data(self):
        """
        Copy all metadata from input datasets to output datasets, except axis
        data that is no longer valid.
        """
        remove_keys = self.__remove_axis_data()
        in_meta_data, out_meta_data = self.get()
        copy_dict = {}
        for mData in in_meta_data:
            temp = copy.deepcopy(mData.get_dictionary())
            copy_dict.update(temp)

        for i in range(len(out_meta_data)):
            temp = copy_dict.copy()
            for key in remove_keys[i]:
                if temp.get(key, None) is not None:
                    del temp[key]
            temp.update(out_meta_data[i].get_dictionary())
            out_meta_data[i]._set_dictionary(temp)

    def __set_previous_patterns(self):
        for data in self.get_out_datasets():
            data._set_previous_pattern(
                copy.deepcopy(data._get_plugin_data().get_pattern()))

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
        used thereafter. Remove previewing if it was added in the plugin.
        """
        for data in in_data:
            if data.get_preview().revert_shape:
                data.get_preview()._unset_preview()

    def set_global_frame_index(self, frame_idx):
        self.global_index = frame_idx

    def get_global_frame_index(self):
        """ Get the global frame index. """
        return self.global_index

    def set_current_slice_list(self, sl):
        self.slice_list = sl

    def get_current_slice_list(self):
        """ Get the slice list of the current frame being processed. """
        return self.slice_list

    def get_slice_dir_reps(self, nData):
        """ Return the periodicity of the main slice direction.

        :params int nData: The number of the dataset in the list.
        """
        slice_dir = \
            self.get_plugin_in_datasets()[nData].get_slice_directions()[0]
        sl = [sl[slice_dir] for sl in self.slice_list]
        reps = [i for i in range(len(sl)) if sl[i] == sl[0]]
        return np.diff(reps)[0] if len(reps) > 1 else 1

    def nInput_datasets(self):
        """
        The number of datasets required as input to the plugin

        :returns:  Number of input datasets

        """
        return 1

    def nOutput_datasets(self):
        """
        The number of datasets created by the plugin

        :returns:  Number of output datasets

        """
        return 1

    def nClone_datasets(self):
        """ The number of output datasets that have an clone - i.e. they take\
        it in turns to be used as output in an iterative plugin.
        """
        return 0

    def nFrames(self):
        """ The number of frames to process during each call to process_frames.
        """
        return 'single'

    def final_parameter_updates(self):
        """ An opportunity to update the parameters after they have been set.
        """
        pass

    def get_citation_information(self):
        """
        Gets the Citation Information for a plugin

        :returns:  A populated savu.data.plugin_info.CitationInfomation

        """
        return None

    def executive_summary(self):
        """ Provide a summary to the user for the result of the plugin.

        e.g.
         - Warning, the sample may have shifted during data collection
         - Filter operated normally

        :returns:  A list of string summaries
        """
        return ["Nothing to Report"]
        """
            The base class from which all plugins should inherit.
        :param in_datasets: Create a list of the dataset(s) to \
            process. Default: [].
        :param out_datasets: Create a list of the dataset(s) to \
            create. Default: [].
        """