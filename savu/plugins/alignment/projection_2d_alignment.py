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
.. module:: projection_2d_alignment
   :platform: Unix
   :synopsis: either calculates horizontal-vertical shift vectors for fixing misaligned projection data
   or register misiligned projections explicitly

.. moduleauthor:: Daniil Kazantsev & Yousef Moazzam <scientificsoftware@diamond.ac.uk>
"""

from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin
from skimage.registration import phase_cross_correlation
from skimage import transform as tf
from savu.core.iterate_plugin_group_utils import check_if_in_iterative_loop
import copy

from mpi4py import MPI
import logging

import numpy as np

@register_plugin
class Projection2dAlignment(Plugin, CpuPlugin):
    def __init__(self):
        super(Projection2dAlignment, self).__init__('Projection2dAlignment')
        self.iterations_number = None
        self.iterate_group = None
        self.error_alignment_vector = None

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('PROJECTION', self.get_max_frames())
        in_pData[1].plugin_data_setup('PROJECTION', self.get_max_frames())

        # create a metadata for storing shift vectors
        slice_dirs = list(in_dataset[0].get_slice_dimensions())
        new_shape = (in_dataset[0].get_shape()[slice_dirs[0]], 2)
        out_dataset[0].create_dataset(shape=new_shape,
                                    axis_labels=['x.angles', 'y.shifts'],
                                    remove=False)
        out_dataset[0].add_pattern("METADATA", core_dims=(1,), slice_dims=(0,))
        out_pData[0].plugin_data_setup('METADATA', self.get_max_frames())

        if self.parameters['registration']:
            # generate a dataset with shifted (registered) projections
            out_dataset[1].create_dataset(in_dataset[1])
            # set preview metadata for the dataset containing the shifted
            # projections
            # get the original preview parameters from the loader
            get_original_preview = self.exp.meta_data.plugin_list.plugin_list[0]['data']['preview']
            out_dataset[1].get_preview().set_preview(get_original_preview, load=True)
            out_pData[1].plugin_data_setup('PROJECTION', self.get_max_frames())

        # check if there is an iterative loop and the exp metadata on error shifts exists
        self.iterate_group = check_if_in_iterative_loop(self.exp)
        self.iterations_number = 1
        if bool(self.iterate_group):
            self.iterations_number = self.iterate_group._ip_fixed_iterations
            if 'error_alignment_vector' in list(self.exp.meta_data.dict.keys()):
                self.error_alignment_vector = self.exp.meta_data.dict['error_alignment_vector']
            else:
                self.error_alignment_vector = np.zeros(self.iterations_number)
                self.exp.meta_data.set('error_alignment_vector', copy.deepcopy(self.error_alignment_vector))
        else:
            self.error_alignment_vector = np.zeros(self.iterations_number)
            self.exp.meta_data.set('error_alignment_vector', copy.deepcopy(self.error_alignment_vector))

    def process_frames(self, data):
        projection = data[0]   # an original data to align to (a STATIC reference)
        projection_align = data[1] # a projection for alignment to the given reference

        # calculate x and y shifts
        shifts, error, diffphase = phase_cross_correlation(
                    projection, projection_align, upsample_factor=self.parameters['upsample_factor'])

        if self.parameters['registration']:
            # apply a transformation (translation) to the projection according to
            # the calculated shifts, in order to align it
            transformation = \
                tf.SimilarityTransform(translation=(shifts[1], shifts[0]))
            transformed_image = tf.warp(projection, transformation, order=self.parameters['interpolation_order'],
                mode='edge')
            return [shifts, transformed_image]
        else:
            return [shifts]          

    def post_process(self):
        out_data = self.get_out_datasets()[0]
        shift_vector = out_data.data[:, :]  # get a shift vector
        shift_vector[:, [0, 1]] = shift_vector[:, [1, 0]]  # swap axis in shift vector
        # get previous projection shifts first from experimental metadata
        shift_vector_prev = self.exp.meta_data.dict['projection_shifts']
        shift_vector_prev += shift_vector
        self.exp.meta_data.set('projection_shifts', shift_vector_prev.copy())
        in_meta_data = self.get_in_meta_data()[0]
        in_meta_data.set('projection_shifts', shift_vector_prev.copy())
        # filling the error vector
        error_scalar = np.sum(np.sqrt(shift_vector[:, 0]*shift_vector[:, 0] + shift_vector[:, 1]*shift_vector[:, 1]))
        # print just for the first process
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        if rank == 0:
            print(f"The alignment error is:  {error_scalar}")
            logging.debug("The alignment error is %f" % error_scalar)
        if self.iterations_number == 1:
            self.error_alignment_vector[0] = error_scalar
        else:
            self.error_alignment_vector[self.iterate_group._ip_iteration] = error_scalar
        self.exp.meta_data.set('error_alignment_vector', self.error_alignment_vector.copy())

    def get_max_frames(self):
        return 'single'

    def nInput_datasets(self):
        return 2

    def nOutput_datasets(self):
        if self.parameters['registration']:
            return 2
        else:
            return 1
