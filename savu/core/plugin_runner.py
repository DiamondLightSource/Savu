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
   :synopsis: Plugin list runner, which passes control to the transport layer.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import logging

import savu.core.utils as cu
import savu.plugins.utils as pu
from savu.data.experiment_collection import Experiment


class PluginRunner(object):
    """ Plugin list runner, which passes control to the transport layer.
    """

    def __init__(self, options):
        class_name = "savu.core.transports." + options["transport"] \
                     + "_transport"
        cu.add_base(self, cu.import_class(class_name))
        self._transport_control_setup(options)
        self.exp = None
        self.options = options
        # add all relevent locations to the path
        pu.get_plugins_paths()

    def _run_plugin_list(self):
        """ Create an experiment and run the plugin list.
        """
        self.exp = Experiment(self.options)
        plugin_list = self.exp.meta_data.plugin_list.plugin_list

        logging.info("run_plugin_list: 1")
        self.exp._barrier()
        self._run_plugin_list_check(plugin_list)

        logging.info("run_plugin_list: 2")
        self.exp._barrier()
        expInfo = self.exp.meta_data
        logging.debug("Running process List.save_list_to_file")
        expInfo.plugin_list._save_plugin_list(
            expInfo.get_meta_data("nxs_filename"), exp=self.exp)

        logging.info("run_plugin_list: 3")
        self.exp._barrier()
        self._transport_run_plugin_list()

        logging.info("run_plugin_list: 4")
        self.exp._barrier()

        cu.user_message("***********************")
        cu.user_message("* Processing Complete *")
        cu.user_message("***********************")

        self.exp.nxs_file.close()
        return self.exp

    def _run_plugin_list_check(self, plugin_list):
        """ Run the plugin list through the framework without executing the
        main processing.
        """
        self.exp._barrier()
        self.__check_loaders_and_savers()
        self.__check_gpu()

        self.exp._barrier()
        pu.run_plugins(self.exp, plugin_list, check=True)

        self.exp._barrier()
        self.exp._clear_data_objects()

        self.exp._barrier()
        cu.user_message("Plugin list check complete!")

    def __check_loaders_and_savers(self):
        """ Check plugin list starts with a loader and ends with a saver.
        """
        plugin_obj = self.exp.meta_data.plugin_list
        loaders, savers = plugin_obj._get_loaders_and_savers_index()

        if loaders:
            if loaders[0] is not 0 or loaders[-1]+1 is not len(loaders):
                raise Exception("All loader plugins must be at the beginning "
                                "of the plugin list")
        else:
            raise Exception("The first plugin in the plugin list must be a "
                            "loader.")

        if not savers or savers[0] is not plugin_obj.n_plugins-1:
            raise Exception("The final plugin in the plugin list must be a "
                            "saver")

    def __check_gpu(self):
        """ Check if the process list contains GPU processes and determine if
        GPUs exists. Add GPU processes to the processes list if required."""
        import pynvml as pv
        if not self.exp.meta_data.plugin_list._contains_gpu_processes():
            return
        try:
            pv.nvmlInit()
            count = int(pv.nvmlDeviceGetCount())
            logging.debug("%s GPUs have been found.", count)
        except:
            logging.debug("No GPUs have been found.")
            raise Exception("The process list contains GPU plugins, but "
                            " no GPUs have been found.")

        processes = self.exp.meta_data.get_meta_data('processes')
        if not [i for i in processes if 'GPU' in i]:
            logging.debug("GPU processes missing. GPUs found so adding them.")
            cpus = ['CPU'+str(i) for i in range(count)]
            gpus = ['GPU'+str(i) for i in range(count)]
            for i in range(min(count, len(processes))):
                processes[processes.index(cpus[i])] = gpus[i]
            self.exp.meta_data.set_meta_data('processes', processes)
