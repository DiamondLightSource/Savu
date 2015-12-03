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
.. module:: plugin_runner
   :platform: Unix
   :synopsis: Class to control the plugin and interact with the transport
   layer.  It inherits dynamically from chosen transport type at run time

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""
import logging
import sys

import savu.core.utils as cu
import savu.plugins.utils as pu
from savu.data.experiment_collection import Experiment
from savu.plugins.base_loader import BaseLoader
from savu.plugins.base_saver import BaseSaver


class PluginRunner(object):
    """
    The PluginRunner class controls the plugins and performs the interaction
    between the plugin and transport layers.  It inherits from the chosen
    transport mechanism.
    """

    def __init__(self, options):
        class_name = "savu.core.transports." + options["transport"] \
                     + "_transport"
        cu.add_base(self, cu.import_class(class_name))
        self.transport_control_setup(options)
        self.exp = None

    # TODO : Do we need to have options passed here as it is passed to __init__
    def run_plugin_list(self, options):
        logging.info("Starting to run the plugin list")
        self.exp = Experiment(options)
        plugin_list = self.exp.meta_data.plugin_list.plugin_list

        self.exp.barrier()
        logging.info("Preparing to run the plugin list check")
        self.run_plugin_list_check(plugin_list)

        self.exp.barrier()
        logging.info("Initialising metadata")
        expInfo = self.exp.meta_data
        if expInfo.get_meta_data("process") is 0:
            logging.debug("Running process List.save_list_to_file")
            expInfo.plugin_list.save_plugin_list(
                expInfo.get_meta_data("nxs_filename"))

        self.exp.barrier()
        logging.info("divert to transport process and run process list")
        self.transport_run_plugin_list()

        print "***********************"
        print "* Processing Complete *"
        print "***********************"
        return self.exp

    def run_plugin_list_check(self, plugin_list):
        self.exp.barrier()
        logging.info("Checking loaders and Savers")
        self.check_loaders_and_savers(plugin_list)

        self.exp.barrier()
        logging.info("Running plugins with the check flag")
        pu.run_plugins(self.exp, plugin_list, check=True)

        self.exp.barrier()
        logging.info("empty the data object dictionaries")
        self.exp.clear_data_objects()

        self.exp.barrier()
        logging.info("Plugin list check complete!")
        print "Plugin list check complete!"

    def check_loaders_and_savers(self, plugin_list):
        first_plugin = plugin_list[0]
        end_plugin = plugin_list[-1]

        plugin = pu.load_plugin(first_plugin['id'])
        # check the first plugin is a loader
        if not isinstance(plugin, BaseLoader):
            sys.exit("The first plugin in the process must "
                     "inherit from BaseLoader")

        plugin = pu.load_plugin(end_plugin['id'])
        # check the final plugin is a saver
        if not isinstance(plugin, BaseSaver):
            sys.exit("The final plugin in the process must "
                     "inherit from BaseSaver")
