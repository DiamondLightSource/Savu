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
.. module:: display_formatter
   :platform: Unix
   :synopsis: Classes for formatting plugin list output in the configurator.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import textwrap

from colorama import Fore, Back, Style


class DisplayFormatter(object):

    def __init__(self, plugin_list):
        self.plugin_list_inst = plugin_list
        self.plugin_list = plugin_list.plugin_list

    def _get_string(self, **kwargs):
        out_string = []
        verbosity = kwargs.get('verbose', False)
        level = kwargs.get('level', 'user')

        start = kwargs.get('start', 0)
        stop = kwargs.get('stop', len(self.plugin_list))
        if stop == -1:
            stop = len(self.plugin_list)

        count = start
        plugin_list = self.plugin_list[start:stop]
        for p_dict in plugin_list:
            count += 1
            description = \
                self._get_description(level, p_dict, count, verbosity)
            out_string.append(description)
        return '\n'.join(out_string)

    def _get_description(self, level, p_dict, count, verbose):
        width = 85
        if verbose == '-q':
            return self._get_quiet(p_dict, count, width)
        if not verbose:
            return self._get_default(level, p_dict, count, width)
        if verbose == '-v':
            return self._get_verbose(level, p_dict, count, width)
        if verbose == '-vv':
            return self._get_verbose_verbose(level, p_dict, count, width)

    def _get_plugin_title(self, p_dict, width, fore_colour, back_colour,
                          active="", quiet=False, pos=None):
        pos = "%2s" % (str(pos) + ")") if pos else ""
        title = "%s %s %s" % (active, pos, p_dict['name'])
        title = title if quiet else title+"(%s)" % p_dict['id']
        width -= len(title)
        return back_colour + fore_colour + title + " "*width + Style.RESET_ALL

    def _get_synopsis(self, plugin_name, width, colour_on, colour_off):
        doc_str = \
            self.plugin_list_inst._get_docstring_info(plugin_name)['synopsis']
        synopsis = \
            self._get_equal_lines(doc_str, width, colour_on, colour_off, " "*2)
        if not synopsis:
            return ''
        return "\n" + colour_on + synopsis + colour_off

    def _get_param_details(self, level, p_dict, width, desc=False):
        margin = 4
        keycount = 0
        joiner = "\n" + " "*margin
        params = ''

        all_keys = p_dict['data'].keys()
        if 'hide' in p_dict.keys():
            all_keys = [p for p in all_keys if p not in p_dict['hide']]

        user_keys = [p for p in all_keys if p in p_dict['user']]
        dev_keys = [p for p in all_keys if p not in p_dict['user']]

        if level == 'user':
            keys = user_keys
        else:
            keys = user_keys + dev_keys

        for key in keys:
            keycount += 1
            temp = "\n   %2i)   %20s : %s"
            # keycount = all_keys.index(key)+1
            params += temp % (keycount, key, p_dict['data'][key])
            if desc:
                pdesc = " ".join(desc[key].split())
                pdesc = joiner.join(textwrap.wrap(pdesc, width=width))
                temp = '\n' + Fore.CYAN + ' '*margin + "%s" + Fore.RESET
                params += temp % pdesc
        return params

    def _get_extra_info(self, p_dict, width, colour_off, info_colour,
                        warn_colour):
        extra_info = self.plugin_list_inst._get_docstring_info(p_dict['name'])
        info = self._get_equal_lines(extra_info['info'], width, info_colour,
                                     colour_off, " "*4)
        warn = self._get_equal_lines(extra_info['warn'], width, warn_colour,
                                     colour_off, " "*4)
        info = "\n"+info if info else ''
        warn = "\n"+warn if warn else ''
        return info, warn

    def _get_equal_lines(self, string, width, colour_on, colour_off, offset):
        if not string or not colour_on:
            return ''
        str_list = textwrap.wrap(string, width=width-len(offset))
        new_str_list = []
        for line in str_list:
            lwidth = width - len(line) - len(offset)
            new_str_list.append(
                colour_on + offset + line + " "*lwidth + colour_off)
        return "\n".join(new_str_list)


class DispDisplay(DisplayFormatter):

    def __init__(self, plugin_list):
        super(DispDisplay, self).__init__(plugin_list)

    def _get_quiet(self, p_dict, count, width, quiet=True):
        active = \
            '***OFF***' if 'active' in p_dict and not p_dict['active'] else ''
        pos = p_dict['pos'].strip() if 'pos' in p_dict.keys() else count
        fore = Fore.RED + Style.DIM if active else Fore.LIGHTWHITE_EX
        back = Back.LIGHTBLACK_EX
        return self._get_plugin_title(p_dict, width, fore, back,
                                      active=active, quiet=quiet, pos=pos)

    def _get_default(self, level, p_dict, count, width):
        title = self._get_quiet(p_dict, count, width)
        params = self._get_param_details(level, p_dict, width)
        return title + params

    def _get_verbose(self, level, p_dict, count, width, breakdown=False):
        title = self._get_quiet(p_dict, count, width, quiet=False)
        colour_on = Back.LIGHTBLACK_EX + Fore.LIGHTWHITE_EX
        colour_off = Back.RESET + Fore.RESET
        synopsis = \
            self._get_synopsis(p_dict['name'], width, colour_on, colour_off)
        params = \
            self._get_param_details(level, p_dict, width, desc=p_dict['desc'])
        if breakdown:
            return title, synopsis, params
        return title + synopsis + params

    def _get_verbose_verbose(self, level, p_dict, count, width):
        title, synopsis, param_details = \
            self.__get_verbose(level, p_dict, count, width, breakdown=True)
        info_c = Back.LIGHTBLACK_EX + Fore.LIGHTWHITE_EX
        warn_c = Back.RED + Fore.WHITE
        c_off = Back.RESET + Fore.RESET
        info, warn = self._get_extra_info(p_dict, width, c_off, info_c, warn_c)
        return title + synopsis + info + warn + param_details


class ListDisplay(DisplayFormatter):

    def __init__(self, plugin_list):
        super(ListDisplay, self).__init__(plugin_list)

    def _get_quiet(self, p_dict, count, width):
        return self._get_plugin_title(p_dict, width, Fore.RESET, Back.RESET,
                                      quiet=True)

    def _get_default(self, level, p_dict, count, width):
        title = self._get_quiet(p_dict, count, width)
        synopsis = \
            self._get_synopsis(p_dict['name'], 60, Fore.CYAN, Fore.RESET)
        return title + synopsis

    def _get_verbose(self, level, p_dict, count, width, breakdown=False):
        default_str = self._get_default(level, p_dict, count, width)
        info_c = Back.LIGHTBLACK_EX + Fore.LIGHTWHITE_EX
        c_off = Back.RESET + Fore.RESET
        info, warn = self._get_extra_info(p_dict, width, c_off, info_c, info_c)
        return default_str + info

    def _get_verbose_verbose(self, level, p_dict, count, width):
        all_params = self._get_param_details('all', p_dict, 100)
        default_str = self._get_default(level, p_dict, count, width)
        info_c = Back.LIGHTBLACK_EX + Fore.LIGHTWHITE_EX
        warn_c = Back.RED + Fore.WHITE
        c_off = Back.RESET + Fore.RESET
        info, warn = self._get_extra_info(p_dict, width, c_off, info_c, warn_c)
        return default_str + info + warn + all_params
