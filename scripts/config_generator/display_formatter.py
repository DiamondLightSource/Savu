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

from savu.plugins import utils as pu
import savu.data.framework_citations as fc
from savu.data.plugin_list import CitationInformation


WIDTH = 85


class DisplayFormatter(object):
    def __init__(self, plugin_list):
        self.plugin_list_inst = plugin_list
        self.plugin_list = plugin_list.plugin_list

    def _get_string(self, **kwargs):
        out_string = []
        verbosity = kwargs.get("verbose", False)
        level = kwargs.get("current_level", "basic")
        datasets = kwargs.get("datasets", False)
        expand_dim = kwargs.get("expand_dim", None)

        start = kwargs.get("start", 0)
        stop = kwargs.get("stop", len(self.plugin_list))
        subelem = kwargs.get("subelem", False)

        if stop == -1:
            stop = len(self.plugin_list)

        count = start
        plugin_list = self.plugin_list[start:stop]
        line_break = "%s" % ("-" * WIDTH)
        out_string.append(line_break)

        display_args = {"subelem": subelem, "datasets": datasets,
                        "expand_dim": expand_dim}
        for p_dict in plugin_list:
            count += 1
            description = self._get_description(
                WIDTH, level, p_dict, count, verbosity, display_args
            )
            out_string.append(description)
            out_string.append(line_break)
        return "\n".join(out_string)

    def _get_description(
        self, width, level, p_dict, count, verbose, display_args
    ):
        if verbose == "-q":
            return self._get_quiet(p_dict, count, width)
        if not verbose:
            return self._get_default(
                level, p_dict, count, width, display_args
            )
        if verbose == "-v":
            return self._get_verbose(
                level, p_dict, count, width, display_args
            )
        if verbose == "-vv":
            return self._get_verbose_verbose(
                level, p_dict, count, width, display_args
            )

    def _get_plugin_title(self, p_dict, width, fore_colour, back_colour,
                          active="", quiet=False, pos=None):
        pos = "%2s" % (str(pos) + ")") if pos else ""
        title = "%s %s %s" % (active, pos, p_dict["name"])
        title = title if quiet else title + " (%s)" % p_dict["id"]
        width -= len(title)
        return (
            back_colour + fore_colour + title + " " * width + Style.RESET_ALL
        )

    def _get_quiet(self, p_dict, count, width, quiet=True):
        active = (
            "***OFF***" if "active" in p_dict and not p_dict["active"] else ""
        )
        p_dict["data"] = self._remove_quotes(p_dict["data"])
        pos = p_dict["pos"].strip() if "pos" in list(p_dict.keys()) else count
        fore = Fore.RED + Style.DIM if active else Fore.LIGHTWHITE_EX
        back = Back.LIGHTBLACK_EX
        return self._get_plugin_title(
            p_dict, width, fore, back, active=active, quiet=quiet, pos=pos
        )

    def _get_synopsis(self, p_dict, width, colour_on, colour_off):
        doc_str = p_dict["doc"]
        synopsis = self._get_equal_lines(
            doc_str.get("synopsis"), width, colour_on, colour_off, " " * 2
        )
        return "\n" + synopsis

    def _get_extra_info(self, p_dict, width, colour_off, info_colour,
                        warn_colour):
        doc_str = p_dict["doc"]
        info = self._get_equal_lines(doc_str.get("info"), width, info_colour,
                                     colour_off, " " * 2)
        info = "\n"+info if info else ''

        doc_link = doc_str.get("documentation_link")
        if doc_link:
            documentation_link = self._get_equal_lines(doc_link, width,
                                            info_colour, colour_off, " " * 2)
            info +="\n"+documentation_link

        warn = self._get_equal_lines(doc_str.get('warn'), width, warn_colour,
                                     colour_off, " "*2)
        warn = "\n"+warn if warn else ""
        return info, warn

    def _get_equal_lines(self, string, width, colour_on, colour_off, offset,
                         option_colour=False):
        """ Format the input string so that it is the width specified.
        Surround the string with provided colour.
        """
        if not string or not colour_on:
            return ""
        # Call method directly for split to be used with string and unicode
        string = string.splitlines()
        str_list = []
        for s in string:
            str_list += textwrap.wrap(s, width=width - len(offset))
        new_str_list = []
        if option_colour:
            # Alternate colour choice and doesn't colour the full width
            new_str_list = self._get_option_format(str_list, width,
                            colour_on, colour_off, offset, option_colour,
                            new_str_list)
        else:
            # Fill the whole line with the colour
            for line in str_list:
                lwidth = width - len(line) - len(offset)
                new_str_list.append(
                    colour_on + offset + line + " " * lwidth + colour_off)
        return "\n".join(new_str_list)

    def _remove_quotes(self, data_dict):
        """Remove quotes around variables for display"""
        for key, val in data_dict.items():
            val = str(val).replace("'", "")
            data_dict[key] = val
        return data_dict


