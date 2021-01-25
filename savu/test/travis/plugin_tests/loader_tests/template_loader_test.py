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
.. module:: template_loader
   :platform: Unix
   :synopsis: testing the template_loader plugin
.. moduleauthor:: Aaron Parsons <scientificsoftware@diamond.ac.uk>

"""
import unittest
import tempfile
import shutil
import os
import numpy as np
import h5py as h5
import tifffile

from scripts.config_generator.content import Content
from collections import OrderedDict
from savu.test import test_utils as tu
from savu.plugins.loaders.utils import yaml_utils as yu
from savu.test.travis.framework_tests.plugin_runner_test import \
    run_protected_plugin_runner
import scripts.config_generator.config_utils as utils


class TemplateLoaderTest(unittest.TestCase):

    def test_1D_data(self):
        A = 11

        X = 10
        Y = 13

        expected_output_shape = (A, X, Y)
        expected_top_corners = np.arange(A, dtype=np.float32)

        self.create_N_tiffs(A, frame_size=(X, Y))
        # create a data file with the axis information
        self.data_file['entry/A'] = np.arange(A)
        self.data_file.close()

        # edit and save the yaml
        self.yaml['xrd']['data']['shape'] = '$(len(A_vals),)'
        self.yaml['xrd']['params'].update({'idx_A': 0,
                                           'idx_detx': 1,
                                           'idx_dety': 2,
                                           'A_vals': "$dfile['entry/A'][()]",
                                           'dims': "$range(0, 3)"})

        # add some axis labels
        self.yaml['xrd']['axis_labels'] = {0: {'dim': '$idx_A', 'name': 'A', 'value': '$A_vals', 'units': 'pixels'},
                                           1: self.detX_axis_label,
                                           2: self.detY_axis_label}

        self.save_yaml_and_change_process_list()
        run_protected_plugin_runner(tu.set_options(self.data_file_path,
                                                   process_file=self.process_list_path,
                                                   out_path=self.test_folder))

        # now check the result

        result = h5.File(os.path.join(self.test_folder, 'test_processed.nxs'), 'r')['entry/final_result_xrd/data']
        np.testing.assert_array_equal(result.shape, expected_output_shape,
                                      err_msg='The output shape is not as expected.')
        result_corners = result[..., -1, -1]
        np.testing.assert_equal(result_corners.dtype, expected_top_corners.dtype,
                                err_msg='The array does not output the correct type.')
        np.testing.assert_array_equal(result_corners, expected_top_corners,
                                      err_msg="The output values are not as expected")

    def test_again(self):
        A = 11

        X = 10
        Y = 13

        expected_output_shape = (A, X, Y)
        expected_top_corners = np.arange(A, dtype=np.float32)

        self.create_N_tiffs(A, frame_size=(X, Y))
        # create a data file with the axis information
        self.data_file['entry/A'] = np.arange(A)
        self.data_file.close()

        # edit and save the yaml
        self.yaml['xrd']['data']['shape'] = '$(len(A_vals),)'
        self.yaml['xrd']['params'].update({'idx_A': 0,
                                           'idx_detx': 1,
                                           'idx_dety': 2,
                                           'A_vals': "$dfile['entry/A'][()]",
                                           'dims': "$range(0, 3)"})

        # add some axis labels
        self.yaml['xrd']['axis_labels'] = {0: {'dim': '$idx_A', 'name': 'A', 'value': '$A_vals', 'units': 'pixels'},
                                           1: self.detX_axis_label,
                                           2: self.detY_axis_label}

        self.save_yaml_and_change_process_list()
        run_protected_plugin_runner(tu.set_options(self.data_file_path,
                                                   process_file=self.process_list_path,
                                                   out_path=self.test_folder))

        # now check the result

        result = h5.File(os.path.join(self.test_folder, 'test_processed.nxs'), 'r')['entry/final_result_xrd/data']
        np.testing.assert_array_equal(result.shape, expected_output_shape,
                                      err_msg='The output shape is not as expected.')
        result_corners = result[..., -1, -1]
        np.testing.assert_equal(result_corners.dtype, expected_top_corners.dtype,
                                err_msg='The array does not output the correct type.')
        np.testing.assert_array_equal(result_corners, expected_top_corners,
                                      err_msg="The output values are not as expected")

    def test_2D_data(self):
        A = 3
        B = 4

        X = 10
        Y = 13

        expected_output_shape = (A, B, X, Y)
        expected_top_corners = np.arange(A*B, dtype=np.float32).reshape((A, B))

        self.create_N_tiffs(A*B, frame_size=(X, Y))
        # create a data file with the axis information
        self.data_file['entry/A'] = np.arange(A)
        self.data_file['entry/B'] = np.arange(B)
        self.data_file.close()

        # edit and save the yaml
        self.yaml['xrd']['data']['shape'] = '$(len(A_vals), len(B_vals))'
        self.yaml['xrd']['params'].update({'idx_A': 0,
                                           'idx_B': 1,
                                           'idx_detx': 2,
                                           'idx_dety': 3,
                                           'A_vals': "$dfile['entry/A'][()]",
                                           'B_vals': "$dfile['entry/B'][()]",
                                           'dims': "$range(0, 4)"})

        self.yaml['xrd']['axis_labels'] = {0: {'dim': '$idx_A', 'name': 'A', 'value': '$A_vals', 'units': 'pixels'},
                                           1: {'dim': '$idx_B', 'name': 'B', 'value': '$B_vals', 'units': 'pixels'},
                                           2: self.detX_axis_label,
                                           3: self.detY_axis_label}

        self.save_yaml_and_change_process_list()

        run_protected_plugin_runner(tu.set_options(self.data_file_path,
                                                   process_file=self.process_list_path,
                                                   out_path=self.test_folder))

        result = h5.File(os.path.join(self.test_folder, 'test_processed.nxs'), 'r')['entry/final_result_xrd/data']
        np.testing.assert_array_equal(result.shape, expected_output_shape,
                                      err_msg='The output shape is not as expected.')
        result_corners = result[..., -1, -1]
        np.testing.assert_equal(result_corners.dtype, expected_top_corners.dtype,
                                err_msg='The array does not output the correct type.')
        np.testing.assert_array_equal(result_corners, expected_top_corners,
                                      err_msg="The output values are not as expected")

    def test_3D_data(self):
        A = 3
        B = 4
        C = 5

        X = 10
        Y = 13
        expected_output_shape = (A, B, C, X, Y)
        expected_top_corners = np.arange(A*B*C, dtype=np.float32).reshape((A, B, C))

        self.create_N_tiffs(A*B*C, frame_size=(X, Y))
        # create a data file with the axis information
        self.data_file['entry/A'] = np.arange(A)
        self.data_file['entry/B'] = np.arange(B)
        self.data_file['entry/C'] = np.arange(C)
        self.data_file.close()

        # edit and save the yaml
        self.yaml['xrd']['data']['shape'] = '$(len(A_vals), len(B_vals), len(C_vals))'
        self.yaml['xrd']['params'].update({'idx_A': 0,
                                           'idx_B': 1,
                                           'idx_C': 2,
                                           'idx_detx': 3,
                                           'idx_dety': 4,
                                           'A_vals': "$dfile['entry/A'][()]",
                                           'B_vals': "$dfile['entry/B'][()]",
                                           'C_vals': "$dfile['entry/C'][()]",
                                           'dims': "$range(0, 4)"})

        self.yaml['xrd']['axis_labels'] = {0: {'dim': '$idx_A', 'name': 'A', 'value': '$A_vals', 'units': 'pixels'},
                                           1: {'dim': '$idx_B', 'name': 'B', 'value': '$B_vals', 'units': 'pixels'},
                                           2: {'dim': '$idx_C', 'name': 'C', 'value': '$C_vals', 'units': 'pixels'},
                                           3: self.detX_axis_label,
                                           4: self.detY_axis_label}

        self.save_yaml_and_change_process_list()
        run_protected_plugin_runner(tu.set_options(self.data_file_path,
                                                   process_file=self.process_list_path,
                                                   out_path=self.test_folder))

        result = h5.File(os.path.join(self.test_folder, 'test_processed.nxs'), 'r')['entry/final_result_xrd/data']
        np.testing.assert_array_equal(result.shape, expected_output_shape,
                                      err_msg='The output shape is not as expected.')
        result_corners = result[..., -1, -1]
        np.testing.assert_equal(result_corners.dtype, expected_top_corners.dtype,
                                err_msg='The array does not output the correct type.')
        np.testing.assert_array_equal(result_corners, expected_top_corners,
                                      err_msg="The output values are not as expected")

    def setUp(self):
        self.test_folder = tempfile.mkdtemp(suffix='template_test/')
        self.tif_folder = os.path.join(self.test_folder, 'tiffs/')
        os.mkdir(self.tif_folder)

        # copy across the process list to the working directory
        self.process_list_path = os.path.join(self.test_folder, 'xrd_template_test.nxs')
        shutil.copyfile(tu.get_test_process_path('xrd_template_test.nxs'),
                        self.process_list_path)

        self.detX_axis_label = {'dim': '$idx_detx', 'name': 'detector_x', 'value': None, 'units': 'pixels'}
        self.detY_axis_label = {'dim': '$idx_dety', 'name': 'detector_y', 'value': None, 'units': 'pixels'}

        self.yaml = OrderedDict()
        # now make some standard modifications
        self.yaml['inherit'] = [tu.get_test_data_path(os.path.join('i18_templates', 'xrd_calibration.yml'))]
        self.yaml['xrd'] = OrderedDict()
        self.yaml['xrd']['params'] = {}
        self.yaml['xrd']['data'] = {}
        self.yaml['xrd']['data']['folder'] = self.tif_folder
        self.yaml['xrd']['params']['cfile'] = \
            "$h5py.File('%s', 'r')" % tu.get_test_data_path('LaB6_calibration_new.nxs')

        self.yaml['xrd']['patterns'] = {}
        self.yaml['xrd']['patterns']['DIFFRACTION'] = {'core_dims': '$(idx_detx, idx_dety)',
                                                       'slice_dims': '$tuple([d for d in dims if d not in [idx_detx, idx_dety]])'}
        self.yaml['xrd']['axis_labels'] = {}
        self.yaml['xrd']['metadata'] = {}
        self.data_file_path = os.path.join(self.test_folder, 'test_data.nxs')
        self.data_file = h5.File(self.data_file_path, 'w')  # this will have the axes in.

    def tearDown(self):
        shutil.rmtree(self.test_folder, ignore_errors=True)

    def create_N_tiffs(self, N, file_pattern='%04d.tif', frame_size=(10, 13)):
        '''
        Creates a stack of N tiffs with given frame_size and file pattern in self.tif_folder.
        :param N: The number of tiffs in the stack
        :param file_pattern: The printf pattern for the file names.
        :param frame_size: The shape of the frames. Default: (10,13).
        '''

        data = np.ones(frame_size, dtype=np.float)
        for idx in range(N):
            file_path = os.path.join(self.tif_folder, (file_pattern % idx))
            tifffile.imsave(file_path, data*idx)

    def save_yaml_and_change_process_list(self):
        self.yml_path = os.path.join(self.test_folder, 'xrd_tiff.yml')
        with open(self.yml_path, 'w') as f:
            yu.dump_yaml(self.yaml, f)
        # now set the template path in the process list
        # uses the parameter name instead of number
        # because the number can change between runs
        self.process_list = Content()
        self.process_list.fopen(self.process_list_path, update=False)
        self.process_list.modify('1', 'yaml_file', self.yml_path)
        self.process_list.save(self.process_list_path)


if __name__ == '__main__':
    unittest.main()
