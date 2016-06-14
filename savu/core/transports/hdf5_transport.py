# Copyright 2015 Diamond Light Source Ltd.
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
.. module:: hdf5_transport
   :platform: Unix
   :synopsis: Transport specific plugin list runner, passes the data to and \
       from the plugin.

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""

import copy
import numpy as np

from savu.core.transport_control import TransportControl
from savu.core.transport_setup import MPI_setup
import savu.plugins.utils as pu
import savu.core.utils as cu


class Hdf5Transport(TransportControl):

    def _transport_control_setup(self, options):
        MPI_setup(options)

    def _transport_pre_process(self, in_data_list, out_data_list, plugin_inst):
        """ Run the plugin list inside the transport layer.
        """
        exp = self.exp
        plugin_obj = exp.meta_data.plugin_list
        n_loaders = plugin_obj._get_n_loaders()
        plugin_list = exp.meta_data.plugin_list.plugin_list
        saver_plugin = pu.plugin_loader(exp, plugin_list[-1])

        for i in range(n_loaders):
            pu.plugin_loader(exp, plugin_list[i])

        for i in range(len(plugin_inst)):
            exp.index['in_data'] = in_data_list[i]
            exp.index['out_data'] = out_data_list[i]
            saver_plugin.setup()

#    def _transport_run_plugin_list(self):
#        """ Run the plugin list inside the transport layer.
#        """
#        exp = self.exp
#
#        plugin_obj = exp.meta_data.plugin_list
#        n_loaders = plugin_obj._get_n_loaders()
#        plugin_list = exp.meta_data.plugin_list.plugin_list
#
#        for i in range(n_loaders):
#            pu.plugin_loader(exp, plugin_list[i])
#
#        start = n_loaders
#        stop = 0
#        n_plugins = len(plugin_list) - 1  # minus 1 for saver
#
#        while n_plugins != stop:
#            start_in_data = copy.deepcopy(self.exp.index['in_data'])
#            in_data = exp.index["in_data"][exp.index["in_data"].keys()[0]]
#
#            out_data_objs, stop = in_data._load_data(start)
#            exp._clear_data_objects()
#
#            self.exp.index['in_data'] = copy.deepcopy(start_in_data)
#            self.__real_plugin_run(plugin_list, out_data_objs, start, stop)
#            start = stop
#
#        for key in exp.index["in_data"].keys():
#            exp.index["in_data"][key]._close_file()
#
#        return



    def _process(self, plugin):
        """ Organise required data and execute the main plugin processing.

        :param plugin plugin: The current plugin instance.
        """
        self.process_checks()
        in_data, out_data = plugin.get_datasets()

        expInfo = plugin.exp.meta_data
        in_slice_list = self.__get_all_slice_lists(in_data, expInfo)
        out_slice_list = self.__get_all_slice_lists(out_data, expInfo)

        squeeze_dict = self.__set_functions(in_data, 'squeeze')
        expand_dict = self.__set_functions(out_data, 'expand')

        number_of_slices_to_process = len(in_slice_list[0])
        for count in range(number_of_slices_to_process):
            percent_complete = count/(number_of_slices_to_process * 0.01)
            cu.user_message("%s - %3i%% complete" %
                            (plugin.name, percent_complete))

            section, slice_list = \
                self.__get_all_padded_data(in_data, in_slice_list, count,
                                           squeeze_dict)
            result = plugin.process_frames(section, slice_list)
            self.__set_out_data(out_data, out_slice_list, result, count,
                                expand_dict)

        cu.user_message("%s - 100%% complete" % (plugin.name))
        plugin._revert_preview(in_data)

    def process_checks(self):
        pass
        # if plugin inherits from base_recon and the data inherits from tomoraw
        # then throw an exception