class ParameterFormatter(DisplayFormatter):
    def __init__(self, plugin_list):
        super(ParameterFormatter, self).__init__(plugin_list)

    def _get_param_details(self, level, p_dict, width,
                           desc=False, breakdown=False):
        """ Return a list of parameters organised by visibility level

        :param level: The visibility level controls which parameters the
           user can see
        :param p_dict: Parameter dictionary for one plugin
        :param width: The terminal display width for output string
        :param desc: The description for use later on within the display
          formatter
        :param breakdown: Boolean True if the verbose verbose information
          should be shown
        :return: List of parameters in order
        """
        params = ""
        keycount = 0
        # Return the list of parameters according to the visibility level
        keys = pu.set_order_by_visibility(p_dict["param"], level=level)
        try:
            for key in keys:
                keycount += 1
                params = self._create_display_string(desc, key, p_dict,
                                                     params, keycount, width, breakdown)
            return params
        except Exception as e:
            print("ERROR: " + str(e))
            raise

    def _create_display_string(self, desc, key, p_dict, params, keycount,
                               width, breakdown, expand_dim=None):
        margin = 6
        str_margin = " " * margin
        temp = "\n   %2i)   %29s : %s"
        val = p_dict["data"][key]
        if key == "preview" and expand_dim is not None:
            val = pu._dumps(val)
            if expand_dim == "all":
                val = self._preview_output(val, width, self._get_dimensions(val))
            else:
                pu.check_valid_dimension(expand_dim, val)
                val = self._dim_slice_output(val, width, expand_dim)
        params += temp % (keycount, key, val)
        if desc:
            params = self._append_description(desc, key, p_dict, str_margin,
                                              width, params, breakdown)
        return params

    def _get_dimensions(self, preview_list):
        """ Check how many dimensions to display

        :param preview_list: The preview parameter
        :return: Dimensions to display
        """
        return 1 if not preview_list else len(preview_list)

    def _preview_output(self, preview, width, dims):
        """ Compile output string lines for preview syntax"""
        temp_str = ""
        for dim in range(1, dims + 1):
            temp_str += self._dim_slice_output(preview, width, dim)
        return temp_str

    def _dim_slice_output(self, preview_list, width, dims):
        """Compile the string lines for dimension and slice notation syntax"""
        temp_str = ""
        # If there are multiple values in list format
        # Only show the values for the dimensions chosen
        if not preview_list:
            # If empty
            preview_display_value = ":"
        else:
            preview_display_value = preview_list[dims - 1]

        prev_val = self._set_syntax(preview_display_value)
        temp_str += f"\n   {'dim' + str(dims): >37} : "
        temp_str += self._get_slice_notation_info(prev_val, width)

        return temp_str

    def _get_slice_notation_info(self, val, width):
        """Create a string for certain slice notation information,
        start:stop:step (and chunk if provided)

        :param val: The value to be displayed
        :param width: The console text width
        :return: String containing split notation to display
        """
        import itertools
        basic_split_keys = ["start", "stop", "step"]
        all_split_keys = [*basic_split_keys, "chunk"]
        split_str = ""

        if pu.is_slice_notation(val):
            val_list = val.split(":")
            if len(val_list) < 3:
                # Make sure the start stop step split keys are always shown,
                # even when blank
                val_list.append('')
            for slice_name, v in zip(all_split_keys, val_list):
                # Only print up to the shortest list.
                # (Only show the chunk value if it is in val_list)
                split_str += self._get_slice_str(slice_name, v, width)
        else:
            # Display the first value as 'start', keep stop and step blank
            val_list = [val]
            for slice_name, v in itertools.zip_longest(basic_split_keys,
                                                       val_list, fillvalue=""):
                split_str += self._get_slice_str(slice_name, v, width)

        return split_str

    def _get_slice_str(self, label, value, width):
        """Create a string to display information

        :param label: The label to describe the value
        :param val: The value to be displayed
        :param width: The console text width
        :return: A string with a "label: value" format
        """
        margin = 6
        str_margin = " " * margin

        style_on = Style.BRIGHT
        style_off = Style.RESET_ALL

        split_line_str = f"{label: >39} : {value}"
        split_text = self._get_equal_lines(
            split_line_str, width, style_off, style_off, str_margin
        )
        return "\n" + split_text

    def _set_syntax(self, val):
        """ Remove additional spaces, replace colon for 'all' """
        if isinstance(val, str):
            if pu.is_slice_notation(val):
                if val == ":":
                    val = ""
                else:
                    val = val.strip()
            else:
                val = val.strip()
        return val


