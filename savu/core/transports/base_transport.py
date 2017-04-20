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

    def _transport_process(self, plugin):
        """ Organise required data and execute the main plugin processing.

        :param plugin plugin: The current plugin instance.
        """
        in_data, out_data = plugin.get_datasets()
        sdirs = [d.get_slice_directions()[0] for d in in_data]
        in_sl = self.__get_all_slice_lists(in_data, 'in')
        out_sl = self.__get_all_slice_lists(out_data, 'out')
        nIn = len(in_data)
        nOut = len(out_data)
        nProcs = len(in_sl['process'])
        nTrans = len(in_sl['transfer'][0])

        plugin.set_global_frame_index([f for f in in_sl['frames']])

        squeeze_dict = self.__set_functions(in_data, 'squeeze')
        expand_dict = self.__set_functions(out_data, 'expand')

        result = [np.empty(d._get_plugin_data().get_shape_transfer())
                  for d in out_data]

        # ****** could this be different for different datasets?
        print "\nin process list", in_sl['process']
        print "\nout process list", out_sl['process'], "\n"
        print "IN nProcess", len(in_sl['process'])
        print "IN nTransfer", len(in_sl['transfer'][0])
        print "OUT nProcess", len(out_sl['process'])
        print "OUT nTransfer", len(out_sl['transfer'][0])
        print "nIn", nIn
        print "nOut", nOut

        for d in in_data:
            print "in", d.get_shape()

        for d in out_data:
            print "out", d.get_shape()

        print "\nIN slice list for process"
        for sl in in_sl['process']:
            print sl

        # loop over the transfer data
        for count in range(nTrans):
            end = True if count == nTrans-1 else False
            percent_complete = count/(nTrans * 0.01)
            cu.user_message("%s - %3i%% complete" %
                            (plugin.name, percent_complete))

            in_trans_sl = [in_sl['transfer'][i][count] for i in range(nIn)]
            out_trans_sl = [out_sl['transfer'][i][count] for i in range(nOut)]

            transfer_data, slice_list = \
                self.__transfer_all_data(in_data, in_trans_sl)

            # loop over the process data
            for i in range(nProcs):
                plugin.set_current_slice_list(
                        [in_sl['current'][j][i] for j in range(nIn)])
                process_data = \
                    [squeeze_dict[j](transfer_data[j][in_sl['process'][i][j]])
                     for j in range(nIn)]
                temp = plugin.plugin_process_frames(process_data)
                temp = temp if isinstance(temp, list) else [temp]
                for j in range(len(temp)):
                    result[j][out_sl['process'][i][j]] = \
                          expand_dict[j](temp[j])[out_sl['unpad'][i][j]]

            self.__return_all_data(out_data, out_trans_sl, result, end)

        cu.user_message("%s - 100%% complete" % (plugin.name))
        plugin._revert_preview(in_data)

#    def _transport_process(self, plugin):
#        """ Organise required data and execute the main plugin processing.
#
#        :param plugin plugin: The current plugin instance.
#        """
#        sl_dict = self.__get_slice_lists_info(plugin)
#
#    def __get_slice_lists_info(self, plugin):
#        in_data, out_data = plugin.get_datasets()
#        nIn = len(in_data)
#        nOut = len(out_data)         
#        in_sl = self.__get_all_slice_lists(in_data, 'in')
#        out_sl = self.__get_all_slice_lists(out_data, 'out')
#        nProcessIn = [len(in_sl['process'][:][j]) for j in range(nIn)]
#        nTransferIn = [len(in_sl['transfer'][i][:]) for i in range(nIn)]
#        nProcessOut = [len(out_sl['process'][:][j]) for j in range(nOut)]
#        nTransferOut = [len(out_sl['transfer'][i][:]) for i in range(nOut)]
#        sl_dict = {'len': {'in': {'nproc': nProcessIn, 'ntrans': nTransferIn},
#                    'out': {'nproc': nProcessOut, 'ntrans': nTransferOut}}}
#        return sl_dict    
                        
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
        max_frames = data._get_plugin_data()._get_max_frames_process()
        squeeze_dims = data._get_plugin_data().get_slice_directions()
        if max_frames > 1:
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

    def __transfer_all_data(self, data_list, slice_list):
        """ Get all padded slice lists.

        :param Data data_list: datasets
        :param list(list(slice)) slice_list: slice lists for datasets
        :returns: all data for this frame and associated padded slice lists
        :rtype: list(np.ndarray), list(tuple(slice))
        """
        section = []
        slist = []
        for idx in range(len(data_list)):
            section.append(data_list[idx]._get_padded_data(slice_list[idx]))
            slist.append(slice_list[idx])
        return section, slist

    def __return_all_data(self, data_list, slice_list, result, end):
        """ Transfer plugin results for current frame to backing files.

        :param list(Data) data_list: datasets
        :param list(list(slice)) slice_list: slice lists for datasets
        :param list(np.ndarray) result: plugin results
        :param bool end: True if this is the last entry in the slice list.
        """
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
