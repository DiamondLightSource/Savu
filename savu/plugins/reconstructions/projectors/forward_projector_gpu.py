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
.. module:: forward_projector_gpu
   :platform: Unix
   :synopsis: A forward data projector using ToMoBAR software

.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""

from savu.plugins.plugin import Plugin
from savu.plugins.driver.gpu_plugin import GpuPlugin
from savu.plugins.utils import register_plugin
from savu.core.iterate_plugin_group_utils import check_if_in_iterative_loop

from tomobar.methodsDIR import RecToolsDIR
import numpy as np
import copy

@register_plugin
class ForwardProjectorGpu(Plugin, GpuPlugin):
    def __init__(self):
        super(ForwardProjectorGpu, self).__init__('ForwardProjectorGpu')
        self.angles_total = None
        self.det_horiz_half = None
        self.detectors_horiz = None
        self.projection_shifts = None
        self.cor = None
        self.angles_rad = None

    def pre_process(self):
        # getting metadata for CoR
        in_meta_data = self.get_in_meta_data()[0]
        self.cor = in_meta_data.get('centre_of_rotation')
        self.cor = np.mean(self.cor)  # CoR must be a scalar for 3D geometry

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('VOLUME_XZ', 'multiple')

        in_meta_data = self.get_in_meta_data()[0]
        # extracting parameters from metadata
        angles_meta_deg = in_meta_data.get('rotation_angle')
        self.angles_rad = np.deg2rad(angles_meta_deg)
        self.detectors_horiz = in_meta_data.get('detector_x_length')

        # get experimental metadata of projection_shifts
        if 'projection_shifts' in list(self.exp.meta_data.dict.keys()):
            self.projection_shifts = self.exp.meta_data.dict['projection_shifts']

        # deal with user-defined parameters
        if self.parameters['angles_deg'] is not None:
            angles_list = self.parameters['angles_deg']
            self.angles_rad = np.deg2rad(np.linspace(angles_list[0], angles_list[1], angles_list[2], dtype=np.float))
        if self.parameters['centre_of_rotation'] is not None:
            self.cor = self.parameters['centre_of_rotation']
        if self.parameters['det_horiz'] is not None:
            self.detectors_horiz = self.parameters['det_horiz']

        self.det_horiz_half = 0.5 * self.detectors_horiz
        self.angles_total = len(self.angles_rad)

        out_shape_sino = self.new_shape(in_dataset[0].get_shape(), in_dataset[0])
        labels = ['rotation_angle.degrees', 'detector_y.pixel', 'detector_x.pixel']
        pattern = {'name': 'SINOGRAM', 'slice_dims': (1,),
                   'core_dims': (2, 0)}
        out_dataset[0].create_dataset(axis_labels=labels, shape=out_shape_sino)
        out_dataset[0].add_pattern(pattern['name'],
                                   slice_dims=pattern['slice_dims'],
                                   core_dims=pattern['core_dims'])
        pattern2 = {'name': 'PROJECTION', 'slice_dims': (0,),
                    'core_dims': (1, 2)}
        out_dataset[0].add_pattern(pattern2['name'],
                                   slice_dims=pattern2['slice_dims'],
                                   core_dims=pattern2['core_dims'])
        out_pData[0].plugin_data_setup(pattern['name'], self.get_max_frames())
        out_dataset[0].meta_data.set('rotation_angle', copy.deepcopy(angles_meta_deg))

    def process_frames(self, data):
        object = data[0].astype(np.float32)
        object = np.where(np.isfinite(object), object, 0)
        object_size = np.shape(object)[0]
        vert_size = None # 2D case
        # dealing with 3D data case
        if object.ndim == 3:
            vert_size = np.shape(object)[1]
            iterate_group = check_if_in_iterative_loop(self.exp)
            gpu_device_index = self.parameters['GPU_index']
            if iterate_group is None:
                self.angles_rad = -self.angles_rad
            else:
                # only apply the sign change on iteration 0, not on subsequent
                # iterations
                if iterate_group._ip_iteration == 0:
                    self.angles_rad = -self.angles_rad

            if iterate_group is not None and \
                iterate_group._ip_iteration > 0 and \
                'projection_shifts' in list(self.exp.meta_data.dict.keys()):
                # update projection_shifts from experimental metadata
                self.projection_shifts = \
                    self.exp.meta_data.dict['projection_shifts']
            cor = np.zeros((np.shape(self.projection_shifts)))
            cor[:, 0] = (-self.cor + self.det_horiz_half - 0.5) - self.projection_shifts[:, 0]
            cor[:, 1] = -self.projection_shifts[:, 1] - 0.5
        else:
            cor = (-self.cor + self.det_horiz_half - 0.5)
        RectoolsDIRECT = RecToolsDIR(DetectorsDimH=self.detectors_horiz,  # DetectorsDimH # detector dimension (horizontal)
                                  DetectorsDimV=vert_size,  # DetectorsDimV # detector dimension (vertical)
                                  CenterRotOffset=cor,  # Center of Rotation
                                  AnglesVec=self.angles_rad,  # array of angles in radians
                                  ObjSize=object_size,  # a scalar to define reconstructed object dimensions
                                  device_projector=gpu_device_index)
        if vert_size is not None:
            projected = RectoolsDIRECT.FORWPROJ(np.require(np.swapaxes(object, 0, 1), requirements='CA'))
            projected = np.require(np.swapaxes(projected, 0, 1), requirements='CA')
        else:
            projected = RectoolsDIRECT.FORWPROJ(object)
        return projected

    def new_shape(self, full_shape, data):
        # calculate a new output data shape based on the input data shape
        new_shape_sino_orig = list(full_shape)
        new_shape_sino = (self.angles_total, new_shape_sino_orig[1], self.detectors_horiz)
        return tuple(new_shape_sino)

    def post_process(self):
        # populate CoR value
        in_datasets, out_datasets = self.get_datasets()
        sdirs = in_datasets[0].get_slice_dimensions()
        cor_vect = np.ones(np.prod([in_datasets[0].get_shape()[i] for i in sdirs]))
        self.cor *= cor_vect
        out_datasets[0].meta_data.set('centre_of_rotation', copy.deepcopy(self.cor))

    def get_max_frames(self):
        return 'multiple'

    def nInput_datasets(self):
        return 1

    def nOutput_datasets(self):
        return 1
