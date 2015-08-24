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
import os
import logging 
import time
import sys

import copy

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
        experiment = Experiment(options)
        plugin_list = experiment.meta_data.plugin_list.plugin_list

        self.run_plugin_list_check(experiment, plugin_list)
        self.plugin_loader(experiment, plugin_list[0], True)
        self.set_outfilename(experiment)

        expInfo = experiment.meta_data
        if expInfo.get_meta_data("process") is 0:
            logging.debug("Running process List.save_list_to_file")
            expInfo.plugin_list.save_plugin_list(
                expInfo.get_meta_data("out_filename").values()[0])

        # load relevant metadata 
        expInfo.set_transport_meta_data() #*** do I need this?
        # divert to transport process and run process list
        self.transport_run_plugin_list(experiment)
        
        print "Sorry for the wait..."
        print "You will be happy to know that your processing has now completed."
        print "Please have a nice day."


    def plugin_loader(self, experiment, plugin_dict, flag = False):                     
        plugin = self.load_plugin(plugin_dict['id'])      
        
        if flag is False:
             self.set_datasets(plugin, experiment, plugin_dict)
                                        
        plugin.set_parameters(plugin_dict['data'])
        plugin.setup(experiment)


    def run_plugin_list_check(self, exp, plugin_list):
        self.check_loaders_and_savers(exp, plugin_list)
        self.plugin_loader(exp, plugin_list[0], True)
        
        for plugin_dict in plugin_list[1:-1]:
            self.plugin_loader(exp, plugin_dict)

            for key in exp.index["out_data"]:
                exp.index["in_data"][key] = \
                               copy.deepcopy(exp.index["out_data"][key])
    
        # empty the data object dictionaries            
        exp.index["in_data"] = {}
        exp.index["out_data"] = {}
        print "Plugin list check complete!"
         
                                                                                          
    def get_names(self, names):         
        try:
            data_names = names
        except KeyError:
            data_names = []
        return data_names


    def set_all_datasets(self, expIndex, name):
        data_names = []
        for key in expIndex[name].keys():
            data_names.append(key)
        return data_names
        
        
    def check_nDatasets(self, exp, names, plugin_id, nSets, dtype):
        try:
            if names[0] in "all":
                names = self.set_all_datasets(exp, dtype)
        except IndexError:
            pass
        
        errorMsg = "***ERROR: Broken plugin chain. \n Please name the " + \
            str(nSets) + " " + dtype + " sets associated with the plugin " + \
            plugin_id + " in the process file."

        names = ([names] if type(names) is not list else names)
        if len(names) is not nSets:
            raise Exception(errorMsg)                


    def set_datasets(self, plugin, exp, plugin_dict):
        in_names = self.get_names(plugin_dict["data"]["in_datasets"])
        out_names = self.get_names(plugin_dict["data"]["out_datasets"])

        in_names = ('all' if len(in_names) is 0 else in_names)
        out_names = (in_names if len(out_names) is 0 else out_names)

        print in_names, out_names

        self.check_nDatasets(exp.index, in_names, plugin_dict["id"],
                             plugin.nInput_datasets(), "in_data")
        self.check_nDatasets(exp.index, out_names, plugin_dict["id"],
                             plugin.nOutput_datasets(), "out_data")


        expInfo = exp.meta_data
 
#        if "plugin_datasets" not in expInfo.get_dictionary().keys():
#            expInfo.set_meta_data("plugin_datasets",{})

        expInfo.set_meta_data(["plugin_datasets", "in_data"], in_names)
        expInfo.set_meta_data(["plugin_datasets", "out_data"], out_names)
        print "in_data is ", expInfo.get_meta_data(["plugin_datasets", "in_data"])
        print "out_data is ", expInfo.get_meta_data(["plugin_datasets", "out_data"])


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
    
    
    def set_outfilename(self, exp):
        expInfo = exp.meta_data
        expInfo.set_meta_data("out_filename", {})
        for name in exp.index["in_data"].keys():
            filename = os.path.basename(exp.index["in_data"][name].backing_file.filename)
            filename = os.path.splitext(filename)[0]
            filename = os.path.join(expInfo.get_meta_data("out_path"),
             "%s_processed_%s.nxs" % (filename, time.strftime("%Y%m%d%H%M%S")))
            expInfo.set_meta_data(["out_filename", name], filename)
        
    
    def load_plugin(self, plugin_name):
        """Load a plugin.
    
        :param plugin_name: Name of the plugin to import /path/loc/then.plugin.name
                        if there is no path, then the assumptiuon is an internal
                        plugin
        :type plugin_name: str.
        :returns:  An instance of the class described by the named plugin
    
        """       
        clazz = self.import_class(plugin_name)
        return self.get_class_instance(clazz)
        
        
    def get_class_instance(self, clazz):
        instance = clazz()
        instance.populate_default_parameters()
        return instance


class CitationInformation(object):
    """
    Descriptor of Citation Information for plugins
    """

    def __init__(self):
        super(CitationInformation, self).__init__()
        self.description = "Default Description"
        self.doi = "Default DOI"
        self.endnote = "Default Endnote"
        self.bibtex = "Default Bibtex"

    def write(self, hdf_group):
        citation_group = hdf_group.create_group('citation')
        citation_group.attrs[NX_CLASS] = 'NXcite'
        description_array = np.array([self.description])
        citation_group.create_dataset('description',
                                      description_array.shape,
                                      description_array.dtype,
                                      description_array)
        doi_array = np.array([self.doi])
        citation_group.create_dataset('doi',
                                      doi_array.shape,
                                      doi_array.dtype,
                                      doi_array)
        endnote_array = np.array([self.endnote])
        citation_group.create_dataset('endnote',
                                      endnote_array.shape,
                                      endnote_array.dtype,
                                      endnote_array)
        bibtex_array = np.array([self.bibtex])
        citation_group.create_dataset('bibtex',
                                      bibtex_array.shape,
                                      bibtex_array.dtype,
                                      bibtex_array)
    
