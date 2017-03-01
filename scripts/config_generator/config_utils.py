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
.. module:: config_utils
   :platform: Unix
   :synopsis: Helper functions for the configurator commands.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""
import re
import sys

import savu.plugins.utils as pu
import arg_parsers as parsers


class DummyFile(object):
    def write(self, x): pass


def _redirect_stdout():
    save_stdout = sys.stdout
    sys.stdout = DummyFile()
    return save_stdout


def parse_args(function):
    def _parse_args_wrap_function(content, args):
        doc = function.__doc__
        parser = '%s_arg_parser' % function.__name__
        args = getattr(parsers, parser)(args.split(), doc)
        if not args:
            return content
        return function(content, args)
    return _parse_args_wrap_function


def _populate_plugin_list(content, pfilter=""):
    """ Populate the plugin list from a list of plugin instances. """
    content.plugin_list.plugin_list = []
    sorted_plugins = __get_filtered_plugins(pfilter)
    count = 0
    for key in sorted_plugins:
        content.add(key, str(count))
        count += 1


def __get_filtered_plugins(pfilter):
    """ Get a sorted, filter list of plugins. """
    key_list = []
    star_search = \
        pfilter.split('*')[0] if pfilter and '*' in pfilter else False

    for key, value in pu.plugins.iteritems():
        if star_search:
            search = '(?i)^' + star_search
            if re.match(search, value.__name__) or \
                    re.match(search, value.__module__):
                key_list.append(key)
        elif pfilter in value.__module__ or pfilter in value.__name__:
            key_list.append(key)

    key_list.sort()
    return key_list
