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
.. module:: plugin_driver
   :platform: Unix
   :synopsis: Base class or all driver plugins

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""
import logging
import numpy as np
from mpi4py import MPI

from savu.plugins.driver.basic_driver import BasicDriver


class PluginDriver(BasicDriver):
    """
    The base class from which all plugins should inherit.
    """

    def __init__(self):
        super(PluginDriver, self).__init__()
        self._communicator = None

    def _run_plugin_instances(self, transport, communicator=MPI.COMM_WORLD):
        """ Runs the pre_process, process and post_process methods.

        If parameter tuning is required, loop over the methods and set the
        correct parameters for each run. """

        self.__set_communicator(communicator)
        out_data = self.get_out_datasets()
        extra_dims = self.get_plugin_tools().extra_dims
        repeat = np.prod(extra_dims) if extra_dims else 1

        param_idx = self.__calc_param_indices(extra_dims)
        out_data_dims = [len(d.get_shape()) for d in out_data]
        param_dims = [list(range(d - len(extra_dims), d)) for d in out_data_dims]

        if extra_dims:
            init_vars = self.__get_local_dict()

        for i in range(repeat):
            if extra_dims:
                self.__reset_local_vars(init_vars)
                self.get_plugin_tools()._set_parameters_this_instance(
                    param_idx[i])
                for j in range(len(out_data)):
                    out_data[j]._get_plugin_data()\
                        .set_fixed_dimensions(param_dims[j], param_idx[i])

            super(PluginDriver, self).\
                _run_plugin_instances(transport, communicator=communicator)
            self._reset_process_frames_counter()

        self._revert_preview(self.parameters['in_datasets'])

        for j in range(len(out_data)):
            out_data[j].set_shape(out_data[j].data.shape)

    def __get_local_dict(self):
        """ Gets the local variables of the class minus those from the Plugin
        class. """
        from savu.plugins.plugin import Plugin
        plugin = Plugin()
        copy_keys = vars(self).keys() - vars(plugin).keys()
        copy_dict = {}
        for key in copy_keys:
            copy_dict[key] = getattr(self, key)
        return copy_dict

    def __reset_local_vars(self, copy_dict):
        """ Resets the class variables in copy_dict. """
        for key, value in copy_dict.items():
            setattr(self, key, value)

    def __calc_param_indices(self, dims):
        indices_list = []
        for i in range(len(dims)):
            chunk = int(np.prod(dims[0:i]))
            repeat = int(np.prod(dims[i+1:]))
            idx = np.ravel(np.kron(list(range(dims[i])), np.ones((repeat, chunk))))
            indices_list.append(idx.astype(int))
        return np.transpose(np.array(indices_list))

    def __set_communicator(self, comm):
        self._communicator = comm

    def get_communicator(self):
        return self._communicator
