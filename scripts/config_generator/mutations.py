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
.. module:: mutations.py
   :platform: Unix
   :synopsis: A dictionary detailing changes to plugins, actions and \
       descriptions that are required by the configurator.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

from colorama import Back


def auto_str():
    return ('\n' + Back.CYAN + '***AUTO-REPLACEMENT NOTICE***:' + Back.RESET)


def replace_str(old_name, new_name):
    return (auto_str() + '\n%s has been replaced by %s. '
            '\nPlease check the parameters.\n' % (old_name, new_name))


def rename_str(old_name, new_name):
    return (auto_str() + '\n%s has been renamed as %s. \nNo '
            'further action required.' % (old_name, new_name))

details = \
    {'TimeseriesFieldCorrections':
        {'replace' : 'DarkFlatFieldCorrection',
         'desc'    : replace_str('TimeseriesFieldCorrections',
                                 'DarkFlatFieldCorrection')},
     'Hdf5TomoSaver':
        {'replace'  : 'Hdf5Saver',
         'desc'     : rename_str('Hdf5TomoSaver', 'Hdf5Saver')},
     }
