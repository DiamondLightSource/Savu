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

        count = 0
        gpu_processes = []
        for i in ["GPU" in i for i in processes]:
            if i:
                gpu_processes.append(count)
                count += 1
            else:
                gpu_processes.append(-1)

        # set only GPU processes
        new_processes = [i for i in processes if 'GPU' in i]
        expInfo.set_meta_data('processes', new_processes)

        if not new_processes:
            raise Exception("THERE ARE NO GPU PROCESSES!")

        if gpu_processes[process] >= 0:
            logging.debug("Running the GPU Process %i", process)
            logging.debug("Pre-processing")
            self.run_plugin_instances(transport)
            self.clean_up()

        self.exp.barrier()
        expInfo.set_meta_data('processes', processes)
        return
        