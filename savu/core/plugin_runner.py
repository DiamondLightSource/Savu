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
        class_name = "savu.core.transports." + options["transport"] + "_transport"
        self.add_base(self.import_class(class_name))
        self.transport_control_setup(options)
        self.run_plugin_list(options)

    def import_class(self, class_name):
        name = class_name
        mod = __import__(name)
        components = name.split('.')
        for comp in components[1:]:
            mod = getattr(mod, comp)
        temp = name.split('.')[-1]
        module2class = ''.join(x.capitalize() for x in temp.split('_'))
        return getattr(mod, module2class.split('.')[-1])

    def add_base(self, ExtraBase):
        cls = self.__class__
        self.__class__ = cls.__class__(cls.__name__, (cls, ExtraBase), {})

    def run_plugin_list(self, options):
        logging.info("Starting to run the plugin list")
        experiment = Experiment(options)
        plugin_list = experiment.meta_data.plugin_list.plugin_list

        experiment.barrier()
        logging.info("Preparing to run the plugin list check")
        self.run_plugin_list_check(experiment, plugin_list)

        experiment.barrier()
        logging.info("Initialising metadata")
        expInfo = experiment.meta_data
        if expInfo.get_meta_data("process") is 0:
            logging.debug("Running process List.save_list_to_file")
            expInfo.plugin_list.save_plugin_list(
                expInfo.get_meta_data("nxs_filename"))

        experiment.barrier()
        logging.info("load relevant metadata")
        expInfo.set_transport_meta_data()  # *** do I need this?

        experiment.barrier()
        logging.info("divert to transport process and run process list")
        self.transport_run_plugin_list(experiment)

        print "Sorry for the wait..."
        print "You will be happy to know that your processing has now completed."
        print "Please have a nice day."

    def plugin_loader(self, exp, plugin_dict, **kwargs):
        logging.debug("Running plugin loader")

        try:
            plugin = self.load_plugin(plugin_dict['id'])
        except Exception as e:
            logging.error("failed to load the plugin")
            logging.error(e)
            raise e

        logging.debug("Getting pos and checkflag")
        pos = (kwargs["pos"] if "pos" in kwargs else None)
        check_flag = (kwargs["check"] if "check" in kwargs else False)

        logging.debug("Doing something with the check flag")
        if check_flag is True:
            try:
                plugin_dict["data"]["in_datasets"]
                self.set_datasets(plugin, exp, plugin_dict, pos)
            except KeyError:
                pass

        logging.debug("setting parameters")
        plugin.set_parameters(plugin_dict['data'])

        logging.debug("Running plugin setup")
        plugin.setup(exp)

        logging.debug("finished plugin loader")
        return plugin

    def run_plugins(self, exp, plugin_list, **kwargs):
        self.plugin_loader(exp, plugin_list[0])
        exp.set_nxs_filename()

        check = (kwargs["check"] if "check" in kwargs else False)

        for i in range(1, len(plugin_list)-1):
            exp.barrier()
            logging.info("Checking Plugin %s" % plugin_list[i]['name'])
            self.plugin_loader(exp, plugin_list[i], pos=i, check=check)

    def run_plugin_list_check(self, exp, plugin_list):
        exp.barrier()
        logging.info("Checking loaders and Savers")
        self.check_loaders_and_savers(exp, plugin_list)

        exp.barrier()
        logging.info("Running plugins with the check flag")
        self.run_plugins(exp, plugin_list, check=True)

        exp.barrier()
        logging.info("empty the data object dictionaries")
        exp.clear_data_objects()

        exp.barrier()
        logging.info("Plugin list check complete!")
        print "Plugin list check complete!"

    def get_names(self, names):
        try:
            data_names = names
        except KeyError:
            data_names = []
        return data_names

    def set_all_datasets(self, expIndex, name):
        data_names = []
        for key in expIndex["in_data"].keys():
            data_names.append(key)
        return data_names

    def check_nDatasets(self, exp, names, plugin_id, nSets, dtype, pos):
        try:
            if names[0] in "all":
                names = self.set_all_datasets(exp, dtype)
                # self.copy_plugin_to_list(names, pos)
        except IndexError:
            pass

        errorMsg = "***ERROR: Broken plugin chain. \n Please name the " + \
            str(nSets) + " " + dtype + " sets associated with the plugin " + \
            plugin_id + " in the process file."

        names = ([names] if type(names) is not list else names)
        if len(names) is not nSets:
            raise Exception(errorMsg)
        return names

    def set_datasets(self, plugin, exp, plugin_dict, pos):
        in_names = self.get_names(plugin_dict["data"]["in_datasets"])
        out_names = self.get_names(plugin_dict["data"]["out_datasets"])

        in_names = ('all' if len(in_names) is 0 else in_names)
        out_names = (in_names if len(out_names) is 0 else out_names)

        in_names = self.check_nDatasets(exp.index, in_names, plugin_dict["id"],
                                        plugin.nInput_datasets(), "in_data",
                                        pos)
        out_names = self.check_nDatasets(exp.index, out_names,
                                         plugin_dict["id"],
                                         plugin.nOutput_datasets(),
                                         "out_data",
                                         pos)

        plugin_dict["data"]["in_datasets"] = in_names
        plugin_dict["data"]["out_datasets"] = out_names

    def check_loaders_and_savers(self, experiment, plugin_list):

        first_plugin = plugin_list[0]
        end_plugin = plugin_list[-1]

        plugin = self.load_plugin(first_plugin['id'])
        # check the first plugin is a loader
        if not isinstance(plugin, BaseLoader):
            sys.exit("The first plugin in the process must inherit from BaseLoader")

        plugin = self.load_plugin(end_plugin['id'])
        # check the first plugin is a loader
        if not isinstance(plugin, BaseSaver):
            sys.exit("The final plugin in the process must inherit from BaseSaver")

    def load_plugin(self, plugin_name):
        """Load a plugin.

        :param plugin_name: Name of the plugin to import /path/loc/then.plugin.name
                        if there is no path, then the assumptiuon is an internal
                        plugin
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

