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
.. module:: i18_mm_loader
   :platform: Unix
   :synopsis: A class for loading multiple data types in a multi-modal\
       experimental setup.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import logging
from savu.plugins.loaders.base_loader import BaseLoader
from savu.plugins.unregistered.i18_loaders.base_i18_multi_modal_loader\
    import BaseI18MultiModalLoader
from savu.plugins.unregistered.i18_loaders.i18_xrd_loader \
    import I18XrdLoader as xrd
from savu.plugins.unregistered.i18_loaders.i18_fluo_loader \
    import I18FluoLoader as fluo
from savu.plugins.unregistered.i18_loaders.i18_stxm_loader \
    import I18StxmLoader as stxm
from savu.plugins.unregistered.i18_loaders.i18_monitor_loader \
    import I18MonitorLoader as mon

from savu.plugins.utils import register_plugin
from savu.core.utils import docstring_parameter


class I18MmLoader(BaseLoader):
    def __init__(self, name='I18MmLoader'):
        super(I18MmLoader, self).__init__(name)
        base = BaseI18MultiModalLoader()
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
        for key in [k for k in copy_keys if k != 'name']:
            if key != 'name':
                self.parameters[key] = inst.parameters[key]
        return list(copy_keys)

    def separate_params(self, keys):
        all_keys = list(self.dict.keys()) + keys
        new_dict = {}
        for key in [k for k in all_keys if k != 'name']:
            new_dict[key] = self.parameters[key]
        return new_dict

    @docstring_parameter(BaseI18MultiModalLoader.__doc__, xrd.__doc__,
                         stxm.__doc__, mon.__doc__, fluo.__doc__)
    def _override_class_docstring(self):
        """
        :param dataset_names: The names assigned to each dataset in the \
            order: fluorescence, diffraction, absorption, \
            monitor. Default: ['fluo', 'xrd', 'stxm', 'monitor'].

        {0} \n {1} \n {2} \n {3} \n {4}

        """
        pass

    def __set_names(self):
        fluo, xrd, stxm, monitor = self.parameters['dataset_names']
        self.name_dict = {'fluo': fluo, 'xrd': xrd, 'stxm': stxm,
                          'monitor': monitor}

    def setup(self):
        self.__set_names()
        self._data_loader(fluo(), 'fluo', self.fluo_keys)
        self._data_loader(xrd(), 'xrd', self.xrd_keys)
        self._data_loader(stxm(), 'stxm', self.stxm_keys)
        self._data_loader(mon(), 'monitor', self.mon_keys)

    def _data_loader(self, inst, name, key):
        debug_str = 'This file contains an ' + name
        warn_str = 'This file does not contain a ' + name
        try:
            inst.initialise(self.separate_params(key), self.exp)
            logging.debug(debug_str)
        except IndexError:
            logging.warning(warn_str)
        except:
            raise

    def final_parameter_updates(self):
        # names of individual datasets are not required
        self.delete_parameter_entry('name')
