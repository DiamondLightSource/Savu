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
.. module:: process
   :platform: Unix
   :synopsis: Methods for running a chain of plugins

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""

import os

import savu.plugins.utils as pu


def run_plugin_chain(input_data, plugin_list, processing_dir, mpi=False):
    """Runs a chain of plugins

    :param input_data: The input data to give to the chain
    :type input_data: savu.data.structure.
    :param plugin_list: Names of all the plugins to process in order.
    :type plugin_list: list of str.
    :param processing_dir: Location of the processing directory.
    :type processing_dir: str.
    :param mpi: Whether this is running in mpi, default is false.
    :type mpi: bool.
    """
    in_data = input_data
    output = None
    count = 0
    for plugin_name in plugin_list:
        plugin = pu.load_plugin(None, plugin_name)

        # generate somewhere for the data to go
        file_name = os.path.join(processing_dir,
                                 "%02i%s" % (count, plugin_name))
        output = pu.create_output_data(plugin, in_data, file_name, mpi)

        plugin.set_parameters(None)

        plugin.process(in_data, output, 1, 0)

        in_data.complete()
        in_data = output

        count += 1

    if output is not None:
        output.complete()
