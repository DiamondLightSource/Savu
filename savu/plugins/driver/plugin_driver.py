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

import savu.plugins.utils as pu


class PluginDriver(object):
    """
    The base class from which all plugins should inherit.
    """

    def __init__(self):
        super(PluginDriver, self).__init__()

    def _run_plugin_instances(self, transport, communicator=MPI.COMM_WORLD):
        out_data = self.get_out_datasets()
        extra_dims = self.extra_dims
        repeat = np.prod(extra_dims) if extra_dims else 1

        param_idx = pu.calc_param_indices(extra_dims)
        out_data_dims = [len(d.get_shape()) for d in out_data]
        param_dims = [range(d - len(extra_dims), d) for d in out_data_dims]

        for i in range(repeat):
            if repeat > 1:
                self._set_parameters_this_instance(param_idx[i])
                for j in range(len(out_data)):
                    out_data[j]._get_plugin_data()\
                        .set_fixed_directions(param_dims[j], param_idx[i])

            logging.info("%s.%s", self.__class__.__name__, 'pre_process')
            self.pre_process()

            logging.info("%s.%s", self.__class__.__name__, 'process')
            transport._process(self)

            logging.info("%s.%s", self.__class__.__name__, '_barrier')
            self.exp._barrier(communicator=communicator)

            logging.info("%s.%s", self.__class__.__name__, 'post_process')
            self.post_process()

        for j in range(len(out_data)):
            out_data[j].set_shape(out_data[j].data.shape)
