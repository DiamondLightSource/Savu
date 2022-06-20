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
from savu.data.stats.statistics import Statistics
from savu.core.iterative_plugin_runner import IteratePluginGroup
from savu.core.iterate_plugin_group_utils import check_if_in_iterative_loop, \
    check_if_end_plugin_in_iterate_group


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
        self.exp._setup(self)
        Statistics._setup_class(self.exp)

        plugin_list = self.exp.meta_data.plugin_list
        logging.info('Running the plugin list check')
        self._run_plugin_list_setup(plugin_list)

        exp_coll = self.exp._get_collection()
        n_plugins = plugin_list._get_n_processing_plugins()

        #  ********* transport function ***********
        logging.info('Running transport_pre_plugin_list_run()')
        self._transport_pre_plugin_list_run()

        cp = self.exp.checkpoint
        checkpoint_plugin = cp.get_checkpoint_plugin()
        for i in range(checkpoint_plugin, n_plugins):
            self.exp._set_experiment_for_current_plugin(i)
            memory_before = cu.get_memory_usage_linux()

            # now that nPlugin has been reset, need to check if we're at a
            # plugin index that corresponds to a plugin inside the group to
            # iterate over or not
            current_iterate_plugin_group = check_if_in_iterative_loop(self.exp)

            if current_iterate_plugin_group is None:
                # not in an iterative loop, run as normal
                plugin = self.__run_plugin(exp_coll['plugin_dict'][i])
                plugin_name = plugin.name
            else:
                # in an iterative loop, run differently
                plugin_name = \
                    current_iterate_plugin_group._execute_iteration_0(
                        self.exp, self)

            self.exp._barrier(msg='PluginRunner: plugin complete.')

            memory_after = cu.get_memory_usage_linux()
            logging.debug("{} memory usage before: {} MB, after: {} MB, change: {} MB".format(
                plugin_name, memory_before, memory_after, memory_after - memory_before))

            #  ********* transport functions ***********
            # end the plugin run if savu has been killed
            if self._transport_kill_signal():
                self._transport_cleanup(i + 1)
                break
            self.exp._barrier(msg='PluginRunner: No kill signal... continue.')
            Statistics._count()
            cp.output_plugin_checkpoint()

        #  ********* transport function ***********
        logging.info('Running transport_post_plugin_list_run')
        self._transport_post_plugin_list_run()

        # terminate any remaining datasets
        for data in list(self.exp.index['in_data'].values()):
            self._transport_terminate_dataset(data)

        self.__output_final_message()

        if self.exp.meta_data.get('email'):
            cu.send_email(self.exp.meta_data.get('email'))

        Statistics._post_chain()
        return self.exp

    def __output_final_message(self):
        kill = True if 'killsignal' in \
                       self.exp.meta_data.get_dictionary().keys() else False
        msg = "interrupted by killsignal" if kill else "Complete"
        stars = 40 if kill else 23
        cu.user_message("*" * stars)
        cu.user_message("* Processing " + msg + " *")
        cu.user_message("*" * stars)

    def __run_plugin(self, plugin_dict, clean_up_plugin=True, plugin=None):
        # allow plugin objects to be reused for running iteratively
        if plugin is None:
            plugin = self._transport_load_plugin(self.exp, plugin_dict)

        iterate_plugin_group = check_if_in_iterative_loop(self.exp)

        if iterate_plugin_group is not None and \
            iterate_plugin_group._ip_iteration == 0:
                iterate_plugin_group.add_plugin_to_iterate_group(plugin)

        is_end_plugin_in_iterative_loop = check_if_end_plugin_in_iterate_group(
            self.exp)

        if iterate_plugin_group is not None and \
            is_end_plugin_in_iterative_loop and \
            iterate_plugin_group._ip_iteration == 0:

            # check if this end plugin is ALSO the start plugin
            if iterate_plugin_group.start_index == \
                iterate_plugin_group.end_index:
                iterate_plugin_group.set_start_plugin(plugin)

            # set the end plugin in IteratePluginGroup
            iterate_plugin_group.set_end_plugin(plugin)
            # setup the 'iterating' key in IteratePluginGroup._ip_data_dict
            iterate_plugin_group.set_alternating_datasets()
            # setup the PluginData objects
            iterate_plugin_group.set_alternating_plugin_datasets()
            # setup the datasets for iteration 0 and 1 inside the
            # IteratePluginGroup object
            iterate_plugin_group.setup_datasets()
            # set the output datasets of the end plugin
            iterate_plugin_group._IteratePluginGroup__set_datasets()

        #  ********* transport function ***********
        self._transport_pre_plugin()
        cu.user_message("*Running the %s plugin*" % plugin.name)

        #  ******** transport 'process' function is called inside here ********
        plugin._run_plugin(self.exp, self)  # plugin driver

        self.exp._barrier(msg="Plugin returned from driver in Plugin Runner")
        cu._output_summary(self.exp.meta_data.get("mpi"), plugin)

        # if NOT in an iterative loop, clean up the PluginData associated with
        # the Data objects in the plugin object as normal
        #
        # if in an iterative loop, do not clean up the PluginData object
        # associated with the Data objects of the plugin, apart from for the
        # last iteration
        if clean_up_plugin:
            logging.debug(f"Cleaning up plugin {plugin.name}")
            plugin._clean_up()
        else:
            info_msg = f"Not cleaning up plugin {plugin.name}, as it is in a " \
                f"group to iterate over, will only copy metadata"
            # TODO: maybe other things in Plugin._clean_up() should also be
            # done?
            plugin._Plugin__copy_meta_data()
            logging.debug(info_msg)

        finalise = self.exp._finalise_experiment_for_current_plugin()

        #  ********* transport function ***********
        self._transport_post_plugin()

        for data in finalise['remove'] + finalise['replace']:
            #  ********* transport function ***********
            self._transport_terminate_dataset(data)

        self.exp._reorganise_datasets(finalise)

        return plugin

    def _run_plugin_list_setup(self, plugin_list):
        """ Run the plugin list through the framework without executing the
        main processing.
        """
        plugin_list._check_loaders()
        self.__check_gpu()

        n_loaders = self.exp.meta_data.plugin_list._get_n_loaders()
        n_plugins = plugin_list._get_n_processing_plugins()
        plist = plugin_list.plugin_list

        # set loaders
        for i in range(n_loaders):
            pu.plugin_loader(self.exp, plist[i])
            self.exp._set_initial_datasets()

        # run all plugin setup methods and store information in experiment
        # collection
        count = 0

        for plugin_dict in plist[n_loaders:n_loaders + n_plugins]:
            self.__plugin_setup(plugin_dict, count)
            count += 1

        plugin_list._add_missing_savers(self.exp)

        #  ********* transport function ***********
        self._transport_update_plugin_list()

        # check added savers
        for plugin_dict in plist[n_loaders + count:]:
            self.__plugin_setup(plugin_dict, count)
            count += 1

        self.exp._reset_datasets()
        self.exp._finalise_setup(plugin_list)
        cu.user_message("Plugin list check complete!")

    def __plugin_setup(self, plugin_dict, count):
        self.exp.meta_data.set("nPlugin", count)
        plugin = pu.plugin_loader(self.exp, plugin_dict, check=True)
        plugin._revert_preview(plugin.get_in_datasets())
        plugin_dict['cite'] = plugin.tools.get_citations()
        plugin._clean_up()
        self.exp._merge_out_data_to_in(plugin_dict)

    def __check_gpu(self):
        """ Check if the process list contains GPU processes and determine if
        GPUs exists. Add GPU processes to the processes list if required."""
        if not self.exp.meta_data.plugin_list._contains_gpu_processes():
            return

        try:
            import pynvml as pv
        except Exception:
            logging.debug("pyNVML module not found")
            raise Exception("pyNVML module not found")

        try:
            pv.nvmlInit()
            count = int(pv.nvmlDeviceGetCount())
            if count == 0:
                raise Exception("No GPUs found")
            logging.debug("%s GPUs have been found.", count)

            if not self.exp.meta_data.get('test_state'):
                for i in range(count):
                    handle = pv.nvmlDeviceGetHandleByIndex(i)
                    if pv.nvmlDeviceGetComputeRunningProcesses(handle):
                        raise Exception("Unfortunately, GPU %i is busy. Try \
                            resubmitting the job to the queue." % i)
        except Exception as e:
            raise Exception("Unable to run GPU plugins: %s", str(e))
        self.__set_gpu_processes(count)

    def __set_gpu_processes(self, count):
        processes = self.exp.meta_data.get('processes')
        if not [i for i in processes if 'GPU' in i]:
            logging.debug("GPU processes missing. GPUs found so adding them.")
            cpus = ['CPU' + str(i) for i in range(count)]
            gpus = ['GPU' + str(i) for i in range(count)]
            for i in range(min(count, len(processes))):
                processes[processes.index(cpus[i])] = gpus[i]
            self.exp.meta_data.set('processes', processes)
