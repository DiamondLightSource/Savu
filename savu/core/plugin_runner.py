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
import copy

import savu.core.utils as cu
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
        cu.add_base(self, cu.import_class(self, class_name))
        self.transport_control_setup(options)
        self.exp = None

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
        logging.info("load relevant metadata")
        expInfo.set_transport_meta_data()  # *** do I need this?

        self.exp.barrier()
        logging.info("divert to transport process and run process list")
        self.transport_run_plugin_list()

        print "***********************"
        print "* Processing Complete *"
        print "***********************"
        return self.exp

    def plugin_loader(self, plugin_dict, **kwargs):
        logging.debug("Running plugin loader")

        try:
            plugin = self.load_plugin(plugin_dict['id'])
        except Exception as e:
            logging.error("failed to load the plugin")
            logging.error(e)
            raise e

        logging.debug("Getting checkflag")
        check_flag = kwargs.get('check', False)

        logging.debug("Doing something with the check flag")
        if check_flag:
            try:
                plugin_dict["data"]["in_datasets"]
                self.set_datasets(plugin, plugin_dict)
            except KeyError:
                pass

        logging.debug("Running plugin main setup")
        plugin.main_setup(self.exp, plugin_dict['data'])

        logging.debug("finished plugin loader")
        return plugin

    def run_plugins(self, plugin_list, **kwargs):
        self.plugin_loader(plugin_list[0])
        self.exp.set_nxs_filename()

        check = kwargs.get('check', False)

        for i in range(1, len(plugin_list)-1):
            self.exp.barrier()
            logging.info("Checking Plugin %s" % plugin_list[i]['name'])
            self.plugin_loader(plugin_list[i], check=check)
            self.exp.merge_out_data_to_in()

    def run_plugin_list_check(self, plugin_list):
        self.exp.barrier()
        logging.info("Checking loaders and Savers")
        self.check_loaders_and_savers(plugin_list)

        self.exp.barrier()
        logging.info("Running plugins with the check flag")
        self.run_plugins(plugin_list, check=True)

        self.exp.barrier()
        logging.info("empty the data object dictionaries")
        self.exp.clear_data_objects()

        self.exp.barrier()
        logging.info("Plugin list check complete!")
        print "Plugin list check complete!"

    def get_names(self, names):
        try:
            data_names = names
        except KeyError:
            data_names = []
        return data_names

    def set_all_datasets(self, name):
        data_names = []
        for key in self.exp.index["in_data"].keys():
            data_names.append(key)
        return data_names

    def check_nDatasets(self, names, plugin_id, nSets, dtype):
        try:
            if names[0] in "all":
                names = self.set_all_datasets(dtype)
        except IndexError:
            pass

        errorMsg = "***ERROR: Broken plugin chain. \n Please name the " + \
            str(nSets) + " " + dtype + " sets associated with the plugin " + \
            plugin_id + " in the process file."

        names = ([names] if type(names) is not list else names)
        if len(names) is not nSets:
            raise Exception(errorMsg)
        return names

    def set_datasets(self, plugin, plugin_dict):
        in_names = self.get_names(plugin_dict["data"]["in_datasets"])
        out_names = self.get_names(plugin_dict["data"]["out_datasets"])

        default_in_names = plugin.parameters['in_datasets']
        default_out_names = plugin.parameters['out_datasets']

        in_names = in_names if in_names else default_in_names
        out_names = out_names if out_names else default_out_names

        in_names = ('all' if len(in_names) is 0 else in_names)
        out_names = (in_names if len(out_names) is 0 else out_names)

        in_names = self.check_nDatasets(in_names, plugin_dict["id"],
                                        plugin.nInput_datasets(), "in_data")
        out_names = self.check_nDatasets(out_names, plugin_dict["id"],
                                         plugin.nOutput_datasets(), "out_data")

        plugin_dict["data"]["in_datasets"] = in_names
        plugin_dict["data"]["out_datasets"] = out_names

    def check_loaders_and_savers(self, plugin_list):

        first_plugin = plugin_list[0]
        end_plugin = plugin_list[-1]

        plugin = self.load_plugin(first_plugin['id'])
        # check the first plugin is a loader
        if not isinstance(plugin, BaseLoader):
            sys.exit("The first plugin in the process must "
                     "inherit from BaseLoader")

        plugin = self.load_plugin(end_plugin['id'])
        # check the final plugin is a saver
        if not isinstance(plugin, BaseSaver):
            sys.exit("The final plugin in the process must "
                     "inherit from BaseSaver")

    def reorganise_datasets(self, out_data_objs, link_type):
        out_data_list = self.exp.index["out_data"]
        self.close_unwanted_files(out_data_list)
        self.remove_unwanted_data(out_data_objs)

        self.exp.barrier()
        logging.info("Copy out data to in data")
        self.copy_out_data_to_in_data(link_type, out_data_objs)

        self.exp.barrier()
        logging.info("Clear up all data objects")
        self.exp.clear_out_data_objects()

    def remove_unwanted_data(self, out_data_objs):
        logging.info("Remove unwanted data from the plugin chain")
        for out_objs in out_data_objs:
            if out_objs.remove is True:
                self.exp.remove_dataset(out_objs)

    def close_unwanted_files(self, out_data_list):
        for out_objs in out_data_list:
            if out_objs in self.exp.index["in_data"].keys():
                self.exp.index["in_data"][out_objs].close_file()

    def copy_out_data_to_in_data(self, link_type, out_data_obj):
        for output in out_data_obj:
            output.save_data(link_type)
            self.exp.index["in_data"][output.name] = copy.deepcopy(output)

