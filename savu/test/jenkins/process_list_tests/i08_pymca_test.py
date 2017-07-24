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
.. module:: nx_xrd_loader_test
   :platform: Unix
   :synopsis: testing the nx_xrd loader

.. moduleauthor:: Aaron Parsons <scientificsoftware@diamond.ac.uk>

"""
import unittest
from savu.test import test_utils as tu
from savu.test.travis.framework_tests.plugin_runner_test import \
    run_protected_plugin_runner
import h5py as h5
import os
import numpy as np
import shutil

def change_permissions_recursive(path, mode):
    for root, dirs, files in os.walk(path, topdown=False):
        for di in [os.path.join(root,d) for d in dirs]:
            os.chmod(di, mode)
    for fil in [os.path.join(root, f) for f in files]:
            os.chmod(fil, mode)
            
class I08PymcaTest(unittest.TestCase):
     
#     def test_i08(self):
#         data_file = tu.get_test_big_data_path('pymca_live_processing_test/i08-10471.nxs')
#         process_file = tu.get_test_process_path('i08_pymca_process.nxs')
#         run_protected_plugin_runner(tu.set_options(data_file,
#                                                    process_file=process_file))

    def test_i08_REGRESSION(self):
        data_file = tu.get_test_big_data_path('pymca_live_processing_test/i08-10471.nxs')
        process_file = tu.get_test_process_path('i08_pymca_process.nxs')
        outdir = '/tmp/pymca_i08_test/'
        if os.path.exists(outdir):
            shutil.rmtree(outdir)
        os.makedirs(outdir)
        options = tu.set_options(data_file,process_file=process_file,out_path=outdir)
        run_protected_plugin_runner(options)
        change_permissions_recursive(options['out_path'], 777)
        
        f_test = h5.File(options['out_path']+os.sep+options['out_folder']+'_processed.nxs','r') #  the result of this test
        f_known = h5.File(tu.get_test_big_data_path('pymca_live_processing_test/savu_test_result/test_processed.nxs'),'r')#  a known good result from the same data
        # first we just do a direct comparison of the data. This should be equal exactly.
        data = '/entry/final_result_fluo/data'
        elements = 'entry/final_result_fluo/PeakElements'
#         test=np.around(f_test[data][...], decimals=-1)
#         known=np.around(f_known[data][...], decimals=-1)
#         self.assertEqual(test, known)
        np.testing.assert_array_almost_equal(f_test[data][...], f_known[data][...], 0) # this needs to be -1
        self.assertListEqual(list(f_test[elements][...]), list(f_known[elements][...]))
        


if __name__ == "__main__":
    unittest.main()
