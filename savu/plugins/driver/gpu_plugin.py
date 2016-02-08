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
.. module:: gpu_plugin
   :platform: Unix
   :synopsis: Base class for all plugins which use a GPU on the target machine

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""
import logging
import copy
import numpy as np
from mpi4py import MPI

from savu.plugins.driver.plugin_driver import PluginDriver


class GpuPlugin(PluginDriver):
    """
    The base class from which all plugins should inherit.
    """

    def __init__(self):
        super(GpuPlugin, self).__init__()

    def run_plugin(self, exp, transport):

        expInfo = exp.meta_data
        processes = copy.copy(expInfo.get_meta_data("processes"))
        process = expInfo.get_meta_data("process")

        gpu_processes = [False]*len(processes)
        idx = [i for i in range(len(processes)) if 'GPU' in processes[i]]
        for i in idx:
            gpu_processes[i] = True

        # set only GPU processes
        new_processes = [i for i in processes if 'GPU' in i]
        if not new_processes:
            raise Exception("THERE ARE NO GPU PROCESSES!")
        expInfo.set_meta_data('processes', new_processes)

        nNodes = new_processes.count(new_processes[0])

        ranks = [i for i, x in enumerate(gpu_processes) if x]
        self.create_new_communicator(ranks, exp, process)

        if gpu_processes[process]:
            expInfo.set_meta_data('process', self.new_comm.Get_rank())
            logging.info("Running the GPU Process %i",
                         self.new_comm.Get_rank())
            GPU_index = self.calculate_GPU_index(nNodes)
            self.parameters['GPU_index'] = GPU_index
            self.run_plugin_instances(transport, communicator=self.new_comm)
            self.clean_up()
            self.free_communicator()
            expInfo.set_meta_data('process', MPI.COMM_WORLD.Get_rank())

        self.exp.barrier()
        expInfo.set_meta_data('processes', processes)
        return

    def create_new_communicator(self, ranks, exp, process):
        self.group = MPI.COMM_WORLD.Get_group()
        self.new_group = MPI.Group.Incl(self.group, ranks)
        self.new_comm = MPI.COMM_WORLD.Create(self.new_group)
        self.exp.barrier()

    def free_communicator(self):
        self.group.Free()
        self.new_group.Free()
        self.new_comm.Free()

    def calculate_GPU_index(self, nNodes):
        rank = self.new_comm.Get_rank()
        return int(rank/nNodes)
