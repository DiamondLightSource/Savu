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

import os
import time
import copy
import h5py
import math
import logging
import numpy as np

import savu.core.utils as cu
import savu.plugins.utils as pu
from savu.data.data_structures.data_types.base_type import BaseType

NX_CLASS = 'NX_class'


class BaseTransport(object):
    """
    Implements functions that control the interaction between the data and
    plugin layers.
    """

    def __init__(self):
        self.pDict = None
        self.no_processing = False

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

    def _transport_load_plugin(self, exp, plugin_dict):
        """ This method is called before each plugin is loaded """
        return pu.plugin_loader(exp, plugin_dict)

    def _transport_pre_plugin(self):
        """
        This method is called directly BEFORE each plugin is executed, but \
        after the plugin is loaded.
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
        pDict['in_sl'] = self._get_all_slice_lists(pDict['in_data'], 'in')
        pDict['out_sl'] = self._get_all_slice_lists(pDict['out_data'], 'out')
        pDict['nIn'] = list(range(len(pDict['in_data'])))
        pDict['nOut'] = list(range(len(pDict['out_data'])))
        pDict['nProc'] = len(pDict['in_sl']['process'])
        if 'transfer' in list(pDict['in_sl'].keys()):
            pDict['nTrans'] = len(pDict['in_sl']['transfer'][0])
        else:
            pDict['nTrans'] = 1
        pDict['squeeze'] = self._set_functions(pDict['in_data'], 'squeeze')
        pDict['expand'] = self._set_functions(pDict['out_data'], 'expand')

        frames = [f for f in pDict['in_sl']['frames']]
        self._set_global_frame_index(plugin, frames, pDict['nProc'])
        self.pDict = pDict

    def _transport_process(self, plugin):
        """ Organise required data and execute the main plugin processing.

        :param plugin plugin: The current plugin instance.
        """
        logging.info("transport_process initialise")
        pDict, result, nTrans = self._initialise(plugin)
        logging.info("transport_process get_checkpoint_params")
        cp, sProc, sTrans = self.__get_checkpoint_params(plugin)

        prange = list(range(sProc, pDict['nProc']))
        kill = False
        for count in range(sTrans, nTrans):
            end = True if count == nTrans-1 else False
            self._log_completion_status(count, nTrans, plugin.name)

            # get the transfer data
            logging.info("Transferring the data")
            transfer_data = self._transfer_all_data(count)

            if count == nTrans-1 and plugin.fixed_length == False:
                shape = [data.shape for data in transfer_data]
                prange = self.remove_extra_slices(prange, shape)

            # loop over the process data
            logging.info("process frames loop")
            result, kill = self._process_loop(
                    plugin, prange, transfer_data, count, pDict, result, cp)

            logging.info("Returning the data")
            self._return_all_data(count, result, end)

            if kill:
                return 1

        if not kill:
            cu.user_message("%s - 100%% complete" % (plugin.name))

    def remove_extra_slices(self, prange, transfer_shape):
        # loop over datasets:
        for i, data in enumerate(self.pDict['in_data']):
            pData = data._get_plugin_data()
            mft = pData.meta_data.get("max_frames_transfer")
            mfp = pData.meta_data.get("max_frames_process")
            sdirs = data.get_slice_dimensions()
            finish = np.prod([transfer_shape[i][j] for j in sdirs])
            rem, full = math.modf((mft - finish)/mfp)
            full = int(full)

            if rem:
                rem = (mft-finish) - full
                self._update_slice_list("in_sl", i, full, sdirs[0], rem)
                for j, out_data in enumerate(self.pDict['out_data']):
                    out_pData = out_data._get_plugin_data()
                    out_mfp = out_pData.meta_data.get("max_frames_process")
                    out_sdir = data.get_slice_dimensions()[0]
                    out_rem = rem/(mfp/out_mfp)
                    if out_rem%1:
                        raise Exception("'Fixed_length' plugin option is invalid")
                    self._update_slice_list("out_sl", j, full, out_sdir, int(out_rem))

        return list(range(prange[0], prange[-1]+1-full))

    def _update_slice_list(self, key, idx, remove, dim, amount):
        sl = list(self.pDict[key]['process'][idx][-remove])
        s = sl[dim]
        sl[dim] = slice(s.start, s.stop - amount*s.step, s.step)
        self.pDict[key]['process'][idx][-1] = sl        

    def _process_loop(self, plugin, prange, tdata, count, pDict, result, cp):
        kill_signal = False
        for i in prange:
            if cp and cp.is_time_to_checkpoint(self, count, i):
                # kill signal sent so stop the processing
                return result, True
            data = self._get_input_data(plugin, tdata, i, count)
            res = self._get_output_data(
                    plugin.plugin_process_frames(data), i)

            for j in pDict['nOut']:
                if res is not None:
                    out_sl = pDict['out_sl']['process'][i][j]
                    if np.ndim(res) == 2:
                        result[j][out_sl] = res[0][j, ]
                    else:
                        result[j][out_sl] = res[j]
                else:
                    result[j] = None
        return result, kill_signal

    def __get_checkpoint_params(self, plugin):
        cp = self.exp.checkpoint
        if cp:
            cp._initialise(plugin.get_communicator())
            return cp, cp.get_proc_idx(), cp.get_trans_idx()
        return None, 0, 0

    def _initialise(self, plugin):
        self.process_setup(plugin)
        pDict = self.pDict
        result = [np.empty(d._get_plugin_data().get_shape_transfer(),
                           dtype=np.float32) for d in pDict['out_data']]
        # loop over the transfer data
        nTrans = pDict['nTrans']
        self.no_processing = True if not nTrans else False
        return pDict, result, nTrans

    def _log_completion_status(self, count, nTrans, name):
        percent_complete: float = count / (nTrans * 0.01)
        cu.user_message("%s - %3i%% complete" % (name, percent_complete))

    def _transport_checkpoint(self):
        """ The framework has determined it is time to checkpoint.  What
        should the transport mechanism do? Override if appropriate. """
        return False

    def _transport_kill_signal(self):
        """ 
        An opportunity to send a kill signal to the framework.  Return
        True or False. """
        return False

    def _get_all_slice_lists(self, data_list, dtype):
        """ 
        Get all slice lists for the current process.

        :param list(Data) data_list: Datasets
        :returns: A list of dictionaries containing slice lists for each \
            dataset
        :rtype: list(dict)
        """
        sl_dict = {}
        for data in data_list:
            sl = data._get_transport_data().\
                    _get_slice_lists_per_process(dtype)
            for key, value in sl.items():
                if key not in sl_dict:
                    sl_dict[key] = [value]
                else:
                    sl_dict[key].append(value)

        for key in [k for k in ['process', 'unpad'] if k in list(sl_dict.keys())]:
            nData = list(range(len(sl_dict[key])))
            #rep = range(len(sl_dict[key][0]))
            sl_dict[key] = [[sl_dict[key][i][j] for i in nData if j < len(sl_dict[key][i])] for j in range(len(sl_dict[key][0]))]
        return sl_dict

    def _transfer_all_data(self, count):
        """ 
        Transfer data from file and pad if required.

        :param int count: The current frame index.
        :returns: All data for this frame and associated padded slice lists
        :rtype: list(np.ndarray), list(tuple(slice))
        """
        pDict = self.pDict
        data_list = pDict['in_data']

        if 'transfer' in list(pDict['in_sl'].keys()):
            slice_list = \
                [pDict['in_sl']['transfer'][i][count] for i in pDict['nIn']]
        else:
            slice_list = [slice(None)]*len(pDict['nIn'])

        section = []
        for idx in range(len(data_list)):
            section.append(data_list[idx]._get_transport_data().
                           _get_padded_data(slice_list[idx]))
        return section

    def _get_input_data(self, plugin, trans_data, nproc, ntrans):
        data = []
        current_sl = []
        for d in self.pDict['nIn']:
            in_sl = self.pDict['in_sl']['process'][nproc][d]
            data.append(self.pDict['squeeze'][d](trans_data[d][in_sl]))
            entry = ntrans*self.pDict['nProc'] + nproc
            if entry < len(self.pDict['in_sl']['current'][d]):
                current_sl.append(self.pDict['in_sl']['current'][d][entry])
            else:
                current_sl.append(self.pDict['in_sl']['current'][d][-1])
        plugin.set_current_slice_list(current_sl)
        return data

    def _get_output_data(self, result, count):
        if result is None:
            return
        unpad_sl = self.pDict['out_sl']['unpad'][count]
        result = result if isinstance(result, list) else [result]
        for j in self.pDict['nOut']:
            if np.ndim(result) == 2:
                result[0][j, ] = self.pDict['expand'][j](result[0][j, ])[unpad_sl[j]]
            else:
                result[j] = self.pDict['expand'][j](result[j])[unpad_sl[j]]
        return result

    def _return_all_data(self, count, result, end):
        """ 
        Transfer plugin results for current frame to backing files.

        :param int count: The current frame index.
        :param list(np.ndarray) result: plugin results
        :param bool end: True if this is the last entry in the slice list.
        """
        pDict = self.pDict
        data_list = pDict['out_data']

        slice_list = None
        if 'transfer' in list(pDict['out_sl'].keys()):
            slice_list = \
                [pDict['out_sl']['transfer'][i][count] for i in pDict['nOut'] \
                     if len(pDict['out_sl']['transfer'][i]) > count]

        result = [result] if type(result) is not list else result

        for idx in range(len(data_list)):
            if result[idx] is not None:
                if slice_list:
                    temp = self._remove_excess_data(
                            data_list[idx], result[idx], slice_list[idx])
                    data_list[idx].data[slice_list[idx]] = temp
                else:
                    data_list[idx].data = result[idx]

    def _set_global_frame_index(self, plugin, frame_list, nProc):
        """ Convert the transfer global frame index to a process global frame
            index.
        """
        process_frames = []
        for f in frame_list:
            if len(f):
                process_frames.append(list(range(f[0]*nProc, (f[-1]+1)*nProc)))

        process_frames = np.array(process_frames)
        nframes = plugin.get_plugin_in_datasets()[0].get_total_frames()
        process_frames[process_frames >= nframes] = nframes - 1
        frames = process_frames[0] if process_frames.size else process_frames
        plugin.set_global_frame_index(frames)

    def _set_functions(self, data_list, name):
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
        slice_dirs = data.get_slice_dimensions()
        n_core_dirs = len(data.get_core_dimensions())
        new_slice = [slice(None)]*len(data.get_shape())
        possible_slices = [copy.copy(new_slice)]

        pData = data._get_plugin_data()
        if pData._get_rank_inc():
            possible_slices[0] += [0]*pData._get_rank_inc()

        if len(slice_dirs) > 1:
            for sl in slice_dirs[1:]:
                new_slice[sl] = None
        possible_slices.append(copy.copy(new_slice))
        new_slice[slice_dirs[0]] = None
        possible_slices.append(copy.copy(new_slice))
        possible_slices = possible_slices[::-1]
        return lambda x: x[tuple(possible_slices[len(x.shape)-n_core_dirs])]

    def __create_squeeze_function(self, data):
        """ Create a function that removes dimensions of length 1.

        :param Data data: Dataset
        :returns: squeeze function
        :rtype: lambda
        """
        pData = data._get_plugin_data()
        max_frames = pData._get_max_frames_process()

        pad = True if pData.padding and data.get_slice_dimensions()[0] in \
            list(pData.padding._get_padding_directions().keys()) else False

        n_core_dims = len(data.get_core_dimensions())
        squeeze_dims = data.get_slice_dimensions()
        if max_frames > 1 or pData._get_no_squeeze() or pad:
            squeeze_dims = squeeze_dims[1:]
            n_core_dims +=1
        if pData._get_rank_inc():
            sl = [(slice(None))]*n_core_dims + [None]*pData._get_rank_inc()
            return lambda x: np.squeeze(x[tuple(sl)], axis=squeeze_dims)
        return lambda x: np.squeeze(x, axis=squeeze_dims)

    def _remove_excess_data(self, data, result, slice_list):
        """ Remove any excess results due to padding for fixed length process \
        frames. """

        mData = data._get_plugin_data().meta_data.get_dictionary()
        temp = np.where(np.array(mData['size_list']) > 1)[0]
        sdir = mData['sdir'][temp[-1] if temp.size else 0]

        # Not currently working for basic_transport
        if isinstance(slice_list, slice):
            return

        sl = slice_list[sdir]
        shape = result.shape

        if shape[sdir] - (sl.stop - sl.start):
            unpad_sl = [slice(None)]*len(shape)
            unpad_sl[sdir] = slice(0, sl.stop - sl.start)
            result = result[tuple(unpad_sl)]
        return result

    def _setup_h5_files(self):
        out_data_dict = self.exp.index["out_data"]

        current_and_next = False
        if 'current_and_next' in self.exp.meta_data.get_dictionary():
            current_and_next = self.exp.meta_data.get('current_and_next')

        count = 0
        for key in out_data_dict.keys():
            out_data = out_data_dict[key]
            filename = self.exp.meta_data.get(["filename", key])
            out_data.backing_file = self.hdf5._open_backing_h5(filename, 'a')
            c_and_n = 0 if not current_and_next else current_and_next[key]
            out_data.group_name, out_data.group = self.hdf5._create_entries(
                out_data, key, c_and_n)
            count += 1

    def _set_file_details(self, files):
        self.exp.meta_data.set('link_type', files['link_type'])
        self.exp.meta_data.set('link_type', {})
        self.exp.meta_data.set('filename', {})
        self.exp.meta_data.set('group_name', {})
        for key in list(self.exp.index['out_data'].keys()):
            self.exp.meta_data.set(['link_type', key], files['link_type'][key])
            self.exp.meta_data.set(['filename', key], files['filename'][key])
            self.exp.meta_data.set(['group_name', key],
                                   files['group_name'][key])

    def _get_filenames(self, plugin_dict):
        count = self.exp.meta_data.get('nPlugin') + 1
        files = {"filename": {}, "group_name": {}, "link_type": {}}
        for key in list(self.exp.index["out_data"].keys()):
            name = key + '_p' + str(count) + '_' + \
                plugin_dict['id'].split('.')[-1] + '.h5'
            link_type = self._get_link_type(key)
            files['link_type'][key] = link_type
            if link_type == 'final_result':
                out_path = self.exp.meta_data.get('out_path')
            else:
                out_path = self.exp.meta_data.get('inter_path')

            filename = os.path.join(out_path, name)
            group_name = "%i-%s-%s" % (count, plugin_dict['name'], key)
            files["filename"][key] = filename
            files["group_name"][key] = group_name

        return files

    def _get_link_type(self, name):
        idx = self.exp.meta_data.get('nPlugin')
        temp = [e for entry in self.data_flow[idx+1:] for e in entry]
        if name in temp or self.exp.index['out_data'][name].remove:
            return 'intermediate'
        return 'final_result'

    def _populate_nexus_file(self, data):
        filename = self.exp.meta_data.get('nxs_filename')

        with h5py.File(filename, 'a') as nxs_file:
            nxs_entry = nxs_file['entry']
            name = data.data_info.get('name')
            group_name = self.exp.meta_data.get(['group_name', name])
            link_type = self.exp.meta_data.get(['link_type', name])

            if link_type == 'final_result':
                group_name = 'final_result_' + data.get_name()
            else:
                link = nxs_entry.require_group(link_type.encode("ascii"))
                link.attrs[NX_CLASS] = 'NXcollection'
                nxs_entry = link

            # delete the group if it already exists
            if group_name in nxs_entry:
                del nxs_entry[group_name]

            plugin_entry = nxs_entry.require_group(group_name)
            plugin_entry.attrs[NX_CLASS] = 'NXdata'
            self._output_metadata(data, plugin_entry, name)

    def _output_metadata(self, data, entry, name, dump=False):
        self.__output_data_type(entry, data, name)
        mDict = data.meta_data.get_dictionary()
        self._output_metadata_dict(entry.require_group('meta_data'), mDict)

        if not dump:
            self.__output_axis_labels(data, entry)
            self.__output_data_patterns(data, entry)
            if self.exp.meta_data.get('link_type')[name] == 'input_data':
                # output the filename
                entry['file_path'] = \
                    os.path.abspath(self.exp.meta_data.get('data_file'))

    def __output_data_type(self, entry, data, name):
        data = data.data if 'data' in list(data.__dict__.keys()) else data
        if isinstance(data, h5py.Dataset):
            return

        entry = entry.require_group('data_type')
        entry.attrs[NX_CLASS] = 'NXcollection'

        ltype = self.exp.meta_data.get('link_type')
        if name in list(ltype.keys()) and ltype[name] == 'input_data':
            self.__output_data(entry, data.__class__.__name__, 'cls')
            return

        args, kwargs, cls, extras = data._get_parameters(data.get_clone_args())

        for key, value in kwargs.items():
            gp = entry.require_group('kwargs')
            if isinstance(value, BaseType):
                self.__output_data_type(gp.require_group(key), value, key)
            else:
                self.__output_data(gp, value, key)

        for key, value in extras.items():
            gp = entry.require_group('extras')
            if isinstance(value, BaseType):
                self.__output_data_type(gp.require_group(key), value, key)
            else:
                self.__output_data(gp, value, key)

        for i in range(len(args)):
            gp = entry.require_group('args')
            self.__output_data(gp, args[i], ''.join(['args', str(i)]))

        self.__output_data(entry, cls, 'cls')

        if 'data' in list(data.__dict__.keys()) and not \
                isinstance(data.data, h5py.Dataset):
            gp = entry.require_group('data')
            self.__output_data_type(gp, data.data, 'data')

    def __output_data(self, entry, data, name):
        if isinstance(data, dict):
            entry = entry.require_group(name)
            entry.attrs[NX_CLASS] = 'NXcollection'
            for key, value in data.items():
                self.__output_data(entry, value, key)
        else:
            try:
                self.__create_dataset(entry, name, data)
            except Exception:
                try:
                    import json
                    data = np.array([json.dumps(data).encode("ascii")])
                    self.__create_dataset(entry, name, data)
                except Exception:
                    try:
                        data = cu._savu_encoder(data)
                        self.__create_dataset(entry, name, data)
                    except:
                        raise Exception('Unable to output %s to file.' % name)

    def __create_dataset(self, entry, name, data):
        if name not in list(entry.keys()):
            entry.create_dataset(name, data=data)
        else:
            entry[name][...] = data

    def __output_axis_labels(self, data, entry):
        axis_labels = data.data_info.get("axis_labels")
        ddict = data.meta_data.get_dictionary()

        axes = []
        count = 0
        for labels in axis_labels:
            name = list(labels.keys())[0]
            axes.append(name)
            entry.attrs[name + '_indices'] = count

            mData = ddict[name] if name in list(ddict.keys()) \
                else np.arange(data.get_shape()[count])
            if isinstance(mData, list):
                mData = np.array(mData)

            if 'U' in str(mData.dtype):
                mData = mData.astype(np.string_)

            axis_entry = entry.require_dataset(name, mData.shape, mData.dtype)
            axis_entry[...] = mData[...]
            axis_entry.attrs['units'] = list(labels.values())[0]
            count += 1
        entry.attrs['axes'] = axes

    def __output_data_patterns(self, data, entry):
        data_patterns = data.data_info.get("data_patterns")
        entry = entry.require_group('patterns')
        entry.attrs[NX_CLASS] = 'NXcollection'
        for pattern in data_patterns:
            nx_data = entry.require_group(pattern)
            nx_data.attrs[NX_CLASS] = 'NXparameters'
            values = data_patterns[pattern]
            self.__output_data(nx_data, values['core_dims'], 'core_dims')
            self.__output_data(nx_data, values['slice_dims'], 'slice_dims')

    def _output_metadata_dict(self, entry, mData):
        entry.attrs[NX_CLASS] = 'NXcollection'
        for key, value in mData.items():
            nx_data = entry.require_group(key)
            if isinstance(value, dict):
                self._output_metadata_dict(nx_data, value)
            else:
                nx_data.attrs[NX_CLASS] = 'NXdata'
                self.__output_data(nx_data, value, key)
