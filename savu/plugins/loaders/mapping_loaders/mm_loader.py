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
.. module:: mm_loader
   :platform: Unix
   :synopsis: A class for loading multi-modal data

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

from savu.plugins.loaders.base_loader import BaseLoader
from savu.plugins.loaders.mapping_loaders.nxfluo_loader \
    import NxfluoLoader as fluo
from savu.plugins.loaders.mapping_loaders.nxxrd_loader \
    import NxxrdLoader as xrd
from savu.plugins.loaders.mapping_loaders.nxstxm_loader \
    import NxstxmLoader as stxm
from savu.plugins.loaders.mapping_loaders.nxmonitor_loader \
    import NxmonitorLoader as mon
import logging

from savu.plugins.utils import register_plugin


@register_plugin
class MmLoader(BaseLoader):
    def __init__(self, name='MmLoader'):
        super(MmLoader, self).__init__(name)
        self.fluo_keys = self.add_default_params(fluo(), 'fluo')
        self.xrd_keys = self.add_default_params(xrd(), 'xrd')
        self.stxm_keys = self.add_default_params(stxm(), 'stxm')
        self.mon_keys = self.add_default_params(mon(), 'monitor')

    def add_default_params(self, inst, name):
        ptools = self.get_plugin_tools()
        inst_keys = inst.parameters.keys()
        copy_keys = list(inst_keys - self.parameters.keys())
        if 'name' in copy_keys: copy_keys.remove('name')
        for key in copy_keys:
            ptools.param.set(key, inst.get_plugin_tools().param.get(key))
            ptools.parameters[key] = inst.get_plugin_tools().parameters[key]
        return inst_keys

    def separate_params(self, name, keys):
        mm_loader_keys = self.get_plugin_tools()._load_param_from_doc(
            self.get_plugin_tools()).keys()
        all_keys = keys - mm_loader_keys
        new_dict = {}
        for key in [k for k in all_keys if k != 'name']:
            new_dict[key] = self.parameters[key]
        new_dict['name'] = self.name_dict[name]
        new_dict['preview'] = self.parameters['preview'][new_dict['name']]
        return new_dict

    def __set_names(self):
        fluo, xrd, stxm, monitor = self.parameters['dataset_names']
        self.name_dict = {'fluo': fluo, 'xrd': xrd, 'stxm': stxm,
                          'monitor': monitor}

    def __set_preview(self):
        preview_dict = {}
        preview = self.parameters['preview']
        for name in list(self.name_dict.values()):
            preview_dict[name] = preview[name] if isinstance(preview, dict) \
                and name in list(preview.keys()) else preview if \
                    isinstance(preview, list) else []
        self.parameters['preview'] = preview_dict

    def setup(self):
        self.__set_names()
        self.__set_preview()
        self._data_loader(fluo(), 'fluo', self.fluo_keys)
        self._data_loader(xrd(), 'xrd', self.xrd_keys)
        self._data_loader(stxm(), 'stxm', self.stxm_keys)
        self._data_loader(mon(), 'monitor', self.mon_keys)

    def _data_loader(self, inst, name, key):
        debug_str = 'This file contains an ' + name
        warn_str = 'This file does not contain a ' + name
        try:
            params = self.separate_params(name, key)
            inst.initialise(params, self.exp)
            logging.debug(debug_str)
        except IndexError:
            # Delete the data object if it has already been created.
            if name in self.exp.index['in_data']:
                del self.exp.index['in_data'][name]
            logging.warning(warn_str)
        except:
            raise

    def final_parameter_updates(self):
        # names of individual datasets are not required
        self.delete_parameter_entry('name')
