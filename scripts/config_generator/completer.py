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
    from . import win_readline as readline
else:
    import readline

RE_SPACE = re.compile('.*\s+$', re.M)


class Completer(object):

    def __init__(self, commands, plugin_list=[]):
        self.commands = commands
        self.plugin_list = plugin_list
        self.matches = None

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
        "Completions for the list commands."
        list_args = [c.strip() for c in self._get_collections()]
        list_args += self.plugin_list
        if not args[0]:
            return list_args
        return [x for x in list_args if x.lower().startswith(args[0].lower())]

    def complete_add(self, args):
        "Completions for the add commands."
        list_args = self.plugin_list
        if not args[0] or len(args) == 2:
            return list_args
        return [x for x in list_args if x.lower().startswith(args[0].lower())]

    def complete_level(self, args):
        "Completions for the level command."
        levels = ['basic', 'intermediate', 'advanced']
        return [l for l in levels if l.lower().startswith(args[0].lower())]

    def _get_collections(self):
        """ Get plugin collection names. """
        import savu.plugins as plugins
        import copy

        path = plugins.__path__[0]
        exclude_dir = ['driver', 'utils', '__pycache__']
        arrow = ' ==> '
        for root, dirs, files in os.walk(path):
            depth = root.count(os.path.sep) - path.count(os.path.sep)
            dirs[:] = [d for d in dirs if d not in exclude_dir]
            if depth == 0:
                colls = copy.copy(dirs)
            else:
                sep = '' if depth == 1 else ' ' + arrow if depth == 2 else \
                    (depth-2)*6*' ' + arrow
                pos = colls.index(sep + os.path.basename(root)) + 1
                sep = ' ' + arrow if depth == 1 else (depth-1)*6*' ' + arrow
                for i in range(len(dirs)):
                    colls.insert(pos, sep + dirs[i])
                    pos += 1
        return colls

    def complete_params(self, args):
        if not args[0]:
            return list(pu.plugins.keys())
        return [x for x in list(pu.plugins.keys()) if x.startswith(args[0])]

    def complete(self, text, state):
        "Generic readline completion entry point."
        if state == 0:
            self.matches = self.__get_matches(readline.get_line_buffer())
        return self.matches[state]

    def __get_matches(self, read_buffer):
        # show all commands
        line = readline.get_line_buffer().split()
        if not line:
            return [c + ' ' for c in list(self.commands.keys())]
        else:
            # account for last argument ending in a space
            if RE_SPACE.match(read_buffer):
                line.append('')

            # resolve command to the implementation function
            cmd = line[0].strip()
            if cmd in list(self.commands.keys()):
                impl = getattr(self, 'complete_%s' % cmd)
                args = line[1:]
                if args:
                    return (impl(args) + [None])
                return [cmd + ' ']
            return [c + ' ' for c in list(self.commands.keys()) if
                    c.startswith(cmd)] + [None]