#    def reorganise_datasets(self, out_datasets, link_type):
#        self.close_unwanted_files(out_datasets)
#        self.remove_unwanted_data(out_datasets)
#
#        self.exp.barrier()
#        logging.info("Copy out data to in data")
#        self.copy_out_data_to_in_data(link_type)
#
#        self.exp.barrier()
#        logging.info("Clear up all data objects")
#        self.exp.clear_out_data_objects()
#
#    def remove_unwanted_data(self, out_datasets):
#        logging.info("Remove unwanted data from the plugin chain")
#        for out_objs in out_datasets:
#            if out_objs.remove is True:
#                self.exp.remove_dataset(out_objs)
#
#    def close_unwanted_files(self, out_datasets):
#        for out_objs in out_datasets:
#            if out_objs in self.exp.index["in_data"].keys():
#                self.exp.index["in_data"][out_objs].close_file()
#
#    def copy_out_data_to_in_data(self, link_type):
#        for key in self.exp.index["out_data"]:
#            output = self.exp.index["out_data"][key]
#            output.save_data(link_type)
#            self.exp.index["in_data"][key] = copy.deepcopy(output)

    def load_plugin(self, plugin_name):
        """Load a plugin.

        :param plugin_name: Name of the plugin to import
                        path/loc/then.plugin.name if there is no path, then the
                        assumptiuon is an internal plugin
        :type plugin_name: str.
        :returns:  An instance of the class described by the named plugin

        """
        logging.debug("getting class")
        logging.debug("plugin name is %s" % plugin_name)
        #clazz = self.import_class(plugin_name)

        name = plugin_name
        logging.debug("about to import the module")
        # TODO This appears to be the failing line.
        mod = __import__(name)
        components = name.split('.')
        logging.debug("Getting the module")
        for comp in components[1:]:
            mod = getattr(mod, comp)
        logging.debug("about to split the name")
        temp = name.split('.')[-1]
        logging.debug("getting the classname from the module")
        module2class = ''.join(x.capitalize() for x in temp.split('_'))
        logging.debug("getting the class from the classname")
        clazz = getattr(mod, module2class.split('.')[-1])
        logging.debug("getting class instance")
        instance = self.get_class_instance(clazz)
        logging.debug("returning class instance")
        return instance

    def get_class_instance(self, clazz):
        instance = clazz()
        instance.populate_default_parameters()
        return instance
