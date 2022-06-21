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

import copy
import numpy as np

import savu.plugins.plugin_datasets_notes as notes
from savu.core.utils import docstring_parameter
from savu.data.data_structures.plugin_data import PluginData


class PluginDatasets(object):

    def __init__(self, *args, **kwargs):
        super(PluginDatasets, self).__init__()
        self.exp = None
        self.data_objs = {}
        self.variable_data_flag = False
        self._max_itemsize = 0

    def __get_data_objects(self, dtype):
        """ Get the data objects associated with the plugin from the experiment
        data index.

        :params str dtype: "in_data" or "out_data"
        :returns: A list of data objects with the names given in
            ``self.parameters``
        :rtype: list(Data)
        """
        data_list = self.parameters[dtype + 'sets']
        data_objs = []
        for data in data_list:
            data_obj = self.exp.index[dtype][data]
            data_objs.append(data_obj)
        return data_objs

    def _clone_datasets(self):
        for data_obj in list(self.exp.index['out_data'].values()):
            if data_obj.raw and data_obj.data:
                data_obj.raw.create_next_instance(data_obj)
#                data_obj.clone = True

    def _finalise_datasets(self):
        in_data, out_data = self.get_datasets()
        for data in in_data + out_data:
            data._finalise_patterns()

    def _finalise_plugin_datasets(self):
        if 'dawn_runner' in list(self.exp.meta_data.get_dictionary().keys()):
            return

        in_pData, out_pData = self.get_plugin_datasets()

        params = {}
        for pData in in_pData + out_pData:
            pData._set_meta_data()
            params[pData] = pData._get_plugin_data_size_params()

        max_bytes = 0
        for key, value in params.items():
            if value['transfer_bytes'] > max_bytes:
                max_data = key
                max_bytes = value['transfer_bytes']

        # set mft and mfp for the largest dataset
        max_data.plugin_data_transfer_setup()
        to_set = list(set(params.keys()).difference(set([max_data])))

        for pData in to_set:
            if params[pData]['total_frames'] == params[max_data]['total_frames']:
                pData.plugin_data_transfer_setup(copy=max_data)
            else:
                if pData.max_frames == 'multiple':
                    msg = "If a plugin reduces the number of frames, the " \
                        "number of frames cannot be 'multiple'."
                    raise Exception(msg)
                pData.plugin_data_transfer_setup(calc=max_data)

    def __set_in_datasets(self):
        """ Set the in_data objects.

        :returns: the in_datasets associated with the plugin.
        :rtype: list[Data]
        """
        return self.__get_data_objects('in_data')

    def __set_out_datasets(self):
        """ Set the out_data objects.

        If the out_datasets do not exist inside the experiment then create
        them.

        :returns: the out_datasets associated with the plugin.
        :rtype: list[Data]
        """
        try:
            out_data = self.__get_data_objects('out_data')
        except KeyError:
            out_data = []
            for data in self.parameters['out_datasets']:
                self.exp.create_data_object("out_data", data)
            out_data = self.__get_data_objects('out_data')
        for data in out_data:
            data.extra_dims = self.get_plugin_tools().get_extra_dims()
        return out_data

    def _get_plugin_data(self, data_list):
        """ Encapsulate a PluginData object in each dataset associated with
        the plugin.

        :params list(Data) data_list: A list of Data objects used in a plugin.
        :returns: A list of PluginData objects.
        :rtype: list(PluginData)
        """
        pData_list = []
        ptools = self.get_plugin_tools()
        used = set()
        unique_data_list = \
            [x for x in data_list if x not in used and (used.add(x) or True)]
        for data in unique_data_list:
            pData_list.append(PluginData(data, self))
            pData_list[-1].extra_dims = ptools.get_extra_dims()
            pData_list[-1].multi_params_dict = ptools.get_multi_params_dict()
        return pData_list

    def _set_plugin_dataset_names(self):
        """ Fill in empty in/out_dataset entries with default values.
        """
        params = self.parameters
        orig_in = copy.copy(params['in_datasets'])
        in_names = self._set_in_dataset_names(params)
        # case that an extra in_dataset is added in the plugin
        in_names = orig_in if len(orig_in) and \
            len(in_names) > len(orig_in) else in_names
        self._set_out_dataset_names(params, in_names)
        # update the entry in the process list
        data_dict = {'in_datasets': params['in_datasets'],
                      'out_datasets': params['out_datasets']}
        idx = self.exp.meta_data.get('nPlugin')
        self.exp.meta_data.plugin_list._update_datasets(idx, data_dict)

    def _set_in_dataset_names(self, params):
        dIn = params['in_datasets']
        dIn = dIn if isinstance(dIn, list) else [dIn]
        dIn = self.exp._set_all_datasets('in_data') if len(dIn) ==0 else dIn
        params['in_datasets'] = dIn
        nIn = self.nInput_datasets() # datasets many be added dynamically here
        return self.check_nDatasets(params['in_datasets'], nIn, 'in_data')

    def _set_out_dataset_names(self, params, in_names):
        dOut = params['out_datasets'] if 'out_datasets' in params.keys() else []
        dOut = dOut if isinstance(dOut, list) else [dOut]
        dOut = (copy.copy(in_names) if len(dOut) == 0 else dOut)
        clones = self.nClone_datasets()
        params['out_datasets'] = dOut
        nOut = self.nOutput_datasets()
        names = self.check_nDatasets(params['out_datasets'], nOut,
                                     "out_data", clones=clones)
        if clones:
            dOut.extend(['itr_clone' + str(i) for i in range(clones)])
    
        for i in range(len(names)):
            new = names[i].split('in_datasets')
            if len(new) == 2:
                names[i] = in_names[int(list(new[1])[1])]
        params["out_datasets"] = names
        return names

    def check_nDatasets(self, names, nSets, dtype, clones=0):
        nSets = len(self.parameters[dtype + 'sets']) if nSets=='var' else nSets
        if len(names) is not (nSets - clones):
            if nSets == 0:
                names = []
            else:
                msg = "ERROR: Broken plugin chain. \n Please name the %s %s " \
                "sets associated with the plugin %s in the process file." % \
                (str(nSets), dtype, self.name)
                raise Exception(msg)
        return names

    def _set_plugin_datasets(self):
        """ Populate ``self.parameters`` in/out_datasets and
        plugin_in/out_datasets with the relevant objects (Data or PluginData).
        """
        if not self.exp._get_dataset_names_complete():
            self._set_plugin_dataset_names()
        self.parameters['in_datasets'] = self.__set_in_datasets()
        self.parameters['out_datasets'] = self.__set_out_datasets()
        self.parameters['plugin_in_datasets'] = \
            self._get_plugin_data(self.parameters['in_datasets'])
        self.parameters['plugin_out_datasets'] = \
            self._get_plugin_data(self.parameters['out_datasets'])

    @docstring_parameter('PluginData', 'in')
    @docstring_parameter(notes.datasets_notes.__doc__)
    def get_plugin_in_datasets(self):
        """ {0} """
        return self.parameters['plugin_in_datasets']

    @docstring_parameter('PluginData', 'out')
    @docstring_parameter(notes.datasets_notes.__doc__)
    def get_plugin_out_datasets(self):
        """ {0} """
        return self.parameters['plugin_out_datasets']

    @docstring_parameter("PluginData")
    @docstring_parameter(notes.two_datasets_notes.__doc__)
    def get_plugin_datasets(self):
        """ {0} """
        return self.get_plugin_in_datasets(), self.get_plugin_out_datasets()

    @docstring_parameter("Data", "in")
    @docstring_parameter(notes.datasets_notes.__doc__)
    def get_in_datasets(self):
        """ {0} """
        return self.parameters['in_datasets']

    @docstring_parameter("Data", "out")
    @docstring_parameter(notes.datasets_notes.__doc__)
    def get_out_datasets(self):
        """ {0} """
        return self.parameters['out_datasets']

    @docstring_parameter("PluginData")
    @docstring_parameter(notes.two_datasets_notes.__doc__)
    def get_datasets(self):
        """ {0} """
        return self.get_in_datasets(), self.get_out_datasets()

    @docstring_parameter("in")
    @docstring_parameter(notes.mData_notes.__doc__)
    def get_in_meta_data(self):
        """ {0} """
        return self.__set_meta_data(self.parameters['in_datasets'], 'in_data')

    @docstring_parameter("out")
    @docstring_parameter(notes.mData_notes.__doc__)
    def get_out_meta_data(self):
        """ {0} """
        return self.__set_meta_data(self.parameters['out_datasets'],
                                    'out_data')

    def get(self):
        """ Get a list of meta_data objects associated with the
        in/out_datasets.

        :returns: All MetaData objects associated with out data objects.
        :rtype: list(MetaData(in_datasets)), list(MetaData(out_datasets))
        """
        return self.get_in_meta_data(), self.get_out_meta_data()

    def __set_meta_data(self, data_list, dtype):
        """ Append all MetaData objs associated with specified datasets to a
        list.

        :params list(Data) data_list:
        :returns: All MetaData objects associated with data objects in
            data_list
        :rtype: list(MetaData)
        """
        meta_data = []
        for data in data_list:
            meta_data.append(data.meta_data)
        return meta_data

    def _set_unknown_shape(self, data, key):
        try:
            return (len(data.meta_data.get(key)),)
        except KeyError:
            return (0,)
        
