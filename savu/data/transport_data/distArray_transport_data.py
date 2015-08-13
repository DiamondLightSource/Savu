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
.. module:: hdf5_transport_data
   :platform: Unix
   :synopsis: A data transport class that is inherited by Data class at 
   runtime. It performs the movement of the data, including loading and saving.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""
import os
import logging 

import numpy as np

from savu.core.utils import logmethod

class Hdf5TransportData(object):
    """
    The Hdf5TransportData class performs the loading and saving of data 
    specific to a hdf5 transport mechanism.
    """
            
    def __init__(self):
        self.backing_file = None

    
    def load_data(self, plugin_runner, exp):

        final_plugin = exp.info["plugin_list"][-1]
        saver_plugin = plugin_runner.load_plugin(final_plugin["id"])

        logging.debug("generating all output files")
        out_data_objects = []
        count = 0
        for plugin_dict in exp.info["plugin_list"][1:-1]:
            
            plugin_id = plugin_dict["id"]
            logging.debug("Loading plugin %s", plugin_id)
            plugin = plugin_runner.load_plugin(plugin_id)
    
            plugin.setup(exp)
            
            self.set_filenames(exp, plugin, plugin_id, count)

            saver_plugin.setup(exp)
            
            out_data_objects.append(exp.index["out_data"].copy())
            
            count += 1
            
        return out_data_objects

    
    def set_filenames(self, exp, plugin, plugin_id, count):
        exp.info["filename"] = {}
        exp.info["group_name"] = {}
        for key in exp.index["out_data"].keys():
            filename = os.path.join(exp.info["out_path"],"%s%02i_%s" % \
                          (exp.info["process_filename"], count, plugin_id))
            filename = filename + "_" + key + ".h5"
            group_name = "%i-%s" % (count, plugin.name)
            logging.debug("Creating output file %s", filename)
            exp.info["filename"][key] = filename
            exp.info["group_name"][key] = group_name

        
    def save_data(self):
        """
        Closes the backing file and completes work
        """
        if self.backing_file is not None:
            logging.debug("Completing file %s",self.backing_file.filename)
            self.backing_file.close()
            self.backing_file = None