class DispDisplay(ParameterFormatter):
    def __init__(self, plugin_list):
        super(DispDisplay, self).__init__(plugin_list)

    def _get_default(self, level, p_dict, count, width, display_args=False):
        title = self._get_quiet(p_dict, count, width)
        params = self._get_param_details(level, p_dict, width, display_args)
        return title + params

    def _get_param_details(self, level, p_dict, width, display_args=False,
                           desc=False, breakdown=False):
        """
        Return a list of parameters organised by visibility level

        :param level: The visibility level controls which parameters the
           user can see
        :param p_dict: Parameter dictionary for one plugin
        :param width: The terminal display width for output strings
        :param display_args: A dictionary with subelem and datasets.
          This filters the visible parameters again. If subelem is chosen,
          only that one parameter is shown (this is useful when ONE parameter
          is modified in the terminal). If datasets is chosen, ONLY the
          in/out dataset parameters are shown
        :param desc: The description for use later on within the display
          formatter
        :param breakdown: Boolean True if the verbose verbose information
          should be shown
        :return: List of parameters in order
        """
        # Check if the parameters need to be filtered
        subelem = display_args.get("subelem")
        datasets = display_args.get("datasets")
        expand_dim = display_args.get("expand_dim")

        level = level if not (subelem or datasets) else False
        # Return the list of parameters according to the visibility level
        # unless a subelement or dataset choice is specified
        keys = pu.set_order_by_visibility(p_dict["param"], level=level)

        filter = subelem if subelem else datasets
        filter_items = [pu.param_to_str(subelem, keys)] \
                        if subelem else ["in_datasets", "out_datasets"]
        # If datasets parameter specified, only show these
        params = ""
        keycount = 0
        try:
            for key in keys:
                keycount += 1
                if filter:
                    if key in filter_items:
                        params = self._create_display_string(desc, key,
                                       p_dict, params, keycount, width,
                                       breakdown, expand_dim)
                else:
                    params = self._create_display_string(desc, key, p_dict,
                                        params, keycount, width, breakdown,
                                        expand_dim)
            return params
        except Exception as e:
            print("ERROR: " + str(e))
            raise

    def _get_verbose(
        self, level, p_dict, count, width, display_args, breakdown=False
    ):
        title = self._get_quiet(p_dict, count, width, quiet=False)
        colour_on = Back.LIGHTBLACK_EX + Fore.LIGHTWHITE_EX
        colour_off = Back.RESET + Fore.RESET
        synopsis = self._get_synopsis(p_dict, width, colour_on, colour_off)
        param_desc = {k: v["description"] for k, v in p_dict["param"].items()}
        params = self._get_param_details(
            level, p_dict, width, display_args, desc=param_desc
        )
        if breakdown:
            params = self._get_param_details(
                level,
                p_dict,
                width,
                display_args,
                desc=param_desc,
                breakdown=breakdown,
            )
            return title, synopsis, params
        return title + synopsis + params

    def _get_verbose_verbose(self, level, p_dict, count, width, display_args):
        title, synopsis, param_details = self._get_verbose(
            level, p_dict, count, width, display_args, breakdown=True
        )
        info_c = Back.CYAN + Fore.LIGHTWHITE_EX
        warn_c = Style.RESET_ALL + Fore.RED
        c_off = Back.RESET + Fore.RESET
        info, warn = self._get_extra_info(
            p_dict, width, c_off, info_c, warn_c
        )
        # Synopsis and get_extra info both call plugin instance and populate
        # parameters which means yaml_load will be called twice
        return title + synopsis + info + warn + param_details

    def _notices(self):
        width = 86
        warnings = self.get_warnings(width)
        if warnings:
            notice = (
                Back.RED
                + Fore.WHITE
                + "IMPORTANT PLUGIN NOTICES"
                + Back.RESET
                + Fore.RESET
                + "\n"
            )
            border = "*" * width + "\n"
            print((border + notice + warnings + "\n" + border))

    def get_warnings(self, width):
        # remove display styling outside of this class
        colour = Back.RESET + Fore.RESET
        warnings = []
        names = []
        for plugin in self.plugin_list:
            if plugin["name"] not in names:
                names.append(plugin["name"])
                doc_str = plugin["doc"]
                warn = doc_str.get("warn")
                if warn:
                    for w in warn.split("\n"):
                        string = plugin["name"] + ": " + w
                        warnings.append(
                            self._get_equal_lines(
                                string, width - 1, colour, colour, " " * 2
                            )
                        )
        return "\n".join(
            ["*" + "\n ".join(w.split("\n")) for w in warnings if w]
        )

    def _append_description(self, desc, key, p_dict, str_margin, width,
                            params, breakdown):
        c_off = Back.RESET + Fore.RESET
        description_verbose = False
        description_keys = ""
        if isinstance(desc[key], str):
            pdesc = " ".join(desc[key].split())
            pdesc = self._get_equal_lines(
                pdesc, width, Fore.CYAN, Fore.RESET, str_margin
            )
            params += "\n" + pdesc
        elif isinstance(desc[key], dict):
            description_keys = desc[key].keys()
            for param_key in description_keys:
                if param_key == "summary":
                    pdesc = desc[key][param_key]
                    pdesc = self._get_equal_lines(
                        pdesc, width, Fore.CYAN, Fore.RESET, str_margin
                    )
                    params += "\n" + pdesc

                if breakdown:
                    params = self._get_verbose_param_details(
                        p_dict, param_key, desc, key, params, width
                    )
                    description_verbose = True

        options = p_dict["param"][key].get("options")
        if options:
            option_text = "Options:"
            option_text = self._get_equal_lines(
                option_text, width, Fore.BLUE, Fore.RESET, str_margin
            )
            params += "\n" + option_text
            for opt in options:
                current_opt = p_dict["data"][key]
                option_verbose = \
                    self._get_verbose_option_string(opt, current_opt,
                            description_keys, description_verbose,
                            desc, key, c_off, width, str_margin)

                temp = "\n" + "%s" + c_off + Style.RESET_ALL
                params += temp % option_verbose

        return params

    def _get_verbose_option_string(self, opt, current_opt, description_keys,
                                   description_verbose, desc, key, c_off,
                                   width, str_margin):
        """ Get the option description string and correctly format it """
        colour, v_colour = self._get_verbose_option_colours(opt, current_opt)
        unicode_bullet_point = "\u2022"
        opt_margin = str_margin + (2 * " ")
        if (description_verbose is True) and ("options" in description_keys):
            # If there are option descriptions present
            options_desc = {k: v
                            for k, v in desc[key]["options"].items()
                            if v}
            if opt in options_desc.keys():
                # Append the description
                opt_d = unicode_bullet_point + str(opt) + ": " \
                        + options_desc[opt]
            else:
                # No description if the field is blank
                opt_d = unicode_bullet_point + str(opt) + ": "
            option_verbose = "\n" + opt_d
            option_verbose = \
                self._get_equal_lines(option_verbose,
                                       width, v_colour, c_off,
                                       opt_margin, option_colour=colour)
        else:
            option_verbose = unicode_bullet_point + str(opt)
            option_verbose = \
                self._get_equal_lines(option_verbose,
                                       width, colour, c_off, opt_margin,
                                       option_colour=colour)
        return option_verbose

    def _get_verbose_option_colours(self, opt, current_opt):
        """Set the colour of the option text

        :param opt: Option string
        :param current_opt: The curently selected option value
        :return: colour, verbose_color
        """
        if current_opt == opt:
            # Highlight the currently selected option by setting a
            # background colour and white text
            colour = Back.BLUE + Fore.LIGHTWHITE_EX
            verbose_color = Back.BLACK + Fore.LIGHTWHITE_EX
        else:
            # Make the option bold using Style.BRIGHT
            colour = Fore.BLUE + Style.BRIGHT
            # Remove bold style for the description
            verbose_color = Style.RESET_ALL + Fore.BLACK
        return colour, verbose_color

    def _get_verbose_param_details(
        self, p_dict, param_key, desc, key, params, width
    ):
        margin = 6
        str_margin = " " * margin
        if param_key == "verbose":
            verbose = desc[key][param_key]
            # Account for margin space
            style_on = Fore.CYAN + "\033[3m"
            style_off = Fore.RESET + "\033[0m"
            verbose = self._get_equal_lines(
                verbose, width, style_on, style_off, str_margin
            )
            params += "\n" + verbose

        if param_key == "range":
            p_range = desc[key][param_key]
            if p_range:
                try:
                    r_color = Fore.MAGENTA
                    r_off = Fore.RESET
                    p_range = self._get_equal_lines(
                        p_range, width, r_color, r_off, str_margin
                    )
                    params += "\n" + p_range
                except TypeError:
                    print(f"You have not filled in the {param_key} field "
                          f"within the yaml information.")
        return params

    def _get_option_format(self, str_list, width, colour_on, colour_off,
                           offset, option_colour, new_str_list):
        """ Special format for the options list """
        count = 0
        for line in str_list:
            lwidth = width - len(line) - len(offset)
            count += 1
            if count == 1:
                """At the first line, split the key so that it's colour is
                different. This is done here so that I keep the key and
                value on the same line.
                I have not passed in the unicode colour before this
                point as the textwrap does not take unicode into
                account when calculating the final string width.
                """
                if ":" in line:
                    option_text = line.split(":")[0]
                    opt_descr_text = line.split(":")[1]
                    line = (
                        option_colour
                        + option_text
                        + ":"
                        + colour_on
                        + opt_descr_text
                    )
                    new_str_list.append(
                        offset + line + colour_off + " " * lwidth
                    )
                else:
                    # Assumes that the option string is one line, the length
                    # of the width
                    new_str_list.append(
                        offset
                        + option_colour
                        + line
                        + colour_off
                        + " " * lwidth
                    )
            else:
                new_str_list.append(
                    offset + colour_on + line + colour_off + " " * lwidth
                )
        return new_str_list


