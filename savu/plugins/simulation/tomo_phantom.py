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
   :synopsis: TomoPhantom package provides an access to simulated phantom libraries and projection data 2D/3D

.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""

import savu.plugins.utils as pu
from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin

import tomophantom
from tomophantom import TomoP2D, TomoP3D
from tomophantom.supp.artifacts import _Artifacts_
import os
from savu.data.plugin_list import CitationInformation
import numpy as np

@register_plugin
class TomoPhantom(Plugin, CpuPlugin):
    """
    A plugin for TomoPhantom software which generates synthetic phantoms and \
    projection data (2D from Phantom2DLibrary.dat and 3D from Phantom3DLibrary.dat)

    :param geom_model: Select a model (integer) from the library (see TomoPhantom files). Default: 1.
    :param geom_model_size: Set the size of the phantom. Default: 256.
    :param geom_projections_total: The total number of projections. Default: 360.
    :param geom_detectors_horiz: The size of _horizontal_ detectors. Default: 300.
    :param artifacts_noise_type: Set the noise type, Poisson or Gaussian. Default: 'Poisson'.
    :param artifacts_noise_sigma: Define noise amplitude. Default: 5000.
    :param artifacts_misalignment_maxamplitude: Incorporate misalignment into projections (in pixels). Default: None.
    :param artifacts_zingers_percentage: add broken pixels to projections, e.g. 0.25. Default: None.
    :param artifacts_stripes_percentage: the amount of stripes in the data, e.g. 1.0. Default: None.
    :param artifacts_stripes_maxthickness: defines the maximal thickness of a stripe. Default: 3.0.
    :param artifacts_stripes_intensity: to incorporate the change of intensity in the stripe. Default: 0.3.
    :param artifacts_stripes_type: set the stripe type between full and partial. Default: 'full'.
    :param artifacts_stripes_variability: the intensity variability of a stripe. Default:  0.007.
    :param out_datasets: Default out dataset names. Default: ['tomo', 'model']
    """

    def __init__(self):
        super(TomoPhantom, self).__init__('TomoPhantom')

    def get_max_frames(self):
        return 'single'

    def nInput_datasets(self):
        return 1

    def nOutput_datasets(self):
        return 2

    def map_volume_dimensions(self, data):
        data._finalise_patterns()
        dim_rotAngle = data.get_data_patterns()['PROJECTION']['main_dir']
        sinogram = data.get_data_patterns()['SINOGRAM']
        dim_detY = sinogram['main_dir']

        core_dirs = sinogram['core_dims']
        dim_detX = list(set(core_dirs).difference(set((dim_rotAngle,))))[0]

        dim_volX = dim_rotAngle
        dim_volY = dim_detY
        dim_volZ = dim_detX
        return dim_volX, dim_volY, dim_volZ

    def setup(self):
        in_dataset, self.out_dataset = self.get_datasets()
        in_pData, self.out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('SINOGRAM', self.get_max_frames())

        [self.out_shape_sino, out_shape_phantom] = self.new_shape(in_dataset[0].get_shape(), in_dataset[0])
        self.out_dataset[0].create_dataset(patterns=in_dataset[0],
                                           axis_labels=in_dataset[0],
                                           shape=self.out_shape_sino)
        self.out_pData[0].plugin_data_setup('SINOGRAM',self.get_max_frames())

        dim_volX, dim_volY, dim_volZ = \
            self.map_volume_dimensions(in_dataset[0])

        axis_labels = [0]*3
        axis_labels = {in_dataset[0]:
                       [str(dim_volX) + '.voxel_x.voxels',
                        str(dim_volY) + '.voxel_y.voxels',
                        str(dim_volZ) + '.voxel_z.voxels']}

        self.out_dataset[1].create_dataset(axis_labels=axis_labels,
                                           shape=out_shape_phantom)
        self.out_dataset[1].add_volume_patterns(dim_volX, dim_volY, dim_volZ)

        self.out_pData[1].plugin_data_setup('VOLUME_XZ', self.get_max_frames())

        self.angles = np.linspace(0.0,179.999,self.parameters['geom_projections_total'],dtype='float32')
        self.out_dataset[0].meta_data.set('rotation_angle', self.angles)

    def new_shape(self, full_shape, data):
        # calculate a new output data shape based on the input data shape
        core_dirs = data.get_core_dimensions()
        new_shape_sino = list(full_shape)
        new_shape_phantom = list(full_shape)
        new_shape_sino= (self.parameters['geom_projections_total'], new_shape_sino[1], self.parameters['geom_detectors_horiz'])
        for dim in core_dirs:
            new_shape_phantom[dim] = self.parameters['geom_model_size']
        return [tuple(new_shape_sino), tuple(new_shape_phantom)]

    def pre_process(self):
        # set parameters for TomoPhantom:
        self.model = self.parameters['geom_model']
        self.dims = self.parameters['geom_model_size']
        self.proj_num = self.parameters['geom_projections_total']
        self.detectors_num = self.parameters['geom_detectors_horiz']
        path = os.path.dirname(tomophantom.__file__)
        self.path_library2D = os.path.join(path, "Phantom2DLibrary.dat")
        self.path_library3D = os.path.join(path, "Phantom3DLibrary.dat")
        #print "The full data shape is", self.get_in_datasets()[0].get_shape()

    def process_frames(self, data):
        # print "The input data shape is", data[0].shape
        if (self.out_shape_sino[1] == 1):
            # create a 2D phantom
            model = TomoP2D.Model(self.model, self.dims, self.path_library2D)
            # create a 2D sinogram
            projdata_clean = TomoP2D.ModelSino(self.model, self.dims, self.detectors_num, self.angles, self.path_library2D)
            # Adding artifacts and noise
            # forming dictionaries with artifact types
            _noise_ =  {'type' : self.parameters['artifacts_noise_type'],
                        'sigma' : self.parameters['artifacts_noise_sigma'],
                        'seed' : 0,
                        'prelog' : False}

            # misalignment dictionary
            _sinoshifts_ = {}
            if self.parameters['artifacts_misalignment_maxamplitude'] is not None:
                _sinoshifts_ = {'maxamplitude' : self.parameters['artifacts_misalignment_maxamplitude']}

            # adding zingers and stripes
            _zingers_ = {}
            if self.parameters['artifacts_zingers_percentage'] is not None:
                _zingers_ = {'percentage' : self.parameters['artifacts_zingers_percentage'],
                            'modulus' : 10}

            _stripes_ = {}
            if self.parameters['artifacts_stripes_percentage'] is not None:
                _stripes_ = {'percentage' : self.parameters['artifacts_stripes_percentage'],
                             'maxthickness' : self.parameters['artifacts_stripes_maxthickness'],
                             'intensity' : self.parameters['artifacts_stripes_intensity'],
                             'type' : self.parameters['artifacts_stripes_type'],
                             'variability' : self.parameters['artifacts_stripes_variability']}

            if self.parameters['artifacts_misalignment_maxamplitude'] is not None:
                [projdata, shifts] = _Artifacts_(projdata_clean, _noise_, _zingers_, _stripes_, _sinoshifts_)
            else:
                projdata = _Artifacts_(projdata_clean, _noise_, _zingers_, _stripes_, _sinoshifts_)
        else:
            # create a 3D phantom
            frame_idx = self.out_pData[0].get_current_frame_idx()[0]
            model = TomoP3D.ModelSub(self.model, self.dims, (frame_idx, frame_idx+1), self.path_library3D)
            model = np.swapaxes(model,0,1)
            model = np.flipud(model[:,0,:])
            # create a 3D projection data
            projdata_clean = TomoP3D.ModelSinoSub(self.model, self.dims, self.detectors_num, self.dims, (frame_idx, frame_idx+1), self.angles, self.path_library3D)
            # Adding artifacts and noise
            # forming dictionaries with artifact types
            _noise_ =  {'type' : self.parameters['artifacts_noise_type'],
                        'sigma' : self.parameters['artifacts_noise_sigma'],
                        'seed' : 0,
                        'prelog' : False}

            # misalignment dictionary
            _sinoshifts_ = {}
            if self.parameters['artifacts_misalignment_maxamplitude'] is not None:
                _sinoshifts_ = {'maxamplitude' : self.parameters['artifacts_misalignment_maxamplitude']}

            # adding zingers and stripes
            _zingers_ = {}
            if self.parameters['artifacts_zingers_percentage'] is not None:
                _zingers_ = {'percentage' : self.parameters['artifacts_zingers_percentage'],
                            'modulus' : 10}

            _stripes_ = {}
            if self.parameters['artifacts_stripes_percentage'] is not None:
                _stripes_ = {'percentage' : self.parameters['artifacts_stripes_percentage'],
                             'maxthickness' : self.parameters['artifacts_stripes_maxthickness'],
                             'intensity' : self.parameters['artifacts_stripes_intensity'],
                             'type' : self.parameters['artifacts_stripes_type'],
                             'variability' : self.parameters['artifacts_stripes_variability']}

            if self.parameters['artifacts_misalignment_maxamplitude'] is not None:
                [projdata, shifts] = _Artifacts_(projdata_clean, _noise_, _zingers_, _stripes_, _sinoshifts_)
            else:
                projdata = _Artifacts_(projdata_clean, _noise_, _zingers_, _stripes_, _sinoshifts_)
            projdata = np.swapaxes(projdata,0,1)
        return [projdata, model]

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
