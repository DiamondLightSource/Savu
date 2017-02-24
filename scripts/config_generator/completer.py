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
.. module:: completer
   :platform: Unix
   :synopsis: completer class for the configurator

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import os
import re

from savu.plugins import utils as pu
if os.name == 'nt':
    import win_readline as readline
else:
    import readline

RE_SPACE = re.compile('.*\s+$', re.M)

list_commands = ['loaders', 'corrections', 'filters', 'reconstructions',
                 'savers']


class Completer(object):

    def __init__(self, commands):
        self.commands = commands

    def _listdir(self, root):
        "List directory 'root' appending the path separator to subdirs."
        res = []
        for name in os.listdir(root):
            path = os.path.join(root, name)
            if os.path.isdir(path):
                name += os.sep
            res.append(name)
        return res

    def _complete_path(self, path=None):
        "Perform completion of filesystem path."
        if not path:
            return self._listdir('.')
        dirname, rest = os.path.split(path)
        tmp = dirname if dirname else '.'
        res = [os.path.join(dirname, p)
               for p in self._listdir(tmp) if p.startswith(rest)]
        # more than one match, or single match which does not exist (typo)
        if len(res) > 1 or not os.path.exists(path):
            return res
        # resolved to a single directory, so return list of files below it
        if os.path.isdir(path):
            return [os.path.join(path, p) for p in self._listdir(path)]
        # exact file match terminates this completion
        return [path + ' ']

    def path_complete(self, args):
        if not args:
            return self._complete_path('.')
        # treat the last arg as a path and complete it
        return self._complete_path(args[-1])

    def complete_open(self, args):
        "Completions for the open commands."
        return self.path_complete(args)

    def complete_save(self, args):
        "Completions for the save commands."
        return self.path_complete(args)

    def complete_list(self, args):
        if not args[0]:
            return list_commands
        return [x for x in list_commands if x.startswith(args[0])]

    def complete_params(self, args):
        if not args[0]:
            return pu.plugins.keys()
        return [x for x in pu.plugins.keys() if x.startswith(args[0])]

    def complete(self, text, state):
        "Generic readline completion entry point."
        read_buffer = readline.get_line_buffer()
        line = readline.get_line_buffer().split()
        # show all commands
        if not line:
            return [c + ' ' for c in self.commands.keys()][state]
        # account for last argument ending in a space
        if RE_SPACE.match(read_buffer):
            line.append('')
        # resolve command to the implementation function
        cmd = line[0].strip()
        if cmd in commands.keys():
            impl = getattr(self, 'complete_%s' % cmd)
            args = line[1:]
            if args:
                return (impl(args) + [None])[state]
            return [cmd + ' '][state]
        results = [c + ' ' for c in self.commands.keys() if
                   c.startswith(cmd)] + [None]
        return results[state]
