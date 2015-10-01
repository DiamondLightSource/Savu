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

""" Methods for running a chain of plugins

.. module:: process
   :platform: Unix
   :synopsis: Methods for running a chain of plugins

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""

import os
import logging
import time

from mpi4py import MPI

import savu.plugins.utils as pu
from savu.core.utils import logfunction


def run_plugin_chain(input_data, plugin_list, processing_dir, mpi=False,
                     processes=["CPU0"], process=0):
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
    logging.debug("Starting run_plugin_chain")
    in_data = input_data
    output = None
    count = 0
    for plugin_name in plugin_list:
        logging.debug("Loading plugin %s", plugin_name)
        plugin = pu.load_plugin(plugin_name)

        # generate somewhere for the data to go
        file_name = os.path.join(processing_dir,
                                 "%02i_%s.h5" % (count, plugin.name))
        logging.debug("Creating output file : %s", file_name)
        output = pu.create_output_data(plugin, in_data, file_name, plugin.name,
                                       mpi)

        plugin.set_parameters(None)

        logging.debug("Starting processing  plugin %s", plugin_name)
        plugin.run_plugin(in_data, output, processes, process)
        logging.debug("Completed processing plugin %s", plugin_name)

        if in_data is not output:
            in_data.complete()
        in_data = output

        if mpi:
            logging.debug("MPI awaiting barrier")
            MPI.COMM_WORLD.barrier()

        count += 1

    if output is not None:
        output.complete()


@logfunction
def run_plugin_list(input_data, plugin_list, processing_dir, mpi=False,
                    processes=["CPU0"], process=0):
    """Runs a chain of plugins

    :param input_data: The input data to give to the chain
    :type input_data: savu.data.structure.
    :param plugin_list: Plugin list.
    :type plugin_list: savu.data.structure.PluginList.
    :param processing_dir: Location of the processing directory.
    :type processing_dir: str.
    :param mpi: Whether this is running in mpi, default is false.
    :type mpi: bool.
    """
    logging.debug("Running plugin list, just a check")
    filename = os.path.basename(input_data.backing_file.filename)
    filename = os.path.splitext(filename)[0]
    output_filename = \
        os.path.join(processing_dir,
                     "%s_processed_%s.nxs" % (filename,
                                              time.strftime("%Y%m%d%H%M%S")))
    if process == 0:
        logging.debug("Running process List.save_list_to_file")
        plugin_list.save_list_to_file(output_filename)

    in_data = input_data
    output = None

    logging.debug("generating all output files")
    files = []
    count = 0
    for plugin_dict in plugin_list.plugin_list:
        logging.debug("Loading plugin %s", plugin_dict['id'])
        plugin = pu.load_plugin(plugin_dict['id'])

        # generate somewhere for the data to go
        file_name = os.path.join(processing_dir,
                                 "%s%02i_%s.h5" % (plugin_list.name, count,
                                                   plugin_dict['id']))
        group_name = "%i-%s" % (count, plugin.name)
        logging.debug("Creating output file %s", file_name)
        output = pu.create_output_data(plugin, in_data, file_name, group_name,
                                       mpi)

        files.append(output)

        in_data = output
        count += 1

    logging.debug("processing Plugins")

    in_data = input_data
    count = 0
    for plugin_dict in plugin_list.plugin_list:
        logging.debug("Loading plugin %s", plugin_dict['id'])
        plugin = pu.load_plugin(plugin_dict['id'])

        output = files[count]

        plugin.set_parameters(plugin_dict['data'])

        logging.debug("Starting processing  plugin %s", plugin_dict['id'])
        plugin.run_plugin(in_data, output, processes, process)
        logging.debug("Completed processing plugin %s", plugin_dict['id'])

        if in_data is not output:
            in_data.complete()
        in_data = output

        if mpi:
            logging.debug("Blocking till all processes complete")
            MPI.COMM_WORLD.Barrier()

        if plugin == 0:
            cite_info = plugin.get_citation_information()
            if cite_info is not None:
                plugin_list.add_plugin_citation(output_filename, count,
                                                cite_info)
            group_name = "%i-%s" % (count, plugin.name)
            plugin_list.add_intermediate_data_link(output_filename,
                                                   output, group_name)

        count += 1

    if output is not None:
        output.complete()
