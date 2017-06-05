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

import textwrap
from colorama import Back
import display_formatter as df


def wrap(string):
    string = string.split('\n')
    final_str = []
    for s in string:
        final_str += textwrap.wrap(s, width=df.WIDTH)
    return '\n' + '\n'.join(final_str)


def header(string):
    return (Back.CYAN + string + Back.RESET + '\n')


def auto_replace_str():
    return header('***AUTO-REPLACEMENT NOTICE***:')


def auto_remove_str():
    return header('***AUTO-REMOVAL NOTICE***:')


def plugin_notice_str():
    return header('***PLUGIN NOTICE***:')


def replace_str(old_name, new_name):
    return wrap(auto_replace_str() + '\n%s has been replaced by %s. '
                '\nPlease check the parameters.\n' % (old_name, new_name))


def rename_str(old_name, new_name):
    return wrap(auto_replace_str() + '%s has been renamed as %s. \nNo '
                'further action required.' % (old_name, new_name))


def remove_str(name, reason):
    return wrap(auto_remove_str() + '%s %s' % (name, reason))


def notice_str(name, notice):
    return wrap(plugin_notice_str() + '%s %s' % (name, notice))


hdf5_notice = 'is now used by default.\nPlease remove from the process list, '\
    'unless you wish to override the default parameters (which must be done '\
    'individually for each dataset).'


plugin_mutations = \
    {'TimeseriesFieldCorrections':
        {'replace': 'DarkFlatFieldCorrection',
         'desc': replace_str('TimeseriesFieldCorrections',
                             'DarkFlatFieldCorrection')},
     'Hdf5TomoSaver':
        {'replace': 'Hdf5Saver',
         'desc': replace_str('Hdf5TomoSaver', 'Hdf5Saver')},
     }


param_mutations = \
    {'BaseRecon': {'old': 'center_of_rotation', 'new': 'centre_of_rotation'}}


plugin_notices = \
    {'Hdf5Saver': {'desc': notice_str('Hdf5Saver', hdf5_notice)}, }
