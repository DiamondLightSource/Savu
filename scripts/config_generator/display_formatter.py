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
import os
import textwrap
import copy

from colorama import Fore, Back, Style

WIDTH = 85


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
        subelem = kwargs.get('subelem', None)
        if stop == -1:
            stop = len(self.plugin_list)

        count = start
        plugin_list = self.plugin_list[start:stop]
        line_break = ('%s' % ('-'*WIDTH))
        out_string.append(line_break)

        for p_dict in plugin_list:
            count += 1
            if subelem is not None:
                if subelem.isdigit():
                    sub_dict = self._select_param(p_dict, subelem, level)
                    p_dict = sub_dict
                    verbosity = '-vv'
                    level = 'all'
                else:
                    print('The sub element value was not an integer.')
            if p_dict is not None:
                description = \
                    self._get_description(WIDTH, level, p_dict, count, verbosity)
                out_string.append(description)
                out_string.append(line_break)
        return '\n'.join(out_string)

    def _select_param(self, temp_param_dict, subelem, level):
        """ Display sub element when specified in savu_config.

        Prevent mutable changes by copying the dict.
        """
        element_present = False
        keycount = 0

        param_dict = copy.deepcopy(temp_param_dict)

        # Select the correct order of parameters according to that on display
        # to the user. This ensures the correct parameter is modified.
        dev_keys = [k for k, v in param_dict['tools'].items()
                    if v['visibility'] not in ['user', 'hide']]
        user_keys = [k for k, v in param_dict['tools'].items()
                     if v['visibility'] == 'user']
        keys = user_keys + dev_keys

        try:
            for key in keys:
                keycount += 1
                if int(subelem) == int(keycount):
                    element_present = True
                    for i in list(param_dict['tools']):
                        if i != key:
                            param_dict['tools'][i]['visibility'] = 'hide'

            if element_present is False:
                print('No matching sub element number found.')
                return None
            return param_dict

        except Exception as e:
            print('ERROR: ' + str(e))
            raise

    def _get_description(self, width, level, p_dict, count, verbose):
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
        title = title if quiet else title+" (%s)" % p_dict['id']
        width -= len(title)
        return back_colour + fore_colour + title + " "*width + Style.RESET_ALL

    def _get_synopsis(self, p_dict, width, colour_on, colour_off):
        doc_str = p_dict['doc']
        synopsis = \
            self._get_equal_lines(doc_str['synopsis'], width, colour_on, colour_off, " "*2)
        if not synopsis:
            return ''
        return "\n" + colour_on + synopsis + colour_off

    def _get_verbose_param_details(self, p_dict, param_key, desc, key,
                                   params, width):
        margin = 4
        joiner = "\n" + " " * margin
        if param_key == 'verbose':
            verbose = desc[key][param_key]
            # Account for margin space
            verbose = joiner.join(textwrap.wrap(verbose,
                                                width=width - margin))
            temp = joiner + Fore.GREEN + "%s" + Fore.RESET
            params += temp % verbose

        if param_key == 'range':
            p_range = desc[key]['range']
            if p_range:
                try:
                    p_range = joiner.join(textwrap.wrap(p_range,
                                                        width=width - margin))
                    temp = joiner + Fore.MAGENTA + "%s" + Fore.RESET
                    params += temp % p_range
                except TypeError:
                    print('You have not filled in the %s field within the'
                          ' yaml information.' % param_key)

        return params

    def _get_param_details(self, level, p_dict, width, desc=False,
                           breakdown=False):
        margin = 4
        keycount = 0
        joiner = "\n" + " "*margin
        params = ''

        dev_keys = [k for k, v in p_dict['tools'].items()
                    if v['visibility'] not in ['user', 'hide']]
        user_keys = [k for k, v in p_dict['tools'].items()
                     if v['visibility'] == 'user']

        try:
            keys = user_keys if level == 'user' else user_keys + dev_keys

            for key in keys:
                keycount += 1
                temp = "\n   %2i)   %20s : %s"
                params += temp % (keycount, key, p_dict['data'][key])
                # Add description for this parameter
                if desc:
                    params = self._append_description(desc, key, p_dict, joiner, width,
                                                      margin, params, breakdown)
            return params
        except Exception as e:
            print('ERROR: ' + str(e))
            raise

    def _append_description(self, desc, key, p_dict, joiner, width, margin,
                            params, breakdown):
        if isinstance(desc[key], str):
            pdesc = " ".join(desc[key].split())
            # Restrict the margin so that the lines don't overflow.
            pdesc = joiner.join(textwrap.wrap(pdesc, width=width - margin))
            temp = joiner + Fore.CYAN + "%s" + Fore.RESET
            params += temp % pdesc
        elif isinstance(desc[key], dict):
            required_keys = desc[key].keys()
            for param_key in required_keys:
                # desc[key][param_key] is the value at this parameter
                if param_key == 'summary':
                    pdesc = desc[key][param_key]
                    pdesc = joiner.join(textwrap.wrap(pdesc,
                                                      width=width - margin))
                    temp = joiner + Fore.CYAN + "%s" + Fore.RESET
                    params += temp % pdesc

                if breakdown:
                    params = self._get_verbose_param_details(p_dict, param_key,
                                                             desc, key, params, width)

        options = p_dict['tools'][key].get('options')
        if options:
            option_text = Fore.BLUE + 'Options:'
            option_text = joiner.join(textwrap.wrap(option_text,
                                                    width=width - margin))
            temp = joiner + "%s"
            params += temp % option_text
            for opt in options:
                opt = self._apply_lower_case(opt)
                current_opt = self._apply_lower_case(p_dict['data'][key])
                if current_opt == opt:
                    colour = Fore.LIGHTCYAN_EX
                    verbose_color = Fore.LIGHTCYAN_EX
                else:
                    colour = Fore.BLUE
                    verbose_color = Fore.GREEN
                option_verbose = ''
                option_verbose += colour + u'\u0009' + u'\u2022' + opt

                if isinstance(desc[key][param_key], dict):
                    # If there are option descriptions present
                    options_desc = {self._apply_lower_case(k): v
                                    for k, v in desc[key][param_key].items() if v}
                    if opt in options_desc.keys():
                        if breakdown:
                            option_verbose += ': ' + verbose_color + options_desc[opt]
                            option_verbose = joiner.join(textwrap.wrap(option_verbose,
                                                         width=width - margin))
                temp = joiner + "%s" + Fore.RESET
                params += temp % option_verbose

        return params

    def _apply_lower_case(self, item):
        return item.lower() if isinstance(item, str) else item

    def _get_extra_info(self, p_dict, width, colour_off, info_colour,
                        warn_colour):
        doc_str = p_dict['doc']
        info = self._get_equal_lines(doc_str['info'], width, info_colour,
                                     colour_off, " "*2)
        warn = self._get_equal_lines(doc_str['warn'], width, warn_colour,
                                     colour_off, " "*2)
        info = "\n"+info if info else ''
        warn = "\n"+warn if warn else ''
        return info, warn

    def _get_equal_lines(self, string, width, colour_on, colour_off, offset):
        if not string or not colour_on:
            return ''
        string = str.splitlines(string)
        str_list = []
        for s in string:
            str_list += textwrap.wrap(s, width=width-len(offset))
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
        p_dict['data'] = self._remove_quotes(p_dict['data'])
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
            self._get_synopsis(p_dict, width, colour_on, colour_off)
        param_desc = {k: v['description'] for k, v in p_dict['tools'].items()}
        params = \
            self._get_param_details(level, p_dict, width, desc=param_desc)
        if breakdown:
            params = \
                self._get_param_details(level, p_dict, width, desc=param_desc,
                                        breakdown=breakdown)
            return title, synopsis, params
        return title + synopsis + params

    def _get_verbose_verbose(self, level, p_dict, count, width):
        title, synopsis, param_details = \
            self._get_verbose(level, p_dict, count, width, breakdown=True)
        info_c = Back.CYAN + Fore.LIGHTWHITE_EX
        warn_c = Back.WHITE + Fore.RED
        c_off = Back.RESET + Fore.RESET
        info, warn = self._get_extra_info(p_dict, width, c_off, info_c, warn_c)
        # Synopsis and get_extra info both call plugin instance and populate
        # parameters which means yaml_load will be called twice
        return title + synopsis + info + warn + param_details

    def _remove_quotes(self, data_dict):
        """ Remove quotes around variables for display
        """
        for key, val in data_dict.iteritems():
            val = str(val).replace("'", "")
            data_dict[key] = val
        return data_dict

    def _notices(self):
        width = 86
        warnings = self.get_warnings(width)
        if warnings:
            notice = Back.RED + Fore.WHITE + "IMPORTANT PLUGIN NOTICES" +\
                Back.RESET + Fore.RESET + "\n"
            border = "*"*width + '\n'
            print (border + notice + warnings + '\n'+border)

    def get_warnings(self, width):
        # remove display styling outside of this class
        colour = Back.RESET + Fore.RESET
        warnings = []
        names = []
        for plugin in self.plugin_list:
            if plugin['name'] not in names:
                names.append(plugin['name'])
                warn = plugin['doc']['warn']
                if warn:
                    for w in warn.split('\n'):
                        string = plugin['name'] + ": " + w + '.'
                        warnings.append(self._get_equal_lines(
                            string, width-1, colour, colour, " "*2))
        return "\n".join(
            ["*" + "\n ".join(w.split('\n')) for w in warnings if w])


