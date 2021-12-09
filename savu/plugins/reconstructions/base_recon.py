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
.. module:: base_recon
   :platform: Unix
   :synopsis: A base class for all reconstruction methods

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""

import math
import copy
import numpy as np
import subprocess as sp
import os
np.seterr(divide='ignore', invalid='ignore')

import savu.core.utils as cu
from savu.plugins.plugin import Plugin

MAX_OUTER_PAD = 2.1


class BaseRecon(Plugin):


    def __init__(self, name='BaseRecon'):
        super(BaseRecon, self).__init__(name)
        self.nOut = 1
        self.nIn = 1
        self.scan_dim = None
        self.rep_dim = None
        self.br_vol_shape = None
        self.frame_angles = None
        self.frame_cors = None
        self.frame_init_data = None
        self.centre = None
        self.base_pad_amount = None
        self.padding_alg = False
        self.cor_shift = 0
        self.init_vol = False
        self.cor_as_dataset = False

    def base_pre_process(self):
        in_data, out_data = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()
        self.pad_dim = \
            in_pData[0].get_data_dimension_by_axis_label('x', contains=True)
        in_meta_data = self.get_in_meta_data()[0]

        self.exp.log(self.name + " End")
        self.br_vol_shape = out_pData[0].get_shape()
        self.set_centre_of_rotation(in_data[0], out_data[0], in_meta_data)

        self.main_dir = in_data[0].get_data_patterns()['SINOGRAM']['main_dir']
        self.angles = in_meta_data.get('rotation_angle')

        if len(self.angles.shape) != 1:
            self.scan_dim = in_data[0].get_data_dimension_by_axis_label('scan')
        self.slice_dirs = out_data[0].get_slice_dimensions()

        shape = in_pData[0].get_shape()
        factor = self.__get_outer_pad()
        self.sino_pad = int(math.ceil(factor * shape[self.pad_dim]))

        self.sino_func, self.cor_func = self.set_function(shape)

        self.range = self.parameters['force_zero']
        self.fix_sino = self.get_sino_centre_method()

    def __get_outer_pad(self):
        pad = self.parameters['outer_pad'] if 'outer_pad' in self.parameters \
            else False
        # length of diagonal of square is side*sqrt(2)
        factor = math.sqrt(2) - 1
        if isinstance(pad, bool):
            return factor if pad is True else 0

        factor = float(pad)
        if factor > MAX_OUTER_PAD:
            factor = MAX_OUTER_PAD
            msg = 'Maximum outer_pad value is 2.1, using this instead'
            cu.user_message(msg)
        return factor

    def get_vol_shape(self):
        return self.br_vol_shape

    def set_centre_of_rotation(self, inData, outData, mData):
        # if cor has been passed as a dataset then do nothing
        if isinstance(self.parameters['centre_of_rotation'], str):
            return
        if 'centre_of_rotation' in list(mData.get_dictionary().keys()):
            cor = self.__set_param_from_meta_data(mData, inData, 'centre_of_rotation')
        else:
            val = self.parameters['centre_of_rotation']
            if isinstance(val, dict):
                cor = self.__polyfit_cor(val, inData)
            else:
                sdirs = inData.get_slice_dimensions()
                cor = np.ones(np.prod([inData.get_shape()[i] for i in sdirs]))
                # if centre of rotation has not been set then fix it in the
                # centre
                val = val if val != 0 else \
                    (self.get_vol_shape()[self._get_detX_dim()]) / 2.0
                cor *= val
                # mData.set('centre_of_rotation', cor) see Github ticket
        self.cor = cor
        outData.meta_data.set("centre_of_rotation", copy.deepcopy(self.cor))
        self.centre = self.cor[0]

    def populate_metadata_to_output(self, inData, outData, mData, meta_list):
        # writing into the metadata associated with the output (reconstruction)
        for meta_items in meta_list:
            outData.meta_data.set(meta_items, copy.deepcopy(mData.get(meta_items)))

        xDim = inData.get_data_dimension_by_axis_label('x', contains=True)
        det_length = inData.get_shape()[xDim]
        outData.meta_data.set("detector_x_length", copy.deepcopy(det_length))

    def __set_param_from_meta_data(self, mData, inData, meta_string):
        meta_param = mData.get(meta_string)
        sdirs = inData.get_slice_dimensions()
        total_frames = np.prod([inData.get_shape()[i] for i in sdirs])
        if total_frames > len(meta_param):
            meta_param = np.tile(meta_param, total_frames // len(meta_param))
        return meta_param

    def __polyfit_cor(self, cor_dict, inData):
        if 'detector_y' in list(inData.meta_data.get_dictionary().keys()):
            y = inData.meta_data.get('detector_y')
        else:
            yDim = inData.get_data_dimension_by_axis_label('detector_y')
            y = np.arange(inData.get_shape()[yDim])

        z = np.polyfit(list(map(int, list(cor_dict.keys()))), list(cor_dict.values()), 1)
        p = np.poly1d(z)
        cor = p(y)
        return cor

    def set_function(self, pad_shape):
        centre_pad = self.parameters['centre_pad'] if 'centre_pad' in \
            self.parameters else False
        if not centre_pad:
            def cor_func(cor):
                return cor
            if self.parameters['log']:
                sino_func = self.__make_lambda()
            else:
                sino_func = self.__make_lambda(log=False)
        else:
            def cor_func(cor):
                return cor + self.sino_pad
            if self.parameters['log']:
                sino_func = self.__make_lambda(pad=pad_shape)
            else:
                sino_func = self.__make_lambda(pad=pad_shape, log=False)
        return sino_func, cor_func

    def __make_lambda(self, log=True, pad=False):
        log_func = 'np.nan_to_num(sino)' if not log else self.parameters['log_func']
        if pad:
            pad_tuples, mode = self.__get_pad_values(pad)
            log_func = log_func.replace(
                    'sino', 'np.pad(sino, %s, "%s")' % (pad_tuples, mode))
        return eval("lambda sino: " + log_func)

    def __get_pad_values(self, pad_shape):
        mode = 'edge'
        pad_tuples = [(0, 0)] * (len(pad_shape) - 1)
        pad_tuples.insert(self.pad_dim, (self.sino_pad, self.sino_pad))
        pad_tuples = tuple(pad_tuples)
        return pad_tuples, mode

    def base_process_frames_before(self, data):
        """
        Reconstruct a single sinogram with the provided centre of rotation
        """
        sl = self.get_current_slice_list()[0]
        init = data[1] if self.init_vol else None
        angles = \
            self.angles[:, sl[self.scan_dim]] if self.scan_dim else self.angles
        angles = np.squeeze(angles)

        self.frame_angles = angles

        dim_sl = sl[self.main_dir]

        if self.cor_as_dataset:
            self.frame_cors = self.cor_func(data[len(data) - 1])
        else:
            frame_nos = \
                self.get_plugin_in_datasets()[0].get_current_frame_idx()
            a = self.cor[tuple([frame_nos])]
            self.frame_cors = self.cor_func(a)

        # for extra padded frames that make up the numbers
        if not self.frame_cors.shape:
            self.frame_cors = np.array([self.centre])

        len_data = len(np.arange(dim_sl.start, dim_sl.stop, dim_sl.step))

        missing = [self.centre] * (len(self.frame_cors) - len_data)
        self.frame_cors = np.append(self.frame_cors, missing)

        # fix to remove NaNs in the initialised image
        if init is not None:
            init[np.isnan(init)] == 0.0
        self.frame_init_data = init

        data[0] = self.fix_sino(self.sino_func(data[0]), self.frame_cors[0])
        return data

    def base_process_frames_after(self, data):
        lower_range, upper_range = self.range
        data = np.nan_to_num(data)
        if lower_range is not None:
            data[data < lower_range] = 0.0
        if upper_range is not None:
            data[data > upper_range] = 0.0
        return data

    def pad_sino(self, sino, cor):
        """  Pad the sinogram so the centre of rotation is at the centre. """
        detX = self._get_detX_dim()
        pad = self.get_centre_offset(sino, cor, detX)
        self.cor_shift = pad[0]
        pad_tuples = [(0, 0)] * (len(sino.shape) - 1)
        pad_tuples.insert(detX, tuple(pad))
        self.__set_pad_amount(max(pad))
        return np.pad(sino, tuple(pad_tuples), mode='edge')

    def _get_detX_dim(self):
        pData = self.get_plugin_in_datasets()[0]
        return pData.get_data_dimension_by_axis_label('x', contains=True)

    def get_centre_offset(self, sino, cor, detX):
        centre_pad = self.br_array_pad(cor, sino.shape[detX])
        sino_width = sino.shape[detX]
        new_width = sino_width + max(centre_pad)
        sino_pad = int(math.ceil(float(sino_width) / new_width * self.sino_pad) // 2)
        pad = np.array([sino_pad]*2) + centre_pad
        return pad

    def get_centre_shift(self, sino, cor):
        detX = self._get_detX_dim()
        return max(self.get_centre_offset(sino, self.centre, detX))

    def crop_sino(self, sino, cor):
        """  Crop the sinogram so the centre of rotation is at the centre. """
        detX = self._get_detX_dim()
        start, stop = self.br_array_pad(cor, sino.shape[detX])[::-1]
        self.cor_shift = -start
        sl = [slice(None)] * len(sino.shape)
        sl[detX] = slice(start, sino.shape[detX] - stop)
        sino = sino[tuple(sl)]
        self.set_mask(sino.shape)
        return sino

    def br_array_pad(self, ctr, nPixels):
        width = nPixels - 1.0
        alen = ctr
        blen = width - ctr
        mid = (width - 1.0) / 2.0
        shift = round(abs(blen - alen))
        p_low = 0 if (ctr > mid) else shift
        p_high = shift + 0 if (ctr > mid) else 0
        return np.array([int(p_low), int(p_high)])

    def keep_sino(self, sino, cor):
        """ No change to the sinogram """
        return sino

    def get_sino_centre_method(self):
        centre_pad = self.keep_sino
        if 'centre_pad' in list(self.parameters.keys()):
            cpad = self.parameters['centre_pad']
            if not (cpad is True or cpad is False):
                raise Exception('Unknown value for "centre_pad", please choose'
                                ' True or False.')
            centre_pad = self.pad_sino if cpad else self.crop_sino
        return centre_pad

    def __set_pad_amount(self, pad_amount):
        self.base_pad_amount = pad_amount

    def get_pad_amount(self):
        return self.base_pad_amount

    def get_fov_fraction(self, sino, cor):
        """ Get the fraction of the original FOV that can be reconstructed due\
        to offset centre """
        pData = self.get_plugin_in_datasets()[0]
        detX = pData.get_data_dimension_by_axis_label('x', contains=True)
        original_length = sino.shape[detX]
        shift = self.get_centre_shift(sino, cor)
        return (original_length - shift) / float(original_length)

    def get_reconstruction_alg(self):
        return None

    def get_angles(self):
        """ Get the angles associated with the current sinogram(s).

        :returns: Angles of the current frames.
        :rtype: np.ndarray
        """
        return self.frame_angles

    def get_proj_shifts(self):
        """ Get the 2D (X-Y) shifts associated with every projection frame

        :returns: projecton shifts for the current frames.
        :rtype: np.ndarray
        """
        return self.projection_shifts

    def get_cors(self):
        """
        Get the centre of rotations associated with the current sinogram(s).

        :returns: Centre of rotation values for the current frames.
        :rtype: np.ndarray
        """
        return self.frame_cors + self.cor_shift

    def set_mask(self, shape):
        pass

    def get_initial_data(self):
        """
        Get the initial data (if it is exists) associated with the current \
        sinogram(s).

        :returns: The section of the initialisation data associated with the \
            current frames.
        :rtype: np.ndarray or None
        """
        return self.frame_init_data

    def get_frame_params(self):
        params = [self.get_cors(), self.get_angles(), self.get_vol_shape(),
                  self.get_initial_data()]
        return params

    def get_frame_shifts(self):
        return self.get_proj_shifts()

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        # reduce the data as per data_subset parameter
        self.preview_flag = \
            self.set_preview(in_dataset[0], self.parameters['preview'])

        self._set_volume_dimensions(in_dataset[0])
        axis_labels = self._get_axis_labels(in_dataset[0])
        shape = self._get_shape(in_dataset[0])

        # output dataset
        out_dataset[0].create_dataset(axis_labels=axis_labels, shape=shape)
        out_dataset[0].add_volume_patterns(*self._get_volume_dimensions())

        # set information relating to the plugin data
        in_pData, out_pData = self.get_plugin_datasets()

        self.init_vol = 1 if 'init_vol' in list(self.parameters.keys()) and\
            self.parameters['init_vol'] else 0
        self.cor_as_dataset = 1 if isinstance(
            self.parameters['centre_of_rotation'], str) else 0

        for i in range(len(in_dataset) - self.init_vol - self.cor_as_dataset):
            in_pData[i].plugin_data_setup('SINOGRAM', self.get_max_frames(),
                                          slice_axis=self.get_slice_axis())
            idx = 1

        # initial volume dataset
        if self.init_vol:
#            from savu.data.data_structures.data_types import Replicate
#            if self.rep_dim:
#                in_dataset[idx].data = Replicate(
#                    in_dataset[idx], in_dataset[0].get_shape(self.rep_dim))
            in_pData[1].plugin_data_setup('VOLUME_XZ', self.get_max_frames())
            idx += 1

        # cor dataset
        if self.cor_as_dataset:
            self.cor_as_dataset = True
            in_pData[idx].plugin_data_setup('METADATA', self.get_max_frames())

        # set pattern_name and nframes to process for all datasets
        out_pData[0].plugin_data_setup('VOLUME_XZ', self.get_max_frames())

        meta_list = ['rotation_angle']  # metadata list to populate
        in_meta_data = self.get_in_meta_data()[0]

        if 'projection_shifts' in list(self.exp.meta_data.dict.keys()):
            self.projection_shifts = self.exp.meta_data.dict['projection_shifts']
        else:
            self.projection_shifts = np.zeros((in_dataset[0].get_shape()[self.volX], 2))  # initialise a 2d array of projection shifts
            self.exp.meta_data.set('projection_shifts', copy.deepcopy(self.projection_shifts))

        out_dataset[0].meta_data.set("projection_shifts", copy.deepcopy(self.projection_shifts))
        self.populate_metadata_to_output(in_dataset[0], out_dataset[0], in_meta_data, meta_list)

    def _get_axis_labels(self, in_dataset):
        """
        Get the new axis labels for the output dataset - this is now a volume.

        Parameters
        ----------
        in_dataset : :class:`savu.data.data_structures.data.Data`
            The input dataset to the plugin.

        Returns
        -------
        labels : dict
            The axis labels for the dataset that is output from the plugin.

        """
        labels = in_dataset.data_info.get('axis_labels')[0]
        volX, volY, volZ = self._get_volume_dimensions()
        labels = [str(volX) + '.voxel_x.voxels', str(volZ) + '.voxel_z.voxels']
        if volY:
            labels.append(str(volY) + '.voxel_y.voxels')
        labels = {in_dataset: labels}
        return labels

    def _set_volume_dimensions(self, data):
        """
        Map the input dimensions to the output volume dimensions

        Parameters
        ----------
        in_dataset : :class:`savu.data.data_structures.data.Data`
            The input dataset to the plugin.
        """
        data._finalise_patterns()
        self.volX = data.get_data_dimension_by_axis_label("rotation_angle")
        self.volZ = data.get_data_dimension_by_axis_label("x", contains=True)
        self.volY = data.get_data_dimension_by_axis_label(
            "y", contains=True, exists=True)

    def _get_volume_dimensions(self):
        return self.volX, self.volY, self.volZ

    def _get_shape(self, in_dataset):
        shape = list(in_dataset.get_shape())
        volX, volY, volZ = self._get_volume_dimensions()

        if self.parameters['vol_shape'] in ('auto', 'fixed'):
            shape[volX] = shape[volZ]
        else:
            shape[volX] = self.parameters['vol_shape']
            shape[volZ] = self.parameters['vol_shape']

        if 'resolution' in self.parameters.keys():
            shape[volX] = int(shape[volX] // self.parameters['resolution'])
            shape[volZ] = int(shape[volZ] // self.parameters['resolution'])
        return tuple(shape)

    def get_max_frames(self):
        """
        Number of data frames to pass to each instance of process_frames func

        Returns
        -------
        str or int
            "single", "multiple" or integer (only to be used if the number of
                                             frames MUST be fixed.)
        """
        return 'multiple'

    def get_slice_axis(self):
        """
        Fix the fastest changing slice dimension

        Returns
        -------
        str or None
            str should be the axis_label corresponding to the fastest changing
            dimension

        """
        return None

    def nInput_datasets(self):
        nIn = 1
        if 'init_vol' in self.parameters.keys() and \
                self.parameters['init_vol']:
            if len(self.parameters['init_vol'].split('.')) == 3:
                name, temp, self.rep_dim = self.parameters['init_vol']
                self.parameters['init_vol'] = name
            nIn += 1
            self.parameters['in_datasets'].append(self.parameters['init_vol'])
        if isinstance(self.parameters['centre_of_rotation'], str):
            self.parameters['in_datasets'].append(
                self.parameters['centre_of_rotation'])
            nIn += 1
        return nIn

    def nOutput_datasets(self):
        return self.nOut

    def reconstruct_pre_process(self):
        """
        Should be overridden to perform pre-processing in a child class
        """
        pass

    def executive_summary(self):
        summary = []
        if not self.preview_flag:
            summary.append(("WARNING: Ignoring preview parameters as a preview"
                            " has already been applied to the data."))
        if len(summary) > 0:
            return summary
        return ["Nothing to Report"]

    def get_gpu_memory(self):
        command = "nvidia-smi --query-gpu=memory.free --format=csv"
        memory_free_info = sp.check_output(command.split()).decode('ascii').split('\n')[:-1][1:]
        memory_free_values = [int(x.split()[0]) for i, x in enumerate(memory_free_info)]
        return memory_free_values
