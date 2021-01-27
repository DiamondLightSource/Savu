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
.. module:: mutations
   :platform: Unix
   :synopsis: A dictionary detailing changes to plugins, actions and descriptions that are required by the configurator.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import textwrap
from colorama import Back, Fore
from . import display_formatter as df


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


def param_changes_str(plugin):
    return header('***CHANGES TO PARAMETERS IN %s***:' % plugin)


def replace_str(old_name, new_name):
    return wrap(auto_replace_str() + '\n%s has been replaced by %s. '
                'Please check the parameters.\n' % (old_name, new_name))


def rename_str(old_name, new_name):
    return wrap(auto_replace_str() + '%s has been renamed as %s. No '
                'further action required.' % (old_name, new_name))


def remove_str(name, reason):
    return wrap(auto_remove_str() + '%s %s' % (name, reason))


def notice_str(name, notice):
    return wrap(plugin_notice_str() + '%s %s' % (name, notice))


def param_change_str(old, new, plugin, keys):
    removed = list(set(old).difference(set(new)))
    added = list(set(new).difference(set(old)))
    replaced = [entry['old'] for k in keys for entry in param_mutations[k]['params']
                if entry['old'] in list(old.keys())]
    replacing = [entry['new'] for k in keys for entry in param_mutations[k]['params']
                 if entry['old'] in list(old.keys())]

    removed = [x for x in removed if x not in replaced]
    added = [x for x in added if x not in replacing]

    if len(removed + added + replaced) > 0:
        removed_str = ["Removing parameter %s" % r for r in removed]
        added_str = ["Adding parameter %s" % a for a in added]
        replaced_str = ["Replacing parameter %s with %s" % (
                replaced[i], replacing[i]) for i in range(len(replaced))]
        print(wrap(param_changes_str(plugin) + '%s' % (
                '\n'.join(removed_str + added_str + replaced_str))))

hdf5_notice = 'is now used by default.\nPlease remove from the process list, '\
    'unless you wish to override the default parameters (which must be done '\
    'individually for each dataset).'

dezing_notice = '\nA faster and more accurate version of DezingFilter is now'\
    ' available as Dezinger.'

distortion_notice = 'A new version of DistortionCorrection is available with'\
    ' the version available in 2.3 \nand below being renamed as '\
    'DistortionCorrectionDeprecated.  Please replace with \nthe new version.'

medianfilt_notice = '\nThis version of MedianFilter is now deprecated. Please'\
' replace with the newer faster versions - MedianFilter or MedianFilterGpu.'

dezinger_dep_notice ='is now deprecated.  Please replace with the new version'\
                    ' of Dezinger (or DezingerGPU).'

dezinger_notice = '\nDezinger plugin has been replaced with a new version, '\
    'please update the parameters.  '\
    '\nNB: Dezinger should now be applied to normalised data. A GPU version '\
    'DezingerGPU is also available.'


plugin_mutations = \
    {'TimeseriesFieldCorrections':
        {'replace': 'DarkFlatFieldCorrection',
         'desc': replace_str('TimeseriesFieldCorrections',
                             'DarkFlatFieldCorrection')},
     'Hdf5TomoSaver':
        {'replace': 'Hdf5Saver',
         'desc': replace_str('Hdf5TomoSaver', 'Hdf5Saver')},
     'DezingFilter':
        {'replace': 'DezingerSimple',
         'desc': rename_str('DezingFilter', 'DezingerSimple') + wrap(dezing_notice)},
     'SavuLoader':
        {'replace': 'SavuNexusLoader',
         'desc': replace_str('SavuLoader', 'SavuNexusLoader')},
     'DistortionCorrection':
        {'replace': 'DistortionCorrectionDeprecated',
         'up_to_version': '2.4', # if the plist version is less than 2.4 (or not defined) then apply this mutation
         'desc': '\n' + Fore.RED + auto_replace_str() + wrap(distortion_notice) + Fore.RESET},
     'MedianFilter':
        {'replace': 'MedianFilterDeprecated',
         'up_to_version': '3.0', # if the plist version is less than 3.0 (or not defined) then apply this mutation
         'desc': '\n' + Fore.RED + auto_replace_str() + wrap(medianfilt_notice) + Fore.RESET},
     'Dezinger':
        {'replace': 'Dezinger',
         'up_to_version': '3.0', # if the plist version is less than 3.0 (or not defined) then apply this mutation
         'desc': '\n' + Fore.RED + auto_replace_str() + wrap(dezinger_notice) + Fore.RESET},
      'DezingerSimple':
         {'replace': 'DezingerSimpleDeprecated',
          'up_to_version': '3.0', # if the plist version is less than 3.0 (or not defined) then apply this mutation
          'desc': '\n' + Fore.RED + auto_replace_str() + wrap("\nDezingerSimple " + dezinger_dep_notice) + Fore.RESET},
      'DezingerSinogram':
         {'replace': 'DezingerSinogramDeprecated',
          'up_to_version': '3.0', # if the plist version is less than 3.0 (or not defined) then apply this mutation
          'desc': '\n' + Fore.RED + auto_replace_str() + wrap("\nDezingerSinogram " + dezinger_dep_notice) + Fore.RESET}
     }

param_mutations = \
    {'BaseRecon': {'params': [{'old': 'center_of_rotation', 'new': 'centre_of_rotation'},
                   {'old': 'number_of_iterations', 'new': 'n_iterations'},
                   {'old': 'sino_pad', 'new': 'outer_pad'}],
                   'up_to_version': '2.4'},
     'AstraReconGpu': {'params': [{'old': 'reconstruction_type', 'new': 'algorithm'}],
                       'up_to_version': '2.4'},
     'AstraReconCpu': {'params': [{'old': 'reconstruction_type', 'new': 'algorithm'}],
                                  'up_to_version': '2.4'},
     'DistortionCorrection': {'params': [{'old': 'centre', 'new': 'centre_from_top', 'eval': 'val[0]'},
                              {'old': 'centre', 'new': 'centre_from_left', 'eval': 'val[1]'},
                              {'old': 'centre_x', 'new': 'centre_from_left'},
                              {'old': 'centre_y', 'new': 'centre_from_top'},
                              {'old': 'cod_from_left', 'new': 'centre_from_left'},
                              {'old': 'cod_from_top', 'new': 'centre_from_top'},
                              ], 'up_to_version': '2.4'}}

plugin_notices = \
    {'Hdf5Saver': {'desc': notice_str('Hdf5Saver', hdf5_notice)}, }
