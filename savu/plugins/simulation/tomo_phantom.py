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
.. module:: A wrapper for TomoPhantom software
   :platform: Unix
   :synopsis: TomoPhantom package provides an access to simulated phantom libraries and projection data in 2D/3D/4D
   
.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""

import savu.plugins.utils as pu
from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin

import tomophantom
from tomophantom import TomoP2D, TomoP3D
import os
from savu.data.plugin_list import CitationInformation
import numpy as np

@register_plugin
class TomoPhantom(Plugin, CpuPlugin):
    """
    '2D': Generate 2D phantom and sinogram using Phantom2DLibrary.dat;
    '3D': Generate 3D phantom and projection data using Phantom3DLibrary.dat;
    '4D': Generate 4D phantom and projection data using Phantom3DLibrary.dat;
    
    :param method: Select a method |2D|3D|4D|. Default: '2D'.
    :param model: Select a model (number) from phantom library (see txt files). Default: 1.
    :param dims: Set dimension of the phantom. Default: 256.
    :param proj_num: The number of projections. Default: 360.
    :param detectors_num: The number of (horizontal) detectors. Default:300.
    :param out_datasets: Default out dataset names. Default: ['tomo', 'model']
    """

    def __init__(self):
        super(TomoPhantom, self).__init__('TomoPhantom')

    def nInput_datasets(self):
        return 1

    def nOutput_datasets(self):
        return 2
    
    def setup(self):
        in_dataset, self.out_dataset = self.get_datasets()
        #out_dataset[0].create_dataset(in_dataset[0])
        in_pData, self.out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('SINOGRAM', 'single')
        self.out_shape = self.new_shape(in_dataset[0].get_shape(), in_dataset[0])
        
        self.out_dataset[0].create_dataset(patterns=in_dataset[0],
                                           axis_labels=in_dataset[0],
                                           shape=self.out_shape)
        self.out_pData[0].plugin_data_setup('SINOGRAM', 'single')
        
        
        self.angles = np.linspace(0.0,179.9,self.parameters['proj_num'],dtype='float32')
        self.out_dataset[0].meta_data.set('rotation_angle', self.angles)
        
    def new_shape(self, full_shape, data):
        # example of a function to calculate a new output data shape based on
        # the input data shape
        core_dirs = data.get_core_dimensions()
        new_shape = list(full_shape)
        if ((self.parameters['method'] == 'Phantom2D') or (self.parameters['method'] == 'Phantom3D')):
            for dim in core_dirs:
                new_shape[dim] = self.parameters['dims']
        if (self.parameters['method'] == 'Sino2D'):
            new_shape= (self.parameters['proj_num'], new_shape[1], self.parameters['detectors_num'])
        return tuple(new_shape)
    def pre_process(self):
        # set parameters for TomoPhantom:
        self.method = self.parameters['method']
        self.model = self.parameters['model']
        self.dims = self.parameters['dims']
        self.proj_num = self.parameters['proj_num']
        self.detectors_num = self.parameters['detectors_num']
        path = os.path.dirname(tomophantom.__file__)
        self.path_library2D = os.path.join(path, "Phantom2DLibrary.dat")
        self.path_library3D = os.path.join(path, "Phantom3DLibrary.dat")
        #print "The full data shape is", self.get_in_datasets()[0].get_shape()
        #print "Example is", self.parameters['example']
    def process_frames(self, data):
        # print "The input data shape is", data[0].shape
        if (self.method == '2D'):
            # get a 2D phantom
            model = TomoP2D.Model(self.model, self.dims, self.path_library2D)
            # get a 2D sinogram
            projdata = TomoP2D.ModelSino(self.model, self.dims, self.detectors_num, self.angles, self.path_library2D)
        if (self.method == '3D'):
            # get a 3D phantom
            frame_idx = self.out_pData[0].get_current_frame_idx()[0]
            model = TomoP3D.ModelSub(self.model, self.dims, (frame_idx, frame_idx+1), self.path_library3D)
            model = np.swapaxes(model,0,1)
            # get a 3D projection data 
            projdata = TomoP3D.ModelSinoSub(self.model, self.dims, self.detectors_num, self.dims, (frame_idx, frame_idx+1), self.angles, self.path_library3D)
            #print(np.min(result))
            #print(np.max(result))
        if (self.method == '4D'):
            #TODO
            ###
            return [projdata, model]
    def post_process(self):
        pass
    
    def get_citation_information(self):
        cite_info1 = CitationInformation()
        cite_info1.name = 'citation1'
        cite_info1.description = \
            ("TomoPhantom is a software package to generate 2D-4D analytical phantoms and their Radon transforms for various testing purposes.")
        cite_info1.bibtex = \
            ("@article{kazantsevTP2018,\n" +
             "title={TomoPhantom, a software package to generate 2D-4D analytical phantoms for CT image reconstruction algorithm benchmarks},\n" +
             "author={Daniil and Kazantsev, Valery and Pickalov, Srikanth and Nagella, Edoardo and Pasca, Philip and Withers},\n" +
             "journal={Software X},\n" +
             "volume={7},\n" +
             "number={--},\n" +
             "pages={150--155},\n" +
             "year={2018},\n" +
             "publisher={Elsevier}\n" +
             "}")
        cite_info1.endnote = \
            ("%0 Journal Article\n" +
             "%T TomoPhantom, a software package to generate 2D-4D analytical phantoms for CT image reconstruction algorithm benchmarks\n" +
             "%A Kazantsev, Daniil\n" +
             "%A Pickalov, Valery\n" +
             "%A Nagella, Srikanth\n" +
             "%A Pasca, Edoardo\n" +
             "%A Withers, Philip\n" +
             "%J Software X\n" +
             "%V 7\n" +
             "%N --\n" +
             "%P 150--155\n" +
             "%@ --\n" +
             "%D 2018\n" +
             "%I Elsevier\n")
        cite_info1.doi = "doi:10.1016/j.softx.2018.05.003"
        
        return [cite_info1]