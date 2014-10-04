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

from savu.plugins.plugin import Plugin


class GpuPlugin(Plugin):
    """
    The base class from which all plugins should inherit.
    """

    def __init__(self, name='Gpu_Plugin'):
        super(GpuPlugin, self).__init__(name)

    def run_process(self, data, output, processes, process):
        count = 0
        gpu_processes = []
        gpu_list = ["GPU" in i for i in processes]
        for i in gpu_list:
            if i:
                gpu_processes.append(count)
                count += 1
            else:
                gpu_processes.append(-1)
        if gpu_processes[process] >= 0:
            logging.debug("Running the GPU Process %i", process)
            new_processes = [i for i in processes if "GPU" in i]
            logging.debug(new_processes)
            logging.debug(gpu_processes)
            logging.debug("Process is %s",
                          new_processes[gpu_processes[process]])
            return self.process(data, output, new_processes,
                                gpu_processes[process])
        logging.debug("Not Running the task as not GPU")
        return