#        if isinstance(in_data, TomoRaw):
#            raise Exception("The input data to a reconstruction plugin cannot
#            be Raw data. Have you performed a timeseries_field_correction?")
# call a new process called process_check?

    def __set_functions(self, data_list, name):
        """ Create a dictionary of functions to remove (squeeze) or re-add
        (expand) dimensions, of length 1, from each dataset in a list.

        :param list(Data) data_list: Datasets
        :param str name: 'squeeze' or 'expand'
        :returns: A dictionary of lambda functions
        :rtype: dict
        """
        str_name = 'self.' + name + '_output'
        function = {'expand': self.__create_expand_function,
                    'squeeze': self.__create_squeeze_function}
        ddict = {}
        for i in range(len(data_list)):
            ddict[i] = {i: str_name + str(i)}
            ddict[i] = function[name](data_list[i])
        return ddict

    def __create_expand_function(self, data):
        """ Create a function that re-adds missing dimensions of length 1.

        :param Data data: Dataset
        :returns: expansion function
        :rtype: lambda
        """
        slice_dirs = data._get_plugin_data().get_slice_directions()
        n_core_dirs = len(data._get_plugin_data().get_core_directions())
        new_slice = [slice(None)]*len(data.get_shape())
        possible_slices = [copy.copy(new_slice)]

        if len(slice_dirs) > 1:
            for sl in slice_dirs[1:]:
                new_slice[sl] = None
        possible_slices.append(copy.copy(new_slice))
        new_slice[slice_dirs[0]] = None
        possible_slices.append(copy.copy(new_slice))
        possible_slices = possible_slices[::-1]
        return lambda x: x[possible_slices[len(x.shape)-n_core_dirs]]

    def __create_squeeze_function(self, data):
        """ Create a function that removes dimensions of length 1.

        :param Data data: Dataset
        :returns: squeeze function
        :rtype: lambda
        """
        max_frames = data._get_plugin_data()._get_frame_chunk()
        squeeze_dims = data._get_plugin_data().get_slice_directions()
        if max_frames > 1:
            squeeze_dims = squeeze_dims[1:]
        return lambda x: np.squeeze(x, axis=squeeze_dims)

    def __get_all_slice_lists(self, data_list, expInfo):
        """ Get all slice lists for the current process.

        :param list(Data) data_list: Datasets
        :param: meta_data expInfo: The experiment metadata.
        :returns: slice lists.
        :rtype: list(tuple(slice))
        """
        slice_list = []
        for data in data_list:
            slice_list.append(data._get_slice_list_per_process(expInfo))
        return slice_list

    def __get_all_padded_data(self, data_list, slice_list, count,
                              squeeze_dict):
        """ Get all padded slice lists.

        :param Data data_list: datasets
        :param list(list(slice)) slice_list: slice lists for datasets
        :param int count: frame number.
        :param dict squeeze_dict: squeeze functions for datasets
        :returns: all data for this frame and associated padded slice lists
        :rtype: list(np.ndarray), list(tuple(slice))
        """
        section = []
        slist = []
        for idx in range(len(data_list)):
            section.append(squeeze_dict[idx](
                data_list[idx]._get_padded_slice_data(slice_list[idx][count])))
            slist.append(slice_list[idx][count])
        return section, slist

    def __set_out_data(self, data_list, slice_list, result, count,
                       expand_dict):
        """ Transfer plugin results for current frame to backing files.

        :param list(Data) data_list: datasets
        :param list(list(slice)) slice_list: slice lists for datasets
        :param list(np.ndarray) result: plugin results
        :param int count: frame number
        :param dict expand_dict: expand functions for datasets
        """
        result = [result] if type(result) is not list else result
        for idx in range(len(data_list)):
            data_list[idx].data[slice_list[idx][count]] = \
                data_list[idx]._get_unpadded_slice_data(
                    slice_list[idx][count], expand_dict[idx](result[idx]))

#    def _transfer_to_meta_data(self, return_dict):
#        """
#        """
#        remove_data_sets = []
#        for data_key in return_dict.keys():
#            for name in return_dict[data_key].keys():
#                convert_data = return_dict[data_key][name]
#                remove_data_sets.append(convert_data.name)
#                data_key.meta_data.set(name, convert_data.data[...])
#        return remove_data_sets
