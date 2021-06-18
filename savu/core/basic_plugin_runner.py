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
.. module:: basic_plugin_runner
   :platform: Unix
   :synopsis: Plugin list runner, which passes control to the transport layer.
.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>
"""

import logging

import savu.core.utils as cu
import savu.plugins.utils as pu
from savu.data.experiment_collection import Experiment


class BasicPluginRunner(object):
    """ Plugin list runner, which passes control to the transport layer.
    """

    def __init__(self, options, name='PluginRunner'):
        class_name = "savu.core.transports." + options["transport"] \
                     + "_transport"
        cu.add_base(self, cu.import_class(class_name))
        super(BasicPluginRunner, self).__init__()

        #  ********* transport function ***********
        self._transport_initialise(options)
        self.options = options
        # add all relevent locations to the path
        pu.get_plugins_paths()
        self.exp = Experiment(options)

    def _run_plugin_list(self):
        """ Create an experiment and run the plugin list.
        """
        self.exp.checkpoint = None
        plugin_list = self.exp.meta_data.plugin_list
        plugin_list._check_loaders()

        self.exp._set_nxs_filename()
        if self.exp.meta_data.get('process') == 0:
            fname = self.exp.meta_data.get('nxs_filename')
            plugin_list._save_plugin_list(fname)

        self.exp.__set_loaders_and_savers()

        #  ********* transport function ***********
        self._transport_pre_plugin_list_run()

        n_plugins = plugin_list._get_n_processing_plugins()
        n_loaders = self.exp.meta_data.plugin_list._get_n_loaders()

        plist = plugin_list.plugin_list
        count = 0
        for plugin_dict in plist[n_loaders:n_loaders+n_plugins]:
            self.exp.meta_data.set('nPlugin', count)
            self.__run_plugin(plugin_dict)
            count += 1

        # terminate any remaining datasets
        for data in list(self.exp.index['in_data'].values()):
            self._transport_terminate_dataset(data)

        cu.user_message("***********************")
        cu.user_message("* Processing Complete *")
        cu.user_message("***********************")

        logging.info('Processing complete')
        return self.exp

    def __run_plugin(self, plugin_dict):
        plugin = self._transport_load_plugin(self.exp, plugin_dict)
        self.exp.plugin = plugin
        plugin._main_setup(self.exp, plugin_dict['data'])

        self._transport_pre_plugin()

        plugin._run_plugin(self.exp, self)  # plugin driver
        self.exp._barrier()
        cu._output_summary(self.exp.meta_data.get("mpi"), plugin)
        plugin._clean_up()

        finalise = self.exp._finalise_experiment_for_current_plugin()

        #  ********* transport function ***********
        self._transport_post_plugin()

        for data in finalise['remove'] + finalise['replace']:
            #  ********* transport function ***********
            self._transport_terminate_dataset(data)

        self.exp._reorganise_datasets(finalise)
