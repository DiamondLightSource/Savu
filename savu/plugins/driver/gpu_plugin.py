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
   :synopsis: The driver for GPU plugins.

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""

import os
import copy
import logging
import numpy as np
import pynvml as pv
from mpi4py import MPI
from itertools import chain

from savu.plugins.driver.plugin_driver import PluginDriver
from savu.plugins.driver.basic_driver import BasicDriver

_base = BasicDriver if os.environ['savu_mode'] == 'basic' else PluginDriver


class GpuPlugin(_base):

    def __init__(self):
        super(GpuPlugin, self).__init__()

    def _run_plugin(self, exp, transport):
        expInfo = exp.meta_data
        processes = copy.copy(expInfo.get("processes"))
        process = expInfo.get("process")

        gpu_processes = [False] * len(processes)
        idx = [i for i in range(len(processes)) if 'GPU' in processes[i]]
        for i in idx:
            gpu_processes[i] = True

        # set only GPU processes
        new_processes = [i for i in processes if 'GPU' in i]
        if not new_processes:
            raise Exception("THERE ARE NO GPU PROCESSES!")
        expInfo.set('processes', new_processes)

        nNodes = new_processes.count(new_processes[0])

        ranks = [i for i, x in enumerate(gpu_processes) if x]
        idx = [i for i in range(len(ranks)) if new_processes[i] == 'GPU0']
        diff = np.diff(np.array(idx)) if len(idx) > 1 else 1
        split = np.max(diff) if not isinstance(diff, int) else len(ranks)
        split_ranks = [ranks[n:n + split] for n in range(0, len(ranks), split)]
        ranks = list(chain.from_iterable(zip(*split_ranks)))

        self.__create_new_communicator(ranks, exp, process)

        if gpu_processes[process]:
            self.stats_obj.GPU = True
            expInfo.set('process', self.new_comm.Get_rank())
            GPU_index = self.__calculate_GPU_index(nNodes)
            logging.debug("Running the GPU process %i with GPU index %i",
                          self.new_comm.Get_rank(), GPU_index)
            self.parameters['GPU_index'] = GPU_index
            os.environ['CUDA_DEVICE'] = str(GPU_index)
            self._run_plugin_instances(transport, communicator=self.new_comm)
            self.__free_communicator()
            expInfo.set('process', MPI.COMM_WORLD.Get_rank())
        else:
            logging.info('Not a GPU process: Waiting...')

        self.exp._barrier()
        expInfo.set('processes', processes)
        return

    def __create_new_communicator(self, ranks, exp, process):
        self.group = MPI.COMM_WORLD.Get_group()
        self.new_group = MPI.Group.Incl(self.group, ranks)
        self.new_comm = MPI.COMM_WORLD.Create(self.new_group)
        self.exp._barrier()

    def __free_communicator(self):
        self.group.Free()
        self.new_group.Free()
        self.new_comm.Free()

    def __calculate_GPU_index(self, nNodes):
        pv.nvmlInit()
        nGPUs = int(pv.nvmlDeviceGetCount())
        rank = self.new_comm.Get_rank()
        return int(rank / nNodes) % nGPUs