class ListDisplay(ParameterFormatter):
    def __init__(self, plugin_list):
        super(ListDisplay, self).__init__(plugin_list)

    def _get_quiet(self, p_dict, count, width):
        return self._get_plugin_title(
            p_dict, width, Fore.RESET, Back.RESET, quiet=True
        )

    def _get_default(self, level, p_dict, count, width, display_args=False):
        title = self._get_quiet(p_dict, count, width)
        synopsis = self._get_synopsis(p_dict, width, Fore.CYAN, Fore.RESET)
        return title + synopsis

    def _get_verbose(self, level, p_dict, count, width, display_args,
                     breakdown=False):
        default_str = self._get_default(level, p_dict, count, width)
        info_c = Fore.CYAN
        c_off = Back.RESET + Fore.RESET
        info, warn = self._get_extra_info(
            p_dict, width, c_off, info_c, info_c
        )
        return default_str + info

    def _get_verbose_verbose(self, level, p_dict, count, width, display_args):
        all_params = self._get_param_details("all", p_dict, 100)
        default_str = self._get_default(level, p_dict, count, width)
        info_c = Fore.CYAN
        warn_c = Fore.RED
        c_off = Back.RESET + Fore.RESET
        info, warn = self._get_extra_info(
            p_dict, width, c_off, info_c, warn_c
        )
        return default_str + info + warn + all_params