class ListDisplay(DisplayFormatter):

    def __init__(self, plugin_list):
        super(ListDisplay, self).__init__(plugin_list)

    def _get_quiet(self, p_dict, count, width):
        return self._get_plugin_title(p_dict, width, Fore.RESET, Back.RESET,
                                      quiet=True)

    def _get_default(self, level, p_dict, count, width):
        title = self._get_quiet(p_dict, count, width)
        synopsis = \
            self._get_synopsis(p_dict, width, Fore.CYAN, Fore.RESET)
        return title + synopsis

    def _get_verbose(self, level, p_dict, count, width, breakdown=False):
        default_str = self._get_default(level, p_dict, count, width)
        info_c = Fore.CYAN
        c_off = Back.RESET + Fore.RESET
        info, warn = self._get_extra_info(p_dict, width, c_off, info_c, info_c)
        return default_str + info

    def _get_verbose_verbose(self, level, p_dict, count, width):
        all_params = self._get_param_details('all', p_dict, 100)
        default_str = self._get_default(level, p_dict, count, width)
        info_c = Fore.CYAN
        warn_c = Fore.RED
        c_off = Back.RESET + Fore.RESET
        info, warn = self._get_extra_info(p_dict, width, c_off, info_c, warn_c)
        return default_str + info + warn + all_params
