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
.. module:: i13_ptycho_loader
   :platform: Unix
   :synopsis: A class for loading nxstxm data

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>
"""

from savu.plugins.loaders.mapping_loaders.base_multi_modal_loader \
    import BaseMultiModalLoader
import numpy as np
from savu.plugins.utils import register_plugin
import logging
import h5py


#@register_plugin
class I13PtychoLoader(BaseMultiModalLoader):
    """
    A class to load tomography data from an NXstxm file
    :param mono_energy: The mono energy. Default: 9.1.
    :param is_tomo: The mono energy. Default: True.
    :param theta_step: The theta step. Default:1.0.
    :param theta_start: The theta start. Default: -90.0.
    :param theta_end: The theta end. Default: 90.0.
    """

    def __init__(self, name='I13PtychoLoader'):
        super(I13PtychoLoader, self).__init__(name)

    def setup(self):
        """
         Define the input nexus file
        :param path: The full path of the NeXus file to load.
        :type path: str
        """

        exp = self.exp
        data_obj = exp.create_data_object("in_data", 'ptycho')
        data_obj.backing_file = \
            h5py.File(exp.meta_data.get("data_file"), 'r')
        logging.debug("Creating file '%s' '%s'_entry",
                      data_obj.backing_file.filename, 'ptycho')

        data_obj.data = data_obj.backing_file['entry1/instrument/merlin_sw_hdf/data']
        #        print data_obj.data.shape
        data_obj.set_shape(data_obj.data.shape)
        try:
            control = data_obj.backing_file['/entry1/instrument/ionc_i/ionc_i'][()]
        # this is global since it is to do with the beam
            exp.meta_data.set("control", control)
            logging.debug('adding the ion chamber to the meta data')
        except:
            logging.warning('No ion chamber information. Leaving this blank')

        self.exp.meta_data.set("mono_energy", self.parameters['mono_energy'])

        labels = []
        ### set the rotation
        rotation_angle = None
        if self.parameters['is_tomo']:
            rotation_angle = np.arange(self.parameters['theta_start'],self.parameters['theta_end'], self.parameters['theta_step'])
            labels.append('rotation_angle.degrees')
            data_obj.meta_data.set('rotation_angle', rotation_angle)

#             try:
#                 rotation_angle = data_obj.backing_file['entry1/instrument/t1_theta/t1_theta'][()]
#                 if rotation_angle.ndim > 1:
#                     rotation_angle = rotation_angle[:, 0]
#                 # axis label
#                 labels.append('rotation_angle.degrees')
#
#                 data_obj.meta_data.set('rotation_angle', rotation_angle)
#             except KeyError:
#                 logging.debug("Not a tomography!")

        ### GET THE AXES ###
        x = data_obj.backing_file['entry1/instrument/lab_sxy/lab_sx'][()]*1e-6
        data_obj.meta_data.set('x', x)
        y = data_obj.backing_file['entry1/instrument/lab_sxy/lab_sy'][()]*1e-6
        data_obj.meta_data.set('y', y)
        if rotation_angle is not None and len(x.shape)>1:
            pos = np.zeros((x.shape[0],2,x.shape[1]))
            pos[:,0,:] = y
            pos[:,1,:] = x
        else:
            pos = np.zeros((2,len(y)))
            pos[0,:] = y
            pos[1,:] = x
        data_obj.meta_data.set('xy', pos)
        ######

        ### NOW DO THE LABELS
        labels.append('xy.metres')

        labels.extend(['detectorX.pixel','detectorY.pixel'])
        logging.debug('The labels are: %s',labels)

        data_obj.set_axis_labels(*tuple(labels))
        dims = list(range(len(data_obj.get_shape())))
        diff_core = (-2,-1) # it will always be this
        diff_slice = tuple(dims[:-2])
        logging.debug("is a diffraction")
        logging.debug("the diffraction cores are:"+str(diff_core))
        logging.debug("the diffraction slices are:"+str(diff_slice))
        positions_label = (data_obj.get_data_dimension_by_axis_label('xy', contains=True),)
        rotation_label=[]
        if self.parameters['is_tomo']:
            rotation_label = (data_obj.get_data_dimension_by_axis_label('rotation_angle', contains=True),)
            sino_cores = rotation_label + positions_label
            data_obj.add_pattern("SINOGRAM", core_dims=sino_cores, slice_dims=tuple(set(dims)-set(sino_cores)))

        data_obj.add_pattern("PROJECTION", core_dims=positions_label, slice_dims=tuple(set(dims)-set(positions_label)))



        data_obj.add_pattern("DIFFRACTION", core_dims=diff_core,
                             slice_dims=diff_slice)

        data_obj.add_pattern("4D_SCAN", core_dims=tuple(set(dims)-set(rotation_label)),
                        slice_dims=rotation_label)

        self.set_data_reduction_params(data_obj)
