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
from savu.core.iterative_plugin_runner import IteratePluginGroup


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
            # need to check if we're at a plugin index that corresponds to a
            # plugin inside the group to iterate over or not
            current_iterate_plugin_group = None
            iterate_plugin_groups = self.exp.meta_data.get('iterate_groups')
            for iterate_plugin_group in iterate_plugin_groups:
                if i >= iterate_plugin_group['start_plugin_index'] and \
                    i <= iterate_plugin_group['end_plugin_index']:
                    current_iterate_plugin_group = iterate_plugin_group

            # check if plugin index is one that is the end of a group of plugins
            # to iterate over
            is_end_plugin = False
            if current_iterate_plugin_group is not None and \
                i == current_iterate_plugin_group['end_plugin_index']:
                is_end_plugin = True

            self.exp._set_experiment_for_current_plugin(i,
                is_end_plugin=is_end_plugin)
            memory_before = cu.get_memory_usage_linux()

            # check if plugin is both the start and end plugin, so then it can
            # be run correctly
            if current_iterate_plugin_group is not None and \
                current_iterate_plugin_group['start_plugin_index'] == \
                current_iterate_plugin_group['end_plugin_index'] and \
                i == current_iterate_plugin_group['end_plugin_index'] and \
                current_iterate_plugin_group['iterate_plugin_group']._ip_iteration == 0:
                # same as for when the end plugin is different to the start
                # plugin, do something a bit special for the end plugin
                plugin_name = self.__run_end_plugin_in_iterate_group_on_iteration_0(
                    current_iterate_plugin_group)
                plugin_name = current_iterate_plugin_group['iterate_plugin_group'].end_plugin.name
            else:
                # group of plugins to iterate over is more than one plugin
                if current_iterate_plugin_group is not None and \
                    i == current_iterate_plugin_group['start_plugin_index'] and \
                    current_iterate_plugin_group['iterate_plugin_group']._ip_iteration == 0:
                    print(f"Iteration {current_iterate_plugin_group['iterate_plugin_group']._ip_iteration}")
                    plugin = self.__run_plugin(exp_coll['plugin_dict'][i],
                        clean_up_plugin=False)
                    current_iterate_plugin_group['iterate_plugin_group'].set_start_plugin(plugin)
                    current_iterate_plugin_group['iterate_plugin_group'].add_plugin_to_iterate_group(plugin)
                elif current_iterate_plugin_group is not None and \
                    i == current_iterate_plugin_group['end_plugin_index'] and \
                    current_iterate_plugin_group['iterate_plugin_group']._ip_iteration == 0:
                    # do something a bit special for running the end plugin on
                    # iteration 0...
                    plugin_name = self.__run_end_plugin_in_iterate_group_on_iteration_0(
                        current_iterate_plugin_group)
                    plugin_name = current_iterate_plugin_group['iterate_plugin_group'].end_plugin.name
                else:
                    plugin = self.__run_plugin(exp_coll['plugin_dict'][i])
                    plugin_name = plugin.name
                    if current_iterate_plugin_group is not None and \
                        i >= current_iterate_plugin_group['start_plugin_index'] and \
                        i <= current_iterate_plugin_group['end_plugin_index'] and \
                        current_iterate_plugin_group['iterate_plugin_group']._ip_iteration == 0:
                        current_iterate_plugin_group['iterate_plugin_group'].add_plugin_to_iterate_group(plugin)

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

        return self.exp

    def __output_final_message(self):
        kill = True if 'killsignal' in \
                       self.exp.meta_data.get_dictionary().keys() else False
        msg = "interrupted by killsignal" if kill else "Complete"
        stars = 40 if kill else 23
        cu.user_message("*" * stars)
        cu.user_message("* Processing " + msg + " *")
        cu.user_message("*" * stars)

    def __run_end_plugin_in_iterate_group_on_iteration_0(self,
                                                         iterate_plugin_group_dict):
        '''
        Hacky solution to be able to run the end plugin on iteration 0 and still
        be able to change its output datasets to be only one of the original or
        the cloned dataset.

        This is done by copying a large amount of code from
        PluginRunner.__run_plugin(), and then adding a few things to change the
        ouput datasets of the end plugin in the group of plugins to iterate
        over.

        Note that this functionality probably could also be achieved by
        modifying PluginRunner.__run_plugin().
        '''
        start_plugin_index = iterate_plugin_group_dict['start_plugin_index']
        end_plugin_index = iterate_plugin_group_dict['end_plugin_index']
        iterate_plugin_group = iterate_plugin_group_dict['iterate_plugin_group']

        exp_coll = self.exp._get_collection()
        plugin_dict = exp_coll['plugin_dict'][end_plugin_index]
        # manually load the plugin, so then the output datasets can be modified
        # before running the plugin
        plugin = self._transport_load_plugin(self.exp, plugin_dict)
        # add the end plugin to IteratePluginGroup
        iterate_plugin_group.add_plugin_to_iterate_group(plugin)

        # check if this end plugin is ALSO the start plugin
        if start_plugin_index == end_plugin_index:
            iterate_plugin_group.set_start_plugin(plugin)

        # set the end plugin in IteratePluginGroup
        iterate_plugin_group.set_end_plugin(plugin)
        # setup the 'iterating' key in IteratePluginGroup._ip_data_dict
        iterate_plugin_group.set_alternating_datasets()
        # setup the datasets for iteration 0 and 1 inside the
        # IteratePluginGroup object
        iterate_plugin_group.setup_datasets()
        # set the output datasets of the end plugin
        iterate_plugin_group._IteratePluginGroup__set_datasets()

        # START of stuff copied from __run_plugin()

        #  ********* transport function ***********
        self._transport_pre_plugin()
        cu.user_message("*Running the %s plugin*" % plugin.name)
        plugin._run_plugin(self.exp, self)

        # don't clean up the end plugin on iteration 0 (just like we're not
        # cleaning up any of the other plugins in the group to iterate over on
        # iteration 0), so then the PluginData objects associated to the plugin
        # objects remain intact
        info_msg = f"Not cleaning up plugin {plugin.name}, as it is the end " \
            f"plugin in a group to iterate over"
        print(info_msg)

        # ADDITIONAL stuff for running iterations

        # since the end plugin has now been run, the group of plugins to
        # iterate over has been executed once, and this counts as having done
        # one iteration (ie, at this point, iteration 0 is complete)
        iterate_plugin_group.increment_ip_iteration()

        # kick off all subsequent iterations
        while iterate_plugin_group._ip_iteration < \
            iterate_plugin_group._ip_fixed_iterations:
            iterate_plugin_group._execute_iteration(self.exp, self)

        # set which output dataset to keep, and which to remove
        iterate_plugin_group._finalise_iterated_datasets()

        # END of additional stuff for running iterations

        self.exp._barrier(msg="Plugin returned from driver in Plugin Runner")
        cu._output_summary(self.exp.meta_data.get("mpi"), plugin)
        finalise = self.exp._finalise_experiment_for_current_plugin()

        #  ********* transport function ***********
        self._transport_post_plugin()

        for data in finalise['remove'] + finalise['replace']:
            #  ********* transport function ***********
            self._transport_terminate_dataset(data)

        self.exp._reorganise_datasets(finalise)

        # END of stuff copied from __run_plugin()

        # TODO: for now, return the name of the start plugin of the group to
        # iterate over
        return iterate_plugin_group.start_plugin.name

    def __run_plugin(self, plugin_dict, clean_up_plugin=True, plugin=None):
        # allow plugin objects to be reused for running iteratively
        if plugin is None:
            plugin = self._transport_load_plugin(self.exp, plugin_dict)

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
            print(f"Cleaning up plugin {plugin.name}")
            plugin._clean_up()
        else:
            info_msg = f"Not cleaning up plugin {plugin.name}, as it is in a " \
                f"group to iterate over"
            print(info_msg)

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

        # set metadata that is for indicating if the current plugin is the end
        # plugin of a group of plugins to iterate over
        self.exp.meta_data.set('is_end_plugin_in_iterate_group', False)
        for plugin_dict in plist[n_loaders:n_loaders + n_plugins]:

            # need to catch if the plugin is part of a group of plugins to
            # iterate over
            #
            # this is because the info of if a plugin is at the END of a group
            # of plugins to iterate is being set in the Experiment object's
            # MetaData (self.exp.meta_data)

            # TODO: need some sort of marker (that will likely come from
            # savu_config) that defines the indices of
            # - the plugin that starts the group of plugins to iterate
            # - the plugin that ends the group of plugins to iterate
            #
            # Also, it needs to be relative to the arithmetic that removes any
            # loaders from the loop counter here
            #
            # So there needs to be a check in this loop, on every iteration, for
            # if there is this "marker" that indicates the start of a group of
            # plugins to iterate
            # Pseudocode:
            # if PLUGIN_IS_START_OF_ITERATIVE_GROUP:
            #    set start_plugin_index (from value in savu_config or something)
            #    set end_plugin_index (from value in savu_config or something)
            #    create IteratePluginGroup object

            if self.exp.meta_data.dict['nPlugin'] == 1:
                start_plugin_index = 1
                #end_plugin_index = 1
                end_plugin_index = 2
                iterate_plugin_group = IteratePluginGroup(self)
                # add this IteratePluginGroup object to iterate_groups key in
                # self.exp.meta_data
                #
                # TODO:for some reason, self.exp.meta_data.dict.get('nPlugin')
                # for a plugins is 1 more in PluginRunner._run_plugin_list()
                # than in this method; figure out why, because this hardcoded
                # stuff down below is bad
                iterate_plugin_groups_entry = {
                    'start_plugin_index': start_plugin_index + 1,
                    'end_plugin_index': end_plugin_index + 1,
                    'iterate_plugin_group': iterate_plugin_group
                }
                iterate_plugin_groups = self.exp.meta_data.get('iterate_groups')
                iterate_plugin_groups.append(iterate_plugin_groups_entry)
                # reset the value in the metadata?
                self.exp.meta_data.set('iterate_groups', iterate_plugin_groups)

            # need to check if we're at a plugin index that corresponds to a
            # plugin inside the group to iterate over or not
            current_iterate_plugin_group = None
            iterate_plugin_groups = self.exp.meta_data.get('iterate_groups')
            for iterate_plugin_group in iterate_plugin_groups:
                if count >= iterate_plugin_group['start_plugin_index'] and \
                    count <= iterate_plugin_group['end_plugin_index']:
                    current_iterate_plugin_group = iterate_plugin_group

            if current_iterate_plugin_group is not None and \
                count == current_iterate_plugin_group['start_plugin_index']:
                info_msg = f"Plugin index {count} isn't at the end of a " \
                    f"group to iterate over, so leaving its metadata alone"
                print(info_msg)
                # set metadata that indicates to
                # BaseTransport._transport_post_process() that processing is
                # currently within an iterative loop, to then keep write
                # permissions on intermediate files

            if current_iterate_plugin_group is not None and \
                count == current_iterate_plugin_group['end_plugin_index']:
                # set the metadata indicating the end plugin in the group to
                # iterate over
                self.exp.meta_data.set('is_end_plugin_in_iterate_group', True)

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
