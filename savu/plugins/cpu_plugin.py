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
from savu.plugins.plugin import Plugin


class CpuPlugin(Plugin):
    """
    The base class from which all plugins should inherit.
    """

    def __init__(self, name='Cpu_Plugin'):
        super(CpuPlugin, self).__init__(name)

    def run_process(self, data, output, processes, process):
        count = 0
        cpu_processes = []
        for i in ["CPU" in i for i in processes]:
            if i:
                cpu_processes.append(count)
                count += 1
            else:
                cpu_processes.append(-1)
        if cpu_processes[process] >= 0:
            return self.process(data, output,
                                [i for i in processes if "CPU" in i],
                                cpu_processes[process])
        return
