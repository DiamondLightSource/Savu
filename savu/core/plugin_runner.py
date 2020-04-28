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
import numpy as np

import savu.core.utils as cu
import savu.plugins.utils as pu
from savu.data.experiment_collection import Experiment


class PluginRunner(object):
    """ Plugin list runner, which passes control to the transport layer.
    """

    def __init__(self, options, name='PluginRunner'):
        class_name = "savu.core.transports." + options["transport"] \
                     + "_transport"
        cu.add_base(self, cu.import_class(class_name))
        super(PluginRunner, self).__init__()

        #  ********* transport function ***********
        self._transport_initialise(options)
        self.options = options
        # add all relevent locations to the path
        pu.get_plugins_paths()
        self.exp = Experiment(options)

    def _run_plugin_list(self):
        """ Create an experiment and run the plugin list.
        """
        self.exp._set_nxs_file()

        plugin_list = self.exp.meta_data.plugin_list
        logging.info('Running the plugin list check')
        self._run_plugin_list_setup(plugin_list)

        exp_coll = self.exp._get_collection()
        n_plugins = plugin_list._get_n_processing_plugins()

        #  ********* transport function ***********
        logging.info('Running transport_pre_plugin_list_run()')
        self._transport_pre_plugin_list_run()

        cp = self.exp.checkpoint
        for i in range(cp.get_checkpoint_plugin(), n_plugins):
            self.exp._set_experiment_for_current_plugin(i)
            self.__run_plugin(exp_coll['plugin_dict'][i])
            # end the plugin run if savu has been killed
            self.exp._barrier(msg='PluginRunner: plugin complete.')

            #  ********* transport functions ***********
            if self._transport_kill_signal():
                self._transport_cleanup(i+1)
                break
            self.exp._barrier(msg='PluginRunner: No kill signal... continue.')
            cp.output_plugin_checkpoint()

        #  ********* transport function ***********
        logging.info('Running transport_post_plugin_list_run')
        self._transport_post_plugin_list_run()

        # terminate any remaining datasets
        for data in self.exp.index['in_data'].values():
            self._transport_terminate_dataset(data)

        self.__output_final_message()

        if self.exp.meta_data.get('email'):
            cu.send_email(self.exp.meta_data.get('email'))

        return self.exp

    def __output_final_message(self):
        kill = True if 'killsignal' in \
            self.exp.meta_data.get_dictionary().keys() else False
        msg = "interrupted by killsignal" if kill else "Complete"
        stars = 40 if kill else 23
        cu.user_message("*"*stars)
        cu.user_message("* Processing " + msg + " *")
        cu.user_message("*"*stars)

    def __run_plugin(self, plugin_dict):
        plugin = self._transport_load_plugin(self.exp, plugin_dict)

        #  ********* transport function ***********
        self._transport_pre_plugin()
        cu.user_message("*Running the %s plugin*" % plugin.name)

        #  ******** transport 'process' function is called inside here ********
        plugin._run_plugin(self.exp, self)  # plugin driver

        self.exp._barrier(msg="Plugin returned from driver in Plugin Runner")
        cu._output_summary(self.exp.meta_data.get("mpi"), plugin)
        plugin._clean_up()
        finalise = self.exp._finalise_experiment_for_current_plugin()

        #  ********* transport function ***********
        self._transport_post_plugin()

        for data in finalise['remove'] + finalise['replace']:
            #  ********* transport function ***********
            self._transport_terminate_dataset(data)

        self.exp._reorganise_datasets(finalise)

    def _run_plugin_list_setup(self, plugin_list):
        """ Run the plugin list through the framework without executing the
        main processing.
        """
        plugin_list._check_loaders_and_savers()
        self.__check_gpu()

        n_loaders = self.exp.meta_data.plugin_list._get_n_loaders()
        n_plugins = plugin_list._get_n_processing_plugins()
        plist = plugin_list.plugin_list

        self.exp._setup(self, plugin_list)
        # set loaders
        for i in range(n_loaders):
            pu.plugin_loader(self.exp, plist[i])
            self.exp._set_initial_datasets()

        # run all plugin setup methods and store information in experiment
        # collection
        count = 0
        for plugin_dict in plist[n_loaders:n_loaders+n_plugins]:
            plugin = pu.plugin_loader(self.exp, plugin_dict, check=True)
            plugin._revert_preview(plugin.get_in_datasets())
            plugin_dict['cite'] = plugin.get_citation_information()            
            plugin._clean_up()
            self.exp._update(plugin_dict)
            self.exp._merge_out_data_to_in()
            count += 1
        self.exp._reset_datasets()
        try:
            plugin_list._add_missing_savers(self.exp)
        except Exception as e:
            print(e)
        cu.user_message("Plugin list check complete!")
        #  ********* transport function ***********
        self._transport_update_plugin_list()


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

            if not self.exp.meta_data.get('test_state'):
                for i in range(count):
                    handle = pv.nvmlDeviceGetHandleByIndex(i)
                    if pv.nvmlDeviceGetComputeRunningProcesses(handle):
                        raise Exception("Unfortunately, GPU %i is busy. Try \
                            resubmitting the job to the queue." % i)
        except Exception as e:
            raise Exception("Unable to run GPU plugins: %s", e.message)
        self.__set_gpu_processes(count)

    def __set_gpu_processes(self, count):
        processes = self.exp.meta_data.get('processes')
        if not [i for i in processes if 'GPU' in i]:
            logging.debug("GPU processes missing. GPUs found so adding them.")
            cpus = ['CPU'+str(i) for i in range(count)]
            gpus = ['GPU'+str(i) for i in range(count)]
            for i in range(min(count, len(processes))):
                processes[processes.index(cpus[i])] = gpus[i]
            self.exp.meta_data.set('processes', processes)
