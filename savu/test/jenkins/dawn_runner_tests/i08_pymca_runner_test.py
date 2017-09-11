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
from scripts.dawn_runner import run_savu
import h5py as h5
import os
import scripts.config_generator.config_utils as cu
import savu.plugins.utils as pu
from savu.plugins.utils import dawn_plugins
import threading

class I08PymcaRunnerTest(unittest.TestCase):
    '''
    This test runs and checks the savu-side code for the runner in dawn. The rest should just be GUI
    '''

    def runSavu(self, path2plugin, params, metaOnly, inputs):
        '''
        this is copy paste of how it is implemented in org.dawnsci.python.rpc source code.
        '''
        print("running savu")
        result = run_savu.runSavu(path2plugin, params, metaOnly, inputs, self.persistence)
        print("done")
        return result

    def test_i08(self):
        cu.populate_plugins()
        data_file = tu.get_test_big_data_path('pymca_live_processing_test/i08-10471.nxs')
        data = h5.File(data_file,'r')['/entry/xmapMca/data']
        inputs = {}
        inputs['data'] = data[0,0,0,:]
        inputs['dataset_name'] = ''
        inputs['xaxis_title'] = None
        metaOnly = True
        self.persistence = {}
        self.persistence['sys_path_0_lock'] = threading.Lock()
        self.persistence['sys_path_0_set'] = False
        self.persistence['plugin_object'] = None
        self.persistence['axis_labels'] = None
        self.persistence['axis_values'] = None
        self.persistence['string_key'] = None
        self.persistence['parameters'] = None
        self.persistence['aux'] = {}
        params={}
        params['config']={}
        params['config']['value'] = tu.get_test_big_data_path('pymca_live_processing_test/10471.cfg')
        path2plugin = pu.dawn_plugins['Pymca']['path2plugin']# set by dawn-side code
 
        self.runSavu(path2plugin, params, metaOnly, inputs)

    def test_i08_REGRESSION(self):
        cu.populate_plugins()
        data_file = h5.File(tu.get_test_big_data_path('pymca_live_processing_test/dawn_test_result/result.nxs'),'r')
        data = data_file['/raw_entry/xmapMca/data']
        inputs = {}
        
        inputs['dataset_name'] = ''
        inputs['xaxis_title'] = None
        metaOnly = True
        self.persistence = {}
        self.persistence['sys_path_0_lock'] = threading.Lock()
        self.persistence['sys_path_0_set'] = False
        self.persistence['plugin_object'] = None
        self.persistence['axis_labels'] = None
        self.persistence['axis_values'] = None
        self.persistence['string_key'] = None
        self.persistence['parameters'] = None
        self.persistence['aux'] = {}
        params={}
        params['config']={}
        params['config']['value'] = tu.get_test_big_data_path('pymca_live_processing_test/10471.cfg')
        path2plugin = pu.dawn_plugins['Pymca']['path2plugin']# set by dawn-side code
        pts = [(39,51),
               (45,25),
               (18,29),
               (37,96),
               (8,110)] # just do 5 points for now, is full regression necessary?
        for y,x in pts:
            inputs['data'] = data[x,y,0,:]
            out = self.runSavu(path2plugin, params, metaOnly, inputs)
            aux = out['auxiliary']
            entry = 'entry/auxiliary/0-Python Script - Savu/'
            for key in aux.keys():
                print(key,x,y)
                foo=data_file[entry+key+'/data'][x,y]
                self.assertAlmostEqual(aux[key],foo,delta=0.5)

    def test_i08_notaux(self):
        cu.populate_plugins()
        data_file = tu.get_test_big_data_path('pymca_live_processing_test/i08-10471.nxs')
        data = h5.File(data_file,'r')['/entry/xmapMca/data']
        inputs = {}
        inputs['data'] = data[0,0,0,:]
        inputs['dataset_name'] = ''
        inputs['xaxis_title'] = None
        metaOnly = False
        self.persistence = {}
        self.persistence['sys_path_0_lock'] = threading.Lock()
        self.persistence['sys_path_0_set'] = False
        self.persistence['plugin_object'] = None
        self.persistence['axis_labels'] = None
        self.persistence['axis_values'] = None
        self.persistence['string_key'] = None
        self.persistence['parameters'] = None
        self.persistence['aux'] = {}
        params={}
        params['config']={}
        params['config']['value'] = tu.get_test_big_data_path('pymca_live_processing_test/10471.cfg')
        path2plugin = pu.dawn_plugins['Pymca']['path2plugin']# set by dawn-side code
        self.runSavu(path2plugin, params, metaOnly, inputs)

    def test_i08_notaux_REGRESSION(self):
        cu.populate_plugins()
        data_file = h5.File(tu.get_test_big_data_path('pymca_live_processing_test/dawn_test_result/result.nxs'),'r')
        data = data_file['/raw_entry/xmapMca/data']
        inputs = {}
        
        inputs['dataset_name'] = ''
        inputs['xaxis_title'] = None
        metaOnly = True
        self.persistence = {}
        self.persistence['sys_path_0_lock'] = threading.Lock()
        self.persistence['sys_path_0_set'] = False
        self.persistence['plugin_object'] = None
        self.persistence['axis_labels'] = None
        self.persistence['axis_values'] = None
        self.persistence['string_key'] = None
        self.persistence['parameters'] = None
        self.persistence['aux'] = {}
        params={}
        params['config']={}
        params['config']['value'] = tu.get_test_big_data_path('pymca_live_processing_test/10471.cfg')
        path2plugin = pu.dawn_plugins['Pymca']['path2plugin']# set by dawn-side code
        pts = [(39,51),
               (45,25),
               (18,29),
               (37,96),
               (8,110)] # just do 5 points for now, is full regression necessary?
        for y,x in pts:
            inputs['data'] = data[x,y,0,:]
            out = self.runSavu(path2plugin, params, metaOnly, inputs)
            aux = out['auxiliary']
            entry = 'entry/auxiliary/0-Python Script - Savu/'
            for key in aux.keys():
                print(key,x,y)
                foo=data_file[entry+key+'/data'][x,y]
                self.assertAlmostEqual(aux[key],foo,delta=0.5)

if __name__ == "__main__":
    unittest.main()
