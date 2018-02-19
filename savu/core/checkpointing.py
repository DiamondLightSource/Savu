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
import logging
import numpy as np

import savu.plugins.utils as pu
from savu.plugins.savers.utils.hdf5_utils import Hdf5Utils


class Checkpointing(object):
    """ Plugin list runner, which passes control to the transport layer.
    """

    def __init__(self, exp, name='Checkpointing'):
        self._exp = exp
        self._h5 = Hdf5Utils(self._exp)
        self._filename = 'checkpoint.h5'
        self._file = None
        self._completed_plugins = None
        self._level = None
        self._proc_idx = None
        self._trans_idx = None
        self._comm = None

    def _initialise(self, comm):
        """ Create a new checkpoint file """
        self._comm = comm
        n_procs = len(self._exp.meta_data.get('processes'))
        with self._h5._open_backing_h5(self._file, 'a', comm=comm) as f:
            if not f.keys():
                f.create_dataset('transfer_idx', (n_procs,), dtype=np.int16)
                f.create_dataset('process_idx', (n_procs,), dtype=np.int8)
                f.create_dataset('completed_plugins', (1,), dtype=np.int8)
                f['completed_plugins'][:] = 0
            else:
                f['transfer_idx'][:] = np.zeros(n_procs)
                f['process_idx'][:] = np.zeros(n_procs)
        self._exp._barrier(communicator=comm)

    def __set_checkpoint_info(self):
        mData = self._exp.meta_data.get
        self._file = os.path.join(mData('out_path'), self._filename)
        self._completed_plugins = 0

    def _set_checkpoint_info_from_file(self, level):
        self._level = level
        self._file = os.path.join(os.path.dirname(
                self._exp.meta_data.get('nxs_filename')), self._filename)
        if not os.path.exists(self._file):
            msg = 'No checkpoint file found: Starting from the beginning.'
            logging.debug(msg)
            return self.__set_checkpoint_info()

        with self._h5._open_backing_h5(self._file, 'r') as f:
            self._completed_plugins = \
                f['completed_plugins'][:][0] if 'completed_plugins' in f else 0
            self._proc_idx = f['process_idx'][:] if 'process_idx' in f else 0
            self._trans_idx = \
                f['transfer_idx'][:] if 'transfer_idx' in f else 0
        os.remove(self._file)
        self.__load_data()
        self._exp._barrier()

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
        self._write_plugin_checkpoint()

    def get_checkpoint_plugin(self):
        checkpoint_flag = self._exp.meta_data.get('checkpoint')
        self.__set_checkpoint_info() if not checkpoint_flag else \
            self._set_checkpoint_info_from_file(checkpoint_flag)
        return self._completed_plugins

    def set_checkpoint(self, ti, pi):
        # replace this with real checkpointing flag
        path = self._exp.meta_data.get('out_path')
        killsignal = os.path.join(path, 'killsignal')
        kill = True if os.path.exists(killsignal) else False
        # if kill signal sent
        if kill:
            self._exp.meta_data.set('killsignal', True)
            self.__write_subplugin_checkpoint(ti, pi)
            # jump to the end of the plugin run!
        return kill

    def _get_checkpoint_params(self):
        return self._level, self._completed_plugins

    def __write_subplugin_checkpoint(self, ti, pi):
        process = self._exp.meta_data.get('process')
        with self._h5._open_backing_h5(self._file, 'a', comm=self._comm) as f:
            f['transfer_idx'][process] = ti
            f['process_idx'][process] = pi

    def _write_plugin_checkpoint(self):
        with self._h5._open_backing_h5(self._file, 'a', comm=self._comm) as f:
            if self._exp.meta_data.get('process') == 0:
                f['completed_plugins'][:] = self._completed_plugins
