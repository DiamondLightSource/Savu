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
.. module:: experiment_collection
   :platform: Unix
   :synopsis: Contains the Experiment class and all possible experiment 
   collections from which Experiment can inherit at run time.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

from savu.data.data_structures import Data
from savu.data.meta_data import MetaData

class Experiment(object):
    """
    One instance of this class is created at the beginning of the 
    processing chain and remains until the end.  It holds the current data
    object and a dictionary containing all metadata.
    """
   
    def __init__(self, options):
        self.meta_data = MetaData(options)
        self.info = self.meta_data.dict 
        self.index = {"in_data": {}, "out_data": {}}
        

    def create_data_object(self, dtype, name, bases=None): 
        transport_data = self.get_transport_data()
        self.index[dtype][name] = Data(self.import_class(transport_data))
        if bases is not None:
            self.index[dtype][name].add_base_classes(bases)        
        return self.index[dtype][name]
        

    def get_transport_data(self):
        transport_data = "savu.data.transport_data." + self.info["transport"] \
                            + "_transport_data"
        return transport_data
  

    def load_experiment_collection(self):
        transport_collection = self.info["transport"] + "_experiment"                    
        class_name = ''.join(x.capitalize() for x in transport_collection.split('_'))
        self.add_base(globals()[class_name])
        
    
    def import_class(self, class_name):
        name = class_name
        mod = __import__(name)
        components = name.split('.')
        for comp in components[1:]:
            mod = getattr(mod, comp)
        temp = name.split('.')[-1]
        module2class = ''.join(x.capitalize() for x in temp.split('_'))
        return getattr(mod, module2class.split('.')[-1])
        
        
    def add_base(self, transport):
        cls = self.__class__
        self.__class__ = cls.__class__(cls.__name__, (cls, transport), {})

            