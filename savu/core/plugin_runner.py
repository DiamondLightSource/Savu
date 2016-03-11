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
   :synopsis: Class to control the plugin and interact with the transport \
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

    # TODO : Do we need to have options passed here as it is passed to sp12778
    def _run_plugin_list(self, options):
        self.exp = Experiment(options)
        plugin_list = self.exp.meta_data.plugin_list.plugin_list

        logging.info("run_plugin_list: 1")
        self.exp.barrier()
        self._run_plugin_list_check(plugin_list)

        logging.info("run_plugin_list: 2")
        self.exp.barrier()
        expInfo = self.exp.meta_data
        logging.debug("Running process List.save_list_to_file")
        expInfo.plugin_list.save_plugin_list(
            expInfo.get_meta_data("nxs_filename"), exp=self.exp)

        logging.info("run_plugin_list: 3")
        self.exp.barrier()
        self.transport_run_plugin_list()

        logging.info("run_plugin_list: 4")
        self.exp.barrier()

        cu.user_message("***********************")
        cu.user_message("* Processing Complete *")
        cu.user_message("***********************")

        self.exp.nxs_file.close()

        return self.exp

    def __run_plugin_list_check(self, plugin_list):
        self.exp.barrier()
        self.check_loaders_and_savers(plugin_list)

        self.exp.barrier()
        pu.run_plugins(self.exp, plugin_list, check=True)

        self.exp.barrier()
        self.exp.clear_data_objects()

        self.exp.barrier()
        cu.user_message("Plugin list check complete!")

    def __check_loaders_and_savers(self, plugin_list):
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
