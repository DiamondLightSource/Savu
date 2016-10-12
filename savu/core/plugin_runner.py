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
        plugin_list = self.exp.meta_data.plugin_list

        self.exp._barrier()
        self._run_plugin_list_check(plugin_list)

        self.exp._barrier()
        expInfo = self.exp.meta_data
        logging.debug("Running process List.save_list_to_file")
        expInfo.plugin_list._save_plugin_list(
            expInfo.get_meta_data("nxs_filename"), exp=self.exp)

        self.exp._barrier()
        self._transport_run_plugin_list()

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
        plugin_list._check_loaders_and_savers()
        self.__check_gpu()

        self.exp._barrier()
        self.__fake_plugin_list_run(plugin_list.plugin_list, check=True)

        self.exp._barrier()
        self.exp._clear_data_objects()

        self.exp._barrier()
        cu.user_message("Plugin list check complete!")

    def __fake_plugin_list_run(self, plugin_list, **kwargs):
        """ Run through the plugin list without any processing (setup only)\
        and fill in missing dataset names.
        """
        n_loaders = self.exp.meta_data.plugin_list._get_n_loaders()

        for i in range(n_loaders):
            pu.plugin_loader(self.exp, plugin_list[i])

        self.exp._set_nxs_filename()

        check = kwargs.get('check', False)
        for i in range(n_loaders, len(plugin_list)-1):
            self.exp._barrier()
            plugin = pu.plugin_loader(self.exp, plugin_list[i], check=check)
            plugin_list[i]['cite'] = plugin.get_citation_information()
            plugin._clean_up()
            self.exp._merge_out_data_to_in()

    def __check_gpu(self):
        """ Check if the process list contains GPU processes and determine if
        GPUs exists. Add GPU processes to the processes list if required."""
        if not self.exp.meta_data.plugin_list._contains_gpu_processes():
            return
        try:
            import pynvml as pv
        except:
            logging.debug("pyNVML module not found")
            raise Exception("pyNVML module not found")
        try:
            pv.nvmlInit()
            count = int(pv.nvmlDeviceGetCount())
            logging.debug("%s GPUs have been found.", count)
            for i in range(count):
                handle = pv.nvmlDeviceGetHandleByIndex(i)
                if pv.nvmlDeviceGetComputeRunningProcesses(handle):
                    raise Exception("Unfortunately, GPU %i is busy. Try \
                        resubmitting the job to the queue." % i)
        except:
            logging.debug("No GPUs have been found.")
            raise Exception("The process list contains GPU plugins, but "
                            " no GPUs have been found.")
        self.__set_gpu_processes(count)

    def __set_gpu_processes(self, count):
        processes = self.exp.meta_data.get_meta_data('processes')
        if not [i for i in processes if 'GPU' in i]:
            logging.debug("GPU processes missing. GPUs found so adding them.")
            cpus = ['CPU'+str(i) for i in range(count)]
            gpus = ['GPU'+str(i) for i in range(count)]
            for i in range(min(count, len(processes))):
                processes[processes.index(cpus[i])] = gpus[i]
            self.exp.meta_data.set_meta_data('processes', processes)