class CiteDisplay(DisplayFormatter):
    def __init__(self, plugin_list):
        super(CiteDisplay, self).__init__(plugin_list)

    def _get_default(self, level, p_dict, count, width, display_args=False):
        """Find the citations and print them. Only display citations
        if they are required. For example, if certain methods are being
        used.
        """
        title = self._get_quiet(p_dict, count, width)
        citation = self._get_citation_str(p_dict["tools"].get_citations(),
                                          width,
                                          parameters=p_dict["data"])
        framework_citations = self._get_framework_citations(width)
        return framework_citations + title + citation

    def _get_citation_str(self, citation_dict, width, parameters=""):
        """Get the plugin citation information

        :param: citation_dict: Dictionay containing citation information
        :param parameters: Dictionary containing parameter information
        :param width: The terminal display width for output strings
        :return: cite, A string containing plugin citations
        """
        margin = 6
        str_margin = " " * margin
        line_break = "\n" + str_margin + "-" * (width - margin) + "\n"
        cite = ""
        if citation_dict:
            for citation in citation_dict.values():
                if citation.dependency and parameters:
                    # If the citation is dependent upon a certain parameter
                    # value being chosen
                    str_dep = self._get_citation_dependency_str(
                        citation, parameters, width, str_margin
                    )
                    if str_dep:
                        cite += line_break + str_dep + "\n" \
                                + self._get_citation_lines(citation,
                                                           width,
                                                           str_margin)
                else:
                    cite += line_break \
                            + self._get_citation_lines(citation,
                                                       width, str_margin)
        else:
            cite = f"\n\n{' '}No citations"
        return cite

    def _get_citation_dependency_str(self, citation, parameters, width,
                                     str_margin):
        """Create a message for citations dependent on a
        certain parameter

        :param citation: Single citation dictionary
        :param parameters: List of current parameter values
        :param width: The terminal display width for output strings
        :param str_margin: The terminal display margin
        :return: str_dep, A string to identify citations dependent on
        certain parameter values
        """
        str_dep = ""
        for (citation_dependent_parameter, citation_dependent_value) \
            in citation.dependency.items():
            current_value = parameters[citation_dependent_parameter]
            if current_value == citation_dependent_value:
                str_dep = (
                    f"This citation is for the {citation_dependent_value}"
                    f" {citation_dependent_parameter}"
                )
                str_dep = self._get_equal_lines(
                    str_dep, width, Style.BRIGHT, Style.RESET_ALL, str_margin
                )
        return str_dep

    def _get_framework_title(self, width, fore_colour, back_colour):
        title = "Framework Citations "
        width -= len(title)
        title_str = back_colour + fore_colour + title + " " * width \
                    + Style.RESET_ALL
        return title_str

    def _get_framework_citations(self, width):
        """ Create a string containing framework citations

        :param width: Width of formatted text
        :return: String with framework citations
        """
        citation_dict = {}
        framework_cites = fc.get_framework_citations()
        for cite in framework_cites:
            citation = CitationInformation(**cite)
            citation_dict.update({citation.name: citation})

        title = \
            self._get_framework_title(width, Fore.LIGHTWHITE_EX,
                                             Back.LIGHTBLACK_EX)

        cite = self._get_citation_str(citation_dict, width)
        return title+cite+"\n"

    def _get_citation_lines(self, citation, width, str_margin):
        """Print certain information about the citation in order.

        :param citation: Single citation dictionary
        :param width: The terminal display width for output strings
        :param str_margin: The terminal display margin
        :return: A string containing citation details
        """
        cite_keys = ["name", "description", "doi", "bibtex", "endnote"]
        cite_dict = citation.__dict__
        cite_str = ""

        style_on = Style.BRIGHT
        style_off = Style.RESET_ALL

        for key in cite_keys:
            if cite_dict[key]:
                # Set the key name to be bold
                cite_key = self._get_equal_lines(
                    key.title(), width, style_on, style_off, str_margin
                )
                # No style for the citation content
                cite_value = self._get_equal_lines(
                    cite_dict[key], width, style_off, style_off, str_margin
                )
                # New line for each item
                cite_str += "\n" + cite_key + "\n" + cite_value + "\n"

        return cite_str
