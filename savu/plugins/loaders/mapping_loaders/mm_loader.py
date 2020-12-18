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
from savu.core.utils import docstring_parameter
from savu.plugins.loaders.mapping_loaders.base_multi_modal_loader \
    import BaseMultiModalLoader


@register_plugin
class MmLoader(BaseLoader):

    def __init__(self, name='MmLoader'):
        super(MmLoader, self).__init__(name)
        base = BaseMultiModalLoader()
        base._populate_default_parameters()
        self.doc_string = base.__doc__
        self.dict = base.parameters
        self.fluo_keys = self.set_params(fluo(), 'fluo')
        self.xrd_keys = self.set_params(xrd(), 'xrd')
        self.stxm_keys = self.set_params(stxm(), 'stxm')
        self.mon_keys = self.set_params(mon(), 'monitor')
        for key, value in self.dict.items():
            self.parameters[key] = value

    def set_params(self, inst, name):
        inst._populate_default_parameters()
        copy_keys = inst.parameters.keys() - self.dict.keys()
        for key in copy_keys:
            self.parameters[key] = inst.parameters[key]
        return list(copy_keys)

    def separate_params(self, name, keys):
        all_keys = list(self.dict.keys()) + keys
        new_dict = {}
        for key in [k for k in all_keys if k != 'name']:
            new_dict[key] = self.parameters[key]
        new_dict['name'] = self.name_dict[name]
        new_dict['preview'] = self.parameters['preview'][new_dict['name']]
        return new_dict

    @docstring_parameter(BaseMultiModalLoader.__doc__, xrd.__doc__,
                         stxm.__doc__, mon.__doc__, fluo.__doc__)
    def _override_class_docstring(self):
        """
        :u*param dataset_names: The names assigned to each dataset in the \
            order: fluorescence, diffraction, absorption, \
            monitor. Default: ['fluo', 'xrd', 'stxm', 'monitor'].
        :u*param preview: A slice list of required frames to apply to ALL \
        datasets, else a dictionary of slice lists where the key is the \
        dataset name. Default: [].

        {0} \n {1} \n {2} \n {3} \n {4}

        """
        pass

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
