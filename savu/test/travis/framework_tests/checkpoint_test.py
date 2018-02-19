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
.. module:: checkpoint_tests
   :platform: Unix
   :synopsis: Checking Savu checkpointing works correctly

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import os
import h5py
import tempfile
import unittest
import numpy as np
from shutil import copyfile

from savu.test import test_utils as tu
from savu.core.plugin_runner import PluginRunner
from savu.core.checkpointing import Checkpointing
from savu.data.experiment_collection import Experiment


class CheckpointTest(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        cp = self._get_checkpoint(cfile=False)
        self.cfile = os.path.join(self.tmpdir, cp._filename)

        options = self._get_options()
        exp = self._run_plugin_list(options)

        plist = exp.meta_data.plugin_list.plugin_list
        plist = [p['name'] for p in plist[1:]]
        plist[-1] = 'final_result_tomo'

        # copy original nexus file
        nxs_file = exp.meta_data.get('nxs_filename')
        copy_nxs = ''.join(nxs_file.split('.nxs')[0:-1]) + '_copy.nxs'
        copyfile(nxs_file, copy_nxs)

        # create a checkpoint file with fixed values
        cp = self._get_checkpoint()
        cp._file = self.cfile
        cp._initialise(None)
        self.set_global_parameters(options, plist, nxs_file, copy_nxs, cp)

#    def tearDown(self):
#        self._empty_folder()
#        os.removedirs(self.tmpdir)

    def _empty_folder(self):
        for f in os.listdir(self.tmpdir):
            file_path = os.path.join(self.tmpdir, f)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(e)

    def set_global_parameters(self, options, plist, nxs_file, copy_nxs, cp):
        self.options = options
        self.plist = plist
        self.nxs_file = nxs_file
        self.orig_nxs = copy_nxs
        self.cp = cp

    def _get_options(self, cfile=True):
        options = tu.set_options(tu.get_test_data_path('24737.nxs'))
        options['process_file'] = \
            tu.get_test_process_path('checkpoint_process2.nxs')
        options['out_path'] = self.tmpdir
        options['nxs_filename'] = self.cfile if cfile else None
        options['processes'] = range(1)
        options['mpi'] = False
        return options

    def _get_checkpoint(self, cfile=True):
        exp = Experiment(self._get_options(cfile=cfile))
        checkpoint = Checkpointing(exp)
        return checkpoint

    def _run_plugin_list(self, options):
        plugin_runner = PluginRunner(options)
        exp = plugin_runner._run_plugin_list()
        return exp

    # *************** plugin & subplugin level checkpointing **************
        # Strong kill: options
        # 1: Killed before checkpoint file created
        # 2: Killed before checkpoint file fully populated (initialised)
        # 3: Killed before processing started
        # 4: Killed during processing
            # a) standard
            # b) after a plugin that doesn't populate nxs file, e.g. VoCentering
            # c) re-loading of a different data type, e,g, ImageKey
        # 5: Killed after processing but before data attached to nexus file
        
        # Add something that requires experiment meta data
        # Something that requires a different (non-hdf5) datatype

#    def test_plugin_level_1(self):
#        # 1: Killed before checkpoint file and/or nxs file created
#
#        # No checkpoint file and empty nexus file
#        os.remove(self.cfile)
#        self._refresh_nxs_file(entry=None)
#        self._rerun_from_checkpoint('plugin')
#
#        # No checkpoint file
#        os.remove(self.cfile)
#        self._refresh_nxs_file()
#        self._rerun_from_checkpoint('plugin')
#
#    def test_plugin_level_2(self):
#        # 2: Killed before checkpoint file fully populated (initialised)
#
#        # Remove two datasets from checkpoint file
#        self._amend_checkpoint_file(0, None, None)
#        self._refresh_nxs_file()
#        self._rerun_from_checkpoint('plugin')
#
#        # Remove one dataset from checkpoint file
#        self._amend_checkpoint_file(0, 1, None)
#        self._refresh_nxs_file()
#        self._rerun_from_checkpoint('plugin')
#
#        # Remove all datasets from checkpoint
#        self._amend_checkpoint_file(None, None, None)
#        self._refresh_nxs_file()
#        self._rerun_from_checkpoint('plugin')
#
#    def test_plugin_level_3(self):
#        # 3: Killed before processing started
#
#        self._amend_checkpoint_file(0, 0, 0)
#        self._refresh_nxs_file()
#        self._rerun_from_checkpoint('plugin')
#
#    def test_plugin_level_4a(self):
#        # 4: Killed during processing
#        #    a) standard
#        self._set_checkpoint_parameters(3, 3, 3)
#        # rerun from checkpoint
#        self._rerun_from_checkpoint('plugin')
#
#    def test_plugin_level_4b(self):
#        # 4: Killed during processing
#            # b) after a plugin that doesn't populate nxs file
#        self._set_checkpoint_parameters(5, 3, 3)
#        # rerun from checkpoint
#        self._rerun_from_checkpoint('plugin')

    def test_plugin_level_4c(self):
        # 4: Killed during processing
            # c) re-loading of a different data type, e.g., ImageKey
        self._set_checkpoint_parameters(1, 3, 3)
        # rerun from checkpoint
        self._rerun_from_checkpoint('plugin')

    def _set_checkpoint_parameters(self, p_no, tidx, pidx):
        self._amend_nxs_file(self.orig_nxs, self.nxs_file, self.plist, p_no)
        self._amend_checkpoint_file(p_no, tidx, pidx)
        self._assert_checkpoint_params_equal(p_no, tidx, pidx)

    def _rerun_from_checkpoint(self, level, options=None):
        options = self._get_options() if options is None else options
        options['checkpoint'] = level
        self._run_plugin_list(options)
        self._assert_entries_equal(self.orig_nxs, self.nxs_file)

    def _refresh_nxs_file(self, entry=True):
        with h5py.File(self.nxs_file, 'w') as f:
            if entry:
                f.create_group('entry')

    def _amend_nxs_file(self, copy_file, nxs_file, plist, p_no):
        # update nxs file and checkpoint file
        with h5py.File(copy_file, 'r') as f:
            datasets = self._read_nexus_file(f, [])
            datasets = \
                [d for d in datasets for p in plist[0:p_no] if p in d.name]
            with h5py.File(nxs_file, 'w') as n:
                for d in datasets:
                    group = n.require_group(d.parent.name)
                    f.copy(d, group)

    def _amend_checkpoint_file(self, p_no, pidx, tidx):
        with h5py.File(self.cfile, 'a') as f:
            self._set_nxs_entry(f, 'transfer_idx', tidx)
            self._set_nxs_entry(f, 'process_idx', pidx)
            self._set_nxs_entry(f, 'completed_plugins', p_no)

    def _set_nxs_entry(self, f, dataset, value):
        if value is None and dataset in f:
            f.__delitem__(dataset)
        elif dataset:
            f[dataset][:] = value
        else:
            f[dataset] = value

    def _read_nexus_file(self, nxsfile, datasets):
        # find NXdata
        for key, value in nxsfile.items():
            if self._is_nxdata(value):
                datasets.append(value)
            elif isinstance(value, h5py.Group) and key != 'input_data':
                self._read_nexus_file(value, datasets)
        return datasets

    def _is_nxdata(self, value):
        check = 'NX_class' in value.attrs.keys() and\
            value.attrs['NX_class'] == 'NXdata'
        return check

    def _assert_checkpoint_params_equal(self, p_no, tidx, pidx):
        # find the checkpoint parameters and assert equal
        copy_file = ''.join(self.cfile.split('.h5')[0:-1]) + '_copy.h5'
        copyfile(self.cfile, copy_file)
        cp = self.cp
        cp._exp.checkpoint = cp
        cp._exp.meta_data.set('checkpoint', 'plugin')
        cp._exp.meta_data.set('nxs_filename', self.nxs_file)

        self.assertEqual(cp.get_checkpoint_plugin(), p_no)
        self.assertEqual(cp._trans_idx, tidx)
        self.assertEqual(cp._proc_idx, pidx)
        copyfile(copy_file, self.cfile)
        os.remove(copy_file)

    def _assert_entries_equal(self, f1, f2):
        # get final entries in both files and check that they match
        with h5py.File(f1, 'r') as f1, h5py.File(f2, 'r') as f2:
            d1 = f1['entry/final_result_tomo/data'][:]
            d2 = f2['entry/final_result_tomo/data'][:]
            np.testing.assert_array_almost_equal(d1, d2)


if __name__ == "__main__":
    unittest.main()
