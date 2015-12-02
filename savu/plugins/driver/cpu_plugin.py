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
.. module:: cpu_plugin
   :platform: Unix
   :synopsis: Base class for all plugins which use a CPU on the target machine

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""
import logging
import numpy as np

import savu.plugins.utils as pu


class CpuPlugin(object):
    """
    The base class from which all plugins should inherit.
    """

    def __init__(self):
        super(CpuPlugin, self).__init__()

    def run_plugin(self, exp, transport):

        expInfo = exp.meta_data
        processes = expInfo.get_meta_data("processes")
        process = expInfo.get_meta_data("process")

        count = 0
        cpu_processes = []
        for i in ["CPU" in i for i in processes]:
            if i:
                cpu_processes.append(count)
                count += 1
            else:
                cpu_processes.append(-1)
        if cpu_processes[process] >= 0:
            logging.debug("Running the CPU Process %i", process)
            # new_processes = [i for i in processes if "CPU" in i]

            logging.debug("Pre-processing")

        self.run_plugin_instances(transport)
        self.clean_up()

        logging.debug("Not Running the task as not CPU")
        return

    def run_plugin_instances(self, transport):
        out_data = self.get_out_datasets()
        extra_dims = self.extra_dims
        repeat = np.prod(extra_dims) if extra_dims else 1

        param_idx = pu.calc_param_indices(extra_dims)
        out_data_dims = [len(d.get_shape()) for d in out_data]
        param_dims = [range(d - len(extra_dims), d) for d in out_data_dims]
        for i in range(repeat):
            if repeat > 1:
                self.set_parameters_this_instance(param_idx[i])
                for j in range(len(out_data)):
                    out_data[j].get_plugin_data()\
                        .set_fixed_directions(param_dims[j], param_idx[i])

            logging.info("%s.%s", self.__module__, 'pre_process')
            self.pre_process()

            logging.info("%s.%s", self.__module__, 'process')
            transport.process(self)

            logging.info("%s.%s", self.__module__, 'barrier')
            self.exp.barrier()

            logging.info("%s.%s", self.__module__, 'post_process')
            self.post_process()

            logging.info("%s.%s", self.__module__, 'barrier')

    def process(self, data, output, processes, process):
        """
        This method is called after the process has been created by the
        pipeline framework

        :param data: The input data object.
        :type data: savu.data.data_structures
        :param data: The output data object
        :type data: savu.data.data_structures
        :param processes: The number of processes which will be doing the work
        :type path: int
        :param path: The specific process which we are
        :type path: int
        """
        logging.error("process needs to be implemented for proc %i of %i :" +
                      " input is %s and output is %s",
                      process, processes, data.__class__, output.__class__)
        raise NotImplementedError("process needs to be implemented")
