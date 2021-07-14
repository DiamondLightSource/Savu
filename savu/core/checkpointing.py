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
.. module:: checkpointing
   :platform: Unix
   :synopsis: A class to organise Savu checkpointing.
.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>
"""

import os
import time
import copy
import logging
import numpy as np
from mpi4py import MPI
from shutil import copyfile

import savu.plugins.utils as pu
from savu.data.meta_data import MetaData
from savu.plugins.savers.utils.hdf5_utils import Hdf5Utils


class Checkpointing(object):
    """ Contains all checkpointing associated methods.
    """

    def __init__(self, exp, name='Checkpointing'):
        self._exp = exp
        self._h5 = Hdf5Utils(self._exp)
        self._filename = '_checkpoint.h5'
        self._file = None
        self._start_values = (0, 0, 0)
        self._completed_plugins = 0
        self._level = None
        self._proc_idx = 0
        self._trans_idx = 0
        self._comm = None
        self._timer = None
        self._set_timer()
        self.meta_data = MetaData()

    def _initialise(self, comm):
        """ Create a new checkpoint file """
        with self._h5._open_backing_h5(self._file, 'a', mpi=False) as f:
            self._create_dataset(f, 'transfer_idx', 0)
            self._create_dataset(f, 'process_idx', 0)
            self._create_dataset(
                    f, 'completed_plugins', self._completed_plugins)
        msg = "%s initialise." % self.__class__.__name__
        self._exp._barrier(communicator=comm, msg=msg)

    def _create_dataset(self, f, name, val):
        if name in list(f.keys()):
            f[name][...] = val
        else:
            f.create_dataset(name, data=val, dtype=np.int16)

    def __set_checkpoint_info(self):
        mData = self._exp.meta_data.get
        proc = 'process%d' % mData('process')
        self._folder = os.path.join(mData('out_path'), 'checkpoint')
        self._file = os.path.join(self._folder, proc + self._filename)

        if self._exp.meta_data.get('process') == 0:
            if not os.path.exists(self._folder):
                os.makedirs(os.path.join(self._folder))
        self._exp._barrier(msg='Creating checkpoint folder.')

    def _set_checkpoint_info_from_file(self, level):
        self._level = level
        self.__set_checkpoint_info()
        self.__does_file_exist(self._file, level)

        with self._h5._open_backing_h5(self._file, 'r', mpi=False) as f:
            self._completed_plugins = \
                f['completed_plugins'][...] if 'completed_plugins' in f else 0
            self._proc_idx = f['process_idx'][...] if 'process_idx' in f and \
                level == 'subplugin' else 0
            self._trans_idx = f['transfer_idx'][...] if 'transfer_idx' in f \
                and level == 'subplugin' else 0
            # for testing
            self.__set_start_values(
                    self._completed_plugins, self._trans_idx, self._proc_idx)
            self.__set_dataset_metadata(f, 'in_data')
            self.__set_dataset_metadata(f, 'out_data')

        self.__load_data()
        msg = "%s _set_checkpoint_info_from_file" % self.__class__.__name__
        self._exp._barrier(msg=msg)

    def __does_file_exist(self, thefile, level):
        if not os.path.exists(thefile):
            if level == 'plugin':
                proc0 = os.path.join(self._folder, 'process0' + self._filename)
                self.__does_file_exist(proc0, None)
                copyfile(proc0, self._file)
                return
            raise Exception("No checkpoint file found.")

    def __set_dataset_metadata(self, f, dtype):
        self.meta_data.set(dtype, {})
        if dtype not in list(f.keys()):
            return
        entry = f[dtype]
        for name, gp in entry.items():
            data_entry = gp.require_group('meta_data')
            for key, value in data_entry.items():
                self.meta_data.set([dtype, name, key], value[key][...])

    def _get_dataset_metadata(self, dtype, name):
        return self._data_meta_data(dtype)

    def set_completed_plugins(self, n):
        self._completed_plugins = n

    def __load_data(self):
        self._exp.meta_data.set('checkpoint_loader', True)
        temp = self._exp.meta_data.get('data_file')
        nxsfile = self._exp.meta_data.get('nxs_filename')
        self._exp.meta_data.set('data_file', nxsfile)
        pid = 'savu.plugins.loaders.savu_nexus_loader'
        pu.plugin_loader(self._exp, {'id': pid, 'data': {}})
        self._exp.meta_data.delete('checkpoint_loader')
        self._exp.meta_data.set('data_file', temp)

    def output_plugin_checkpoint(self):
        self._completed_plugins += 1
        self.__write_plugin_checkpoint()
        self._reset_indices()

    def get_checkpoint_plugin(self):
        checkpoint_flag = self._exp.meta_data.get('checkpoint')
        if not checkpoint_flag:
            self.__set_checkpoint_info()
            self._initialise(MPI.COMM_WORLD)
        else:
            self._set_checkpoint_info_from_file(checkpoint_flag)
        return self._completed_plugins

    def is_time_to_checkpoint(self, transport, ti, pi):
        interval = self._exp.meta_data.get(
                ['system_params', 'checkpoint_interval'])
        end = time.time()
        if (end - self._get_timer()) > interval:
            self.__write_subplugin_checkpoint(ti, pi)
            self._set_timer()
            transport._transport_checkpoint()
            return transport._transport_kill_signal()
        return False

    def _get_checkpoint_params(self):
        return self._level, self._completed_plugins

    def __write_subplugin_checkpoint(self, ti, pi):
        with self._h5._open_backing_h5(self._file, 'a', mpi=False) as f:
            f['transfer_idx'][...] = ti
            f['process_idx'][...] = pi

    def __write_plugin_checkpoint(self):
        with self._h5._open_backing_h5(self._file, 'a', mpi=False) as f:
            f['completed_plugins'][...] = self._completed_plugins
            f['transfer_idx'][...] = 0
            f['process_idx'][...] = 0

    def _reset_indices(self):
        self._trans_idx = 0
        self._proc_idx = 0

    def get_trans_idx(self):
        return self._trans_idx

    def get_proc_idx(self):
        return self._proc_idx

    def get_level(self):
        return self._level

    def _set_timer(self):
        self._timer = time.time()

    def _get_timer(self):
        return self._timer

    def __set_start_values(self, v1, v2, v3):
        self._start_values = (copy.copy(v1), copy.copy(v2), copy.copy(v3))

    def get_start_values(self):
        return self._start_values
