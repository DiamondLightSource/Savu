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
.. module:: multi_threaded_plugin
   :platform: Unix
   :synopsis: Driver to run one instance of a plugin on EACH node.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""
from mpi4py import MPI

from savu.plugins.driver.plugin_driver import PluginDriver


class MultiThreadedPlugin(PluginDriver):

    def __init__(self):
        super(MultiThreadedPlugin, self).__init__()

    def get_mem_multiply(self):
        self.processes = self.exp.meta_data.get("processes")
        self.nNodes = self.processes.count(self.processes[0])
        return len(self.processes)/self.nNodes

    def _run_plugin(self, exp, transport):
        process = exp.meta_data.get("process")
        nCores = len(self.processes) // self.nNodes
        masters = self._get_masters(self.processes)

        self.__create_new_communicator(masters, exp)
        self.exp._barrier()

        if process in masters:
            self.parameters['available_CPUs'] = nCores
            self.parameters['available_GPUs'] = len([p for p in self.processes if 'GPU' in p]) // self.nNodes
            self._run_plugin_instances(transport, communicator=self.new_comm)
            self.__free_communicator()

        self.exp._barrier()
        return

    def _get_masters(self, processes):
        masters = [p for p in range(len(processes)) if processes[p] == 'GPU0']
        if not masters:
            masters = \
                [p for p in range(len(processes)) if processes[p] == 'CPU0']
        return masters

    def __create_new_communicator(self, ranks, exp):
        self.group = MPI.COMM_WORLD.Get_group()
        self.new_group = MPI.Group.Incl(self.group, ranks)
        self.new_comm = MPI.COMM_WORLD.Create(self.new_group)
        self.exp._barrier()

    def __free_communicator(self):
        self.group.Free()
        self.new_group.Free()
        self.new_comm.Free()

    def min_max_cpus(self):
        """ Sets the bounds on the number of CPUs required by the plugin, such
        that if bounds=[b1, b2] then b1 is the lower bound and b2 is the upper
        bound.  Set each entry to None if there are no bounds.
        """
        return [None, None]

    def min_max_gpus(self):
        """ Sets the bounds on the number of GPUs required by the plugin, such
        that if bounds=[b1, b2] then b1 is the lower bound and b2 is the upper
        bound.  Set each entry to None if there are no bounds and to 0 if no
        GPUs are required.
        """
        return [0, 0]
