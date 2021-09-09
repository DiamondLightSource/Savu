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
.. module:: base_checkpoint_test
   :platform: Unix
   :synopsis: A base class from which checkpoint tests inherit.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import os
import tempfile
import h5py
import unittest
import numpy as np
from shutil import copyfile
import shutil

from savu.core.plugin_runner import PluginRunner
from savu.core.checkpointing import Checkpointing
from savu.core.utils import ensure_string
from savu.data.experiment_collection import Experiment


class BaseCheckpointTest(object):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        cp = self._get_checkpoint(cfile=False)
        folder = os.path.join(self.tmpdir, 'checkpoint')
        fname = 'process0' + cp._filename
        self.cfile = os.path.join(folder, fname)
        options = self.get_options()
        exp = self._run_plugin_list(options)
        plist = self.set_plist(exp)

        # copy original nexus file
        nxs_file = exp.meta_data.get('nxs_filename')
        copy_nxs = ''.join(nxs_file.split('.nxs')[0:-1]) + '_copy.nxs'
        copyfile(nxs_file, copy_nxs)

        # create a checkpoint file with fixed values
        cp = self._get_checkpoint()
        cp._file = self.cfile
        cp._initialise(None)
        self.set_global_parameters(options, plist, nxs_file, copy_nxs, cp)

    def tearDown(self):
        cp_folder = os.path.join(self.tmpdir, 'checkpoint')
        #self._empty_folder(cp_folder)
        #os.removedirs(cp_folder)
        #self._empty_folder(self.tmpdir)
        #os.removedirs(self.tmpdir)
        shutil.rmtree(cp_folder, ignore_errors=True)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _empty_folder(self, folder):
        for f in os.listdir(folder):
            file_path = os.path.join(folder, f)
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

    def get_options(self, cfile=True):
        options = self.set_data_options()
        options['out_path'] = self.tmpdir
        options['nxs_filename'] = self.cfile if cfile else None
        options['processes'] = list(range(1))
        options['process'] = 0
        options['mpi'] = False
        options['inter_path'] = self.tmpdir
        options['command'] = ''
        return options

    def _get_checkpoint(self, cfile=True):
        exp = Experiment(self.get_options(cfile=cfile))
        checkpoint = Checkpointing(exp)
        return checkpoint

    def _run_plugin_list(self, options):
        plugin_runner = PluginRunner(options)
        exp = plugin_runner._run_plugin_list()
        return exp

    def test_checkpoint_1(self):
        # 1: Killed before checkpoint file created

        # No checkpoint file
        os.remove(self.cfile)
        self._refresh_nxs_file()
        vals = (0, 0, 0, 'plugin')
        with self.assertRaises(Exception) as context:
            self._rerun_from_checkpoint(*vals)
        self.assertTrue('No checkpoint file found.', context.exception)

    def test_plugin_level_2(self):
        # 2: Killed before checkpoint file fully populated (initialised)
        # Remove two datasets from checkpoint file
        vals = (0, None, None, 'plugin')
        self._amend_checkpoint_file(0, None, None)
        self._refresh_nxs_file()
        self._rerun_from_checkpoint(*vals)

        # Remove one dataset from checkpoint file
        vals = (0, 1, 0, 'subplugin')
        self._amend_checkpoint_file(0, 1, None)
        self._refresh_nxs_file()
        self._rerun_from_checkpoint(*vals)

        # Remove all datasets from checkpoint
        vals = (0, 0, 0, 'plugin')
        self._amend_checkpoint_file(None, None, None)
        self._refresh_nxs_file()
        self._rerun_from_checkpoint(*vals)

    def test_plugin_level_3(self):
        # 3: Killed before processing started

        vals = (0, 0, 0)
        self._amend_checkpoint_file(*vals)
        self._refresh_nxs_file()
        self._rerun_from_checkpoint(*(vals + ('plugins',)))

    def test_plugin_level_4a(self):
        # 4: Killed during processing
        #    a) standard
        vals = (3, 0, 0, 'plugin')
        self._set_checkpoint_parameters(*vals)
        # rerun from checkpoint
        self._rerun_from_checkpoint(*vals)

        os.remove(self.nxs_file)
        vals = (3, 3, 3, 'subplugin')
        self._set_checkpoint_parameters(*vals)
        # rerun from checkpoint
        self._rerun_from_checkpoint(*vals)

    def test_plugin_level_4b(self):
        # 4: Killed during processing
        #    b) after a plugin that doesn't populate nxs file - (works with full-field processing list)
        vals = (5, 3, 3, 'plugin')
        self._set_checkpoint_parameters(*vals)
        # rerun from checkpoint
        self._rerun_from_checkpoint(*vals)

        os.remove(self.nxs_file)
        vals = (5, 3, 3, 'subplugin')
        self._set_checkpoint_parameters(*vals)
        # rerun from checkpoint
        self._rerun_from_checkpoint(*vals)

    def test_plugin_level_4c(self):
        # 4: Killed during processing
        #    c) re-loading of a different data type, e.g., ImageKey
        vals = (1, 3, 3, 'plugin')
        self._set_checkpoint_parameters(*vals)
        # rerun from checkpoint
        self._rerun_from_checkpoint(*vals)

        os.remove(self.nxs_file)
        vals = (1, 3, 3, 'subplugin')
        self._set_checkpoint_parameters(*vals)
        # rerun from checkpoint
        self._rerun_from_checkpoint(*vals)

    def _set_checkpoint_parameters(self, p_no, tidx, pidx, level):
        self._amend_nxs_file(self.orig_nxs, self.nxs_file, self.plist, p_no)
        self._amend_checkpoint_file(p_no, tidx, pidx)

    def _rerun_from_checkpoint(self, p_no, tidx, pidx, level, options=None):
        options = self.get_options() if options is None else options
        options['checkpoint'] = level
        exp = self._run_plugin_list(options)
        self._assert_checkpoint_params_equal(p_no, tidx, pidx, level, exp)
        self._assert_entries_equal(self.orig_nxs, self.nxs_file)

    def _refresh_nxs_file(self, entry=True):
        with h5py.File(self.nxs_file, 'w') as f:
            if entry:
                f.create_group('entry')

    def _amend_nxs_file(self, copy_file, nxs_file, plist, p_no):
        # update nxs file and checkpoint file
        with h5py.File(copy_file, 'r') as f:
            datasets = self._read_nexus_file(f, [])
            datasets = [d for d in datasets for p in
                        self._flatten(plist[0:p_no], []) if p in d.name]
            with h5py.File(nxs_file, 'w') as n:
                for d in datasets:
                    group = n.require_group(d.parent.name)
                    f.copy(d, group)

    def _flatten(self, alist, flat_list=[]):
        for l in alist:
            if isinstance(l, list):
                self._flatten(l, flat_list=flat_list)
            else:
                flat_list.append(l)
        return flat_list

    def _amend_checkpoint_file(self, p_no, tidx, pidx):
        with h5py.File(self.cfile, 'a') as f:
            self._create_dataset(f, 'transfer_idx', tidx)
            self._create_dataset(f, 'process_idx', pidx)
            self._create_dataset(f, 'completed_plugins', p_no)

    def _create_dataset(self, f, name, data):
        if name in list(f.keys()):
            f.__delitem__(name)
        if data is not None:
            f.create_dataset(name, data=data, dtype=np.int16)

    def _read_nexus_file(self, nxsfile, datasets):
        # find NXdata
        for key, value in list(nxsfile.items()):
            if self._is_nxdata(value):
                datasets.append(value)
            elif isinstance(value, h5py.Group) and key != 'input_data':
                self._read_nexus_file(value, datasets)
        return datasets

    def _is_nxdata(self, value):
        check = 'NX_class' in list(value.attrs.keys()) and ensure_string(value.attrs['NX_class']) == 'NXdata'
        return check

    def _assert_checkpoint_params_equal(self, p_no, tidx, pidx, level, exp):
        # find the checkpoint parameters and assert equal
        cp = exp.checkpoint
        used_p_no, used_tidx, used_pidx = cp.get_start_values()

        if level == 'plugin':
            tidx = 0
            pidx = 0

        self.assertEqual(used_tidx, tidx)
        self.assertEqual(used_pidx, pidx)
        self.assertEqual(used_p_no, p_no)

    def _assert_entries_equal(self, f1, f2):
        # get final entries in both files and check that they match
        with h5py.File(f1, 'r') as f1, h5py.File(f2, 'r') as f2:
            names = [d.name for d in self._read_nexus_file(f1, [])]
            final_res = [n for n in names if 'final_result' in n]
            for res in final_res:
                data = '/'.join((res, 'data'))
                np.testing.assert_array_almost_equal(f1[data][:], f2[data][:])

if __name__ == "__main__":
    unittest.main()
