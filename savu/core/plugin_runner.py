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
        plugin_list = experiment.info["plugin_list"]

        self.check_loaders_and_savers(experiment, plugin_list)

        self.set_outfilename(experiment)
        if experiment.info["process"] is 0:
            logging.debug("Running process List.save_list_to_file")
            experiment.meta_data.plugin_list.save_plugin_list()
        
        # load relevant metadata 
        experiment.meta_data.set_transport_meta_data() #*** do I need this?
        self.transport_run_plugin_list(experiment)


    def check_loaders_and_savers(self, experiment, plugin_list):
        first_plugin = plugin_list[0]
        plugin = self.load_plugin(first_plugin['id'])   
        
        #*** temporary fix!!!
        plugins = []
        temp = {}
        temp['name'] = "nxfluo_loader"
        temp['id'] = 'savu.plugins.nxfluo_loader'
        temp['data'] = {}
        plugins.append(temp)
#         plugins.append(experiment.info["plugin_list"][0])
#         temp = {}
#         temp['name'] = "astra_FBP_recon"
#         temp['id'] = 'savu.plugins.astra_recon_cpu'
#         temp['data'] = {}        
#         plugins.append(temp)
#         #plugins.append(experiment.info["plugin_list"][1])
#         temp = {}
#         temp['name'] = "hdf5_tomo_saver"
#         temp['id'] = 'savu.plugins.hdf5_tomo_saver'
#         temp['data'] = {}
#         plugins.append(temp)
        experiment.meta_data.set_meta_data("plugin_list", plugins)
        #***

        plugin_list = experiment.meta_data.get_meta_data("plugin_list")
        first_plugin = plugin_list[0]
        end_plugin = plugin_list[-1]

        plugin = self.load_plugin(first_plugin['id'])           
        # check the first plugin is a loader
        if isinstance(plugin, BaseLoader):
            plugin.setup(experiment)
        else:
            sys.exit("The first plugin in the process must inherit from BaseLoader")
    
#         plugin = self.load_plugin(end_plugin['id'])
#         # check the first plugin is a loader
#         if not isinstance(plugin, BaseSaver):
#             sys.exit("The final plugin in the process must inherit from BaseSaver")
    
    
    def set_outfilename(self, exp):
        exp.info["out_filename"] = {}
        for name in exp.index["in_data"].keys():
            filename = os.path.basename(exp.index["in_data"][name].backing_file.filename)
            filename = os.path.splitext(filename)[0]
            exp.info["out_filename"][name] = os.path.join(exp.info["out_path"],
             "%s_processed_%s.nxs" % (filename, time.strftime("%Y%m%d%H%M%S")))
        
    
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
