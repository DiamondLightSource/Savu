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
.. module:: base_transport
   :platform: Unix
   :synopsis: A BaseTransport class which implements functions that control\
   the interaction between the data and plugin layers.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""
import copy
import numpy as np
import savu.core.utils as cu


class BaseTransport(object):
    """
    Implements functions that control the interaction between the data and
    plugin layers.
    """

    def __init__(self):
        self.pDict = None

    def _transport_initialise(self, options):
        """
        Any initial setup required by the transport mechanism on start up.\
        This is called before the experiment is initialised.
        """
        raise NotImplementedError("transport_control_setup needs to be "
                                  "implemented in %s", self.__class__)

    def _transport_update_plugin_list(self):
        """
        This method provides an opportunity to add or remove items from the
        plugin list before plugin list check.
        """
        pass

    def _transport_pre_plugin_list_run(self):
        """
        This method is called after all datasets have been created but BEFORE
        the plugin list is processed.
        """
        pass

    def _transport_pre_plugin(self):
        """
        This method is called directly BEFORE each plugin is executed.
        """
        pass

    def _transport_post_plugin(self):
        """
        This method is called directly AFTER each plugin is executed.
        """
        pass

    def _transport_post_plugin_list_run(self):
        """
        This method is called AFTER the full plugin list has been processed.
        """
        pass

    def _transport_terminate_dataset(self, data):
        """ A dataset that will subequently be removed by the framework.

        :param Data data: A data object to finalise.
        """
        pass

    def process_setup(self, plugin):
        pDict = {}
        pDict['in_data'], pDict['out_data'] = plugin.get_datasets()
        pDict['in_sl'] = self.__get_all_slice_lists(pDict['in_data'], 'in')
        pDict['out_sl'] = self.__get_all_slice_lists(pDict['out_data'], 'out')
        pDict['nIn'] = range(len(pDict['in_data']))
        pDict['nOut'] = range(len(pDict['out_data']))
        pDict['nProc'] = len(pDict['in_sl']['process'])
        pDict['nTrans'] = len(pDict['in_sl']['transfer'][0])
        pDict['squeeze'] = self.__set_functions(pDict['in_data'], 'squeeze')
        pDict['expand'] = self.__set_functions(pDict['out_data'], 'expand')

        frames = [f for f in pDict['in_sl']['frames']]
        self.__set_global_frame_index(plugin, frames, pDict['nProc'])
        self.pDict = pDict

    def _transport_process(self, plugin):
        """ Organise required data and execute the main plugin processing.

        :param plugin plugin: The current plugin instance.
        """
        self.process_setup(plugin)
        pDict = self.pDict
        result = [np.empty(d._get_plugin_data().get_shape_transfer()) for d in
                  pDict['out_data']]

        # loop over the transfer data
        nTrans = pDict['nTrans']
        for count in range(nTrans):
            end = True if count == nTrans-1 else False
            percent_complete = count/(nTrans * 0.01)
            cu.user_message("%s - %3i%% complete" %
                            (plugin.name, percent_complete))
            # get the transfer data
            transfer_data = self.__transfer_all_data(count)

            # loop over the process data
            for i in range(pDict['nProc']):
                data = self._get_input_data(plugin, transfer_data, i)
                res = self._get_output_data(
                        plugin.plugin_process_frames(data), i)
                for j in pDict['nOut']:
                    out_sl = pDict['out_sl']['process'][i][j]
                    result[j][out_sl] = res[j]

            self.__return_all_data(count, result, end)

        cu.user_message("%s - 100%% complete" % (plugin.name))
        plugin._revert_preview(pDict['in_data'])

    def _get_input_data(self, plugin, trans_data, count):
        data = []
        current_sl = []
        for d in self.pDict['nIn']:
            in_sl = self.pDict['in_sl']['process'][count][d]
            data.append(self.pDict['squeeze'][d](trans_data[d][in_sl]))
            current_sl.append(self.pDict['in_sl']['current'][d][count])
        plugin.set_current_slice_list(current_sl)
        return data

    def _get_output_data(self, result, count):
        if result is None:
            return
        unpad_sl = self.pDict['out_sl']['unpad'][count]
        result = result if isinstance(result, list) else [result]
        for j in self.pDict['nOut']:
            result[j] = self.pDict['expand'][j](result[j])[unpad_sl[j]]
        return result

    def __set_global_frame_index(self, plugin, frame_list, nProc):
        """ Convert the transfer global frame index to a process global frame
            index.
        """
        process_frames = []
        for f in frame_list:
            process_frames.append(range(f[0]*nProc, (f[-1]+1)*nProc))
        plugin.set_global_frame_index(process_frames)

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
        pData = data._get_plugin_data()
        max_frames = pData._get_max_frames_process()
        squeeze_dims = pData.get_slice_directions()
        if max_frames > 1 or pData._get_no_squeeze():
            squeeze_dims = squeeze_dims[1:]
        return lambda x: np.squeeze(x, axis=squeeze_dims)

    def __get_all_slice_lists(self, data_list, dtype):
        """ Get all slice lists for the current process.

        :param list(Data) data_list: Datasets
        :returns: A list of dictionaries containing slice lists for each \
            dataset
        :rtype: list(dict)
        """
        sl_dict = {}
        for data in data_list:
            sl = data._get_slice_lists_per_process(dtype)
            for key, value in sl.iteritems():
                if key not in sl_dict:
                    sl_dict[key] = [value]
                else:
                    sl_dict[key].append(value)

        for key in [k for k in ['process', 'unpad'] if k in sl_dict.keys()]:
            nData = range(len(sl_dict[key]))
            rep = range(len(sl_dict[key][0]))
            sl_dict[key] = [[sl_dict[key][i][j] for i in nData] for j in rep]
        return sl_dict

    def __transfer_all_data(self, count):
        """ Get all padded slice lists.

        :param int count: The current frame index.
        :returns: All data for this frame and associated padded slice lists
        :rtype: list(np.ndarray), list(tuple(slice))
        """
        pDict = self.pDict
        data_list = pDict['in_data']
        slice_list = \
            [pDict['in_sl']['transfer'][i][count] for i in pDict['nIn']]
        section = []
        for idx in range(len(data_list)):
            section.append(data_list[idx]._get_padded_data(slice_list[idx]))
        return section

    def __return_all_data(self, count, result, end):
        """ Transfer plugin results for current frame to backing files.

        :param int count: The current frame index.
        :param list(np.ndarray) result: plugin results
        :param bool end: True if this is the last entry in the slice list.
        """
        pDict = self.pDict
        data_list = pDict['out_data']
        slice_list = \
            [pDict['out_sl']['transfer'][i][count] for i in pDict['nOut']]

        result = [result] if type(result) is not list else result
        for idx in range(len(data_list)):
            if end:
                result[idx] = self.__remove_excess_data(
                        data_list[idx], result[idx], slice_list[idx])
            data_list[idx].data[slice_list[idx]] = result[idx]

    def __remove_excess_data(self, data, result, slice_list):
        """ Remove any excess results due to padding for fixed length process \
        frames. """
        sdir = data._get_plugin_data().get_slice_dimension()
        sl = slice_list[sdir]
        shape = result.shape
        if shape[sdir] - (sl.stop - sl.start):
            unpad_sl = [slice(None)]*len(shape)
            unpad_sl[sdir] = slice(0, sl.stop - sl.start)
            result = result[unpad_sl]
        return result
