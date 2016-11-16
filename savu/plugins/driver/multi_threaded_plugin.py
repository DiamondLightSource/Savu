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

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""
import logging
from mpi4py import MPI

from savu.plugins.driver.plugin_driver import PluginDriver


class MultiThreadedPlugin(PluginDriver):
    """
    The base class from which all plugins should inherit.
    """

    def __init__(self):
        super(MultiThreadedPlugin, self).__init__()

    def _run_plugin(self, exp, transport):
        process = exp.meta_data.get_meta_data("process")
        processes = exp.meta_data.get_meta_data("processes")
        nNodes = processes.count(processes[0])
        nCores = len(processes)/nNodes
        masters = [p for p in range(len(processes)) if p % nCores is 0]
        self.__create_new_communicator(masters, exp)

        print "*****available cores", nCores, masters
        if process in masters:
            logging.info("Running a multi-threaded process")
            self.parameters['available_CPUs'] = nCores
            self.parameters['available_GPUs'] = \
                len([p for p in processes if 'GPU' in p])/nNodes
            self._run_plugin_instances(transport, communicator=self.new_comm)
            self.__free_communicator()

        self.exp._barrier()
        return

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
