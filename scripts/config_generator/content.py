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
.. module:: content
   :platform: Unix
   :synopsis: Content class for the configurator

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""
import re
import os
import copy
import inspect

from savu.plugins import utils as pu
from savu.data.plugin_list import PluginList
import scripts.config_generator.parameter_utils as param_u

from . import mutations


class Content(object):
    def __init__(self, filename=None, level="basic"):
        self.disp_level = level
        self.plugin_list = PluginList()
        self.plugin_mutations = mutations.plugin_mutations
        self.param_mutations = mutations.param_mutations
        self.filename = filename
        self._finished = False
        self.failed = {}
        self.expand_dim = None

    def set_finished(self, check="y"):
        self._finished = True if check.lower() == "y" else False

    def is_finished(self):
        return self._finished

    def fopen(self, infile, update=False, skip=False):
        if os.path.exists(infile):
            self.plugin_list._populate_plugin_list(infile, active_pass=True)
        else:
            raise Exception("INPUT ERROR: The file does not exist.")
        self.filename = infile
        if update:
            self.plugin_mutations = self.check_mutations(
                self.plugin_mutations
            )
            self.param_mutations = self.check_mutations(self.param_mutations)
            self._apply_plugin_updates(skip)

    def check_mutations(self, mut_dict: dict):
        plist_version = self._version_to_float(self.plugin_list.version)
        # deleting elements while iterating invalidates the iterator
        # which raises a RuntimeError in Python 3.
        # Instead a copy of the dict is mutated and returned
        mut_dict_copy = mut_dict.copy()
        for key, subdict in mut_dict.items():
            if "up_to_version" in subdict.keys():
                up_to_version = self._version_to_float(
                    subdict["up_to_version"]
                )
                if plist_version >= up_to_version:
                    del mut_dict_copy[key]
        return mut_dict_copy

    def _version_to_float(self, version):
        if version is None:
            return 0
        if isinstance(version, bytes):
            version = version.decode("ascii")
        split_vals = version.split(".")
        return float(".".join([split_vals[0], "".join(split_vals[1:])]))

    def display(self, formatter, **kwargs):
        # Set current level
        if "current_level" not in list(kwargs.keys()):
            kwargs["current_level"] = self.disp_level
        if (
            "disp_level" in list(kwargs.keys())
            and kwargs["disp_level"] is True
        ):
            # Display level
            print(f"Level is set at '{kwargs['current_level']}'")
        else:
            # Display parameter
            kwargs["expand_dim"] = self.expand_dim
            print("\n" + formatter._get_string(**kwargs) + "\n")

    def check_file(self, filename):
        if not filename:
            raise Exception(
                "INPUT ERROR: Please specify the output filepath."
            )
        path = os.path.dirname(filename)
        path = path if path else "."
        if not os.path.exists(path):
            file_error = "INPUT_ERROR: Incorrect filepath."
            raise Exception(file_error)

    def save(self, filename, check="y", template=False):
        self.check_plugin_list_exists()
        # Check if a loader and saver are present.
        self.plugin_list._check_loaders()
        if check.lower() == "y":
            print(f"Saving file {filename}")
            if template:
                self.plugin_list.add_template(create=True)
            self.plugin_list._save_plugin_list(filename)
        else:
            print("The process list has NOT been saved.")

    def clear(self, check="y"):
        if check.lower() == "y":
            self.expand_dim = None
            self.plugin_list.plugin_list = []
            self.plugin_list.clear_iterate_plugin_group_dicts()

    def check_plugin_list_exists(self):
        """ Check if plugin list is populated. """
        pos_list = self.get_positions()
        if not pos_list:
            print("There are no items to access in your list.")
            raise Exception("Please add an item to the process list.")

    def add(self, name, str_pos):
        self.check_for_plugin_failure(name)
        plugin = pu.plugins[name]()
        plugin.get_plugin_tools()._populate_default_parameters()
        pos, str_pos = self.convert_pos(str_pos)
        self.insert(plugin, pos, str_pos)

    def iterate(self, args):
        if args.remove is None and args.set is None:
            # no optional args are given; default to displaying all iterative
            # loops
            self.display_iterative_loops()
        elif args.remove is not None:
            self.remove_iterate_plugin_groups(args.remove)
        elif args.set is not None:
            # create a dict representing a group of plugins to iterate over
            start = args.set[0]
            end = args.set[1]
            iterations = args.set[2]
            self.add_iterate_plugin_group(start, end, iterations)

    def add_iterate_plugin_group(self, start, end, iterations):
        '''
        Add a dict to PluginList that represents a group of plugins in the
        process list to iterate over
        '''
        self.plugin_list.add_iterate_plugin_group_dict(start, end, iterations)

    def remove_iterate_plugin_groups(self, indices):
        """
        Remove dicts in PluginList that represent a group of plugins in the
        process list to iterate over
        """
        self.plugin_list.remove_iterate_plugin_group_dicts(indices)

    def refresh(self, str_pos, defaults=False, change=False):
        pos = self.find_position(str_pos)
        plugin_entry = self.plugin_list.plugin_list[pos]
        name = change if change else plugin_entry["name"]
        active = plugin_entry["active"]
        plugin = pu.plugins[name]()
        plugin.get_plugin_tools()._populate_default_parameters()
        keep = self.get(pos)["data"] if not defaults else None
        self.insert(plugin, pos, str_pos, replace=True)
        self.plugin_list.plugin_list[pos]["active"] = active
        if keep:
            self._update_parameters(plugin, name, keep, str_pos)

    def duplicate(self, dupl_pos, new):
        """ Duplicate the plugin at position dupl_pos
        and insert it at the new position

        :param dupl_pos: Position of the plugin to duplicate
        :param new: New plugin position
        """
        pos = self.find_position(dupl_pos)
        new_pos, new_pos_str = self.convert_pos(new)
        plugin_entry = copy.deepcopy(self.plugin_list.plugin_list[pos])
        plugin_entry["pos"] = new_pos_str
        self.plugin_list.plugin_list.insert(new_pos, plugin_entry)

    def check_for_plugin_failure(self, name):
        """Check if the plugin failed to load

        :param name: plugin name
        """
        if (name not in list(pu.plugins.keys())
                or self.plugin_in_failed_dict(name)):
                if self.plugin_in_failed_dict(name):
                    msg = f"IMPORT ERROR: {name} is unavailable due to" \
                          f" the following error:\n\t{self.failed[name]}"
                    raise Exception(msg)
                raise Exception("INPUT ERROR: Unknown plugin %s" % name)

    def plugin_in_failed_dict(self, name):
        """Check if plugin in failed dictionary

        :param name: plugin name
        :return: True if plugin name in the list of failed plugins
        """
        failed_plugin_list = list(self.failed.keys()) if self.failed else []
        return True if name in failed_plugin_list else False

    def check_preview_param(self, plugin_pos):
        """ Check that the plugin position number is valid and it contains
        a preview parameter

        :param plugin_pos:
        :return:
        """
        pos = self.find_position(plugin_pos)
        plugin_entry = self.plugin_list.plugin_list[pos]
        parameters = plugin_entry["data"]
        if "preview" not in parameters:
            raise Exception("You can only use this command with "
                            "plugins containing the preview parameter")

    def set_preview_display(self, expand_off, expand_dim, dim_view,
                            plugin_pos):
        """Set the dimensions_to_display value to "off" to prevent the
        preview parameter being shown in it's expanded form.

        If dimensions_to_display = "all", then all dimension slices are shown.
        If a number is provided to dim_view, that dimension is shown.

        :param expand_off: True if expand display should be turned off
        :param expand_dim: The dimension number to display, or "all"
        :param dim_view: True if only a certain dimension should be shown
        :param plugin_pos: Plugin position
        """
        if expand_off is True:
            self.expand_dim = None
            print(f"Expand diplay has been turned off")
        else:
            self.check_preview_param(plugin_pos)
            dims_to_display = expand_dim if dim_view else "all"
            self.expand_dim = dims_to_display

    def _update_parameters(self, plugin, name, keep, str_pos):
        union_params = set(keep).intersection(set(plugin.parameters))
        # Names of the parameter names present in both lists
        for param in union_params:
            self.modify(str_pos, param, keep[param], ref=True)
        # add any parameter mutations here
        classes = [c.__name__ for c in inspect.getmro(plugin.__class__)]
        m_dict = self.param_mutations
        keys = [k for k in list(m_dict.keys()) if k in classes]

        changes = False
        for k in keys:
            for entry in m_dict[k]["params"]:
                if entry["old"] in list(keep.keys()):
                    changes = True
                    val = keep[entry["old"]]
                    if "eval" in list(entry.keys()):
                        val = eval(entry["eval"])
                    self.modify(str_pos, entry["new"], val, ref=True)
        if changes:
            mutations.param_change_str(keep, plugin.parameters, name, keys)

    def _apply_plugin_updates(self, skip=False):
        # Update old process lists that start from 0
        the_list = self.plugin_list.plugin_list
        if "pos" in list(the_list[0].keys()) and the_list[0]["pos"] == "0":
            self.increment_positions()

        missing = []
        pos = len(the_list) - 1
        notices = mutations.plugin_notices

        for plugin in the_list[::-1]:
            # update old process lists to include 'active' flag
            if "active" not in list(plugin.keys()):
                plugin["active"] = True

            while True:
                name = the_list[pos]["name"]
                if name in notices.keys():
                    print(notices[name]["desc"])

                # if a plugin is missing from all available plugins
                # then look for mutations in the plugin name
                search = True if name not in pu.plugins.keys() else False
                found = self._mutate_plugins(name, pos, search=search)
                if search and not found:
                    str_pos = self.plugin_list.plugin_list[pos]["pos"]
                    missing.append([name, str_pos])
                    self.remove(pos)
                    pos -= 1
                if name == the_list[pos]["name"]:
                    break
            pos -= 1

        for name, pos in missing[::-1]:
            if skip:
                print(f"Skipping plugin {pos}: {name}")
            else:
                message = (
                    f"\nPLUGIN ERROR: The plugin {name} is "
                    f"unavailable in this version of Savu. \nThe plugin is "
                    f"missing from the position {pos} in the process list. "
                    f"\n Type open -s <process_list> to skip the broken "
                    f"plugin."
                )
                raise Exception(f"Incompatible process list. {message}")

    def _mutate_plugins(self, name, pos, search=False):
        """ Perform plugin mutations. """
        # check for case changes in plugin name
        if search:
            for key in pu.plugins.keys():
                if name.lower() == key.lower():
                    str_pos = self.plugin_list.plugin_list[pos]["pos"]
                    self.refresh(str_pos, change=key)
                    return True

        # check mutations dict
        m_dict = self.plugin_mutations
        if name in m_dict.keys():
            mutate = m_dict[name]
            if "replace" in mutate.keys():
                if mutate["replace"] in list(pu.plugins.keys()):
                    str_pos = self.plugin_list.plugin_list[pos]["pos"]
                    self.refresh(str_pos, change=mutate["replace"])
                    print(mutate["desc"])
                    return True
                raise Exception(
                    f"Replacement plugin {mutate['replace']} "
                    f"unavailable for {name}"
                )
            elif "remove" in mutate.keys():
                self.remove(pos)
                print(mutate["desc"])
            else:
                raise Exception("Unknown mutation type.")
        return False

    def move(self, old, new):
        old_pos = self.find_position(old)
        entry = self.plugin_list.plugin_list[old_pos]
        self.remove(old_pos)
        new_pos, new = self.convert_pos(new)
        name = entry["name"]
        self.insert(pu.plugins[name](), new_pos, new)
        self.plugin_list.plugin_list[new_pos] = entry
        self.plugin_list.plugin_list[new_pos]["pos"] = new
        self.check_iterative_loops([old_pos + 1, new_pos + 1], 0)

    def modify(self, pos_str, param_name, value, default=False, ref=False,
               dim=False):
        """Modify the plugin at pos_str and the parameter at param_name
        The new value will be set if it is valid.

        :param pos_str: The plugin position
        :param param_name: The parameter position/name
        :param value: The new parameter value
        :param default: True if value should be reverted to the default
        :param ref: boolean Refresh the plugin
        :param dim: The dimension to be modified

        returns: A boolean True if the value is a valid input for the
          selected parameter
        """
        pos = self.find_position(pos_str)
        plugin_entry = self.plugin_list.plugin_list[pos]
        tools = plugin_entry["tools"]
        parameters = plugin_entry["data"]
        params = plugin_entry["param"]
        param_name, value = self.setup_modify(params, param_name, value, ref)
        default_str = ["-d", "--default"]
        if default or value in default_str:
            value = tools.get_default_value(param_name)
            self._change_value(param_name, value, tools, parameters)
            valid_modification = True
        else:
            value = self._catch_parameter_tuning_syntax(value, param_name)
            valid_modification = self.modify_main(
                param_name, value, tools, parameters, dim
            )
        return valid_modification

    def _catch_parameter_tuning_syntax(self, value, param_name):
        """Check if the new parameter value seems like it is written
        in parameter tuning syntax with colons. If it is, then append
        a semi colon onto the end.

        :param value: new parameter value
        :param param_name:
        :return: modified value with semi colon appended
        """
        exempt_parameters = ["preview", "indices"]
        if self._is_multi_parameter_syntax(value) \
                and param_name not in exempt_parameters:
            # Assume parameter tuning syntax is being used
            value = f"{value};"
            print("Parameter tuning syntax applied")
        return value

    def _is_multi_parameter_syntax(self, value):
        """If the value contains two colons, is not a dictionary,
        and doesnt already contain a semi colon, then assume that
        it is using parameter tuning syntax

        :param value: new parameter value
        :return boolean True if parameter tuning syntax is being used
        """
        isdict = re.findall(r"[\{\}]+", str(value))
        return (isinstance(value, str)
                and value.count(":") >= 2
                and not isdict
                and ";" not in value)

    def setup_modify(self, params, param_name, value, ref):
        """Get the parameter keys in the correct order and find
        the parameter name string

        :param params: The plugin parameters
        :param param_name: The parameter position/name
        :param value: The new parameter value
        :param ref: boolean Refresh the plugin

        return: param_name str to avoid discrepancy, value
        """
        if ref:
            # For a refresh, refresh all keys, including those with
            # dependencies (which have the display off)
            keys = params.keys()
        else:
            # Select the correct group and order of parameters according to that
            # on display to the user. This ensures correct parameter is modified.
            keys = pu.set_order_by_visibility(params)
            value = self.value(value)
        param_name = pu.param_to_str(param_name, keys)
        return param_name, value

    def modify_main(self, param_name, value, tools, parameters, dim):
        """Check the parameter is within the current parameter list.
        Check the new parameter value is valid, modify the parameter
        value, update defaults, check if dependent parameters should
        be made visible or hidden.

        :param param_name: The parameter position/name
        :param value: The new parameter value
        :param tools: The plugin tools
        :param parameters: The plugin parameters
        :param dim: The dimensions

        returns: A boolean True if the value is a valid input for the
          selected parameter
        """
        parameter_valid = False
        current_parameter_details = tools.param.get(param_name)

        # If dimensions are provided then alter preview param
        if self.preview_dimension_to_modify(dim, param_name):
            # Filter the dimension, dim1 or dim1.start
            dim, _slice = self._separate_dimension_and_slice(dim)
            value = self.modify_preview(
                parameters, param_name, value, dim, _slice
            )

        # If found, then the parameter is within the current parameter list
        # displayed to the user
        if current_parameter_details:
            value_check = pu._dumps(value)
            parameter_valid, error_str = param_u.is_valid(
                param_name, value_check, current_parameter_details
            )
            if parameter_valid:
                self._change_value(param_name, value, tools, parameters)
            else:
                value = str(value)
                display_value = f"{value[0:12]}.." if len(value) > 12 \
                                else value
                print(f"ERROR: The input value {display_value} "
                      f"for {param_name} is not correct.")
                print(error_str)
        else:
            print("Not in parameter keys.")
        return parameter_valid

    def _change_value(self, param_name, value, tools, parameters):
        """ Change the parameter "param_name" value inside the parameters list
        Update feedback messages for various dependant parameters

        :param param_name: The parameter position/name
        :param value: The new parameter value
        :param tools: The plugin tools
        :param parameters: The plugin parameters
        """
        # Save the value
        parameters[param_name] = value
        tools.warn_dependents(param_name, value)
        # Update the list of parameters to hide those dependent on others
        tools.check_dependencies(parameters)

    def check_required_args(self, value, required):
        """Check required argument 'value' is present

        :param value: Argument value
        :param required: bool, True if the argument is required
        """
        if required and (not value):
            raise Exception("Please enter a value")

        if (not required) and value:
            raise Exception(f"Unrecognised argument: {value}")

    def preview_dimension_to_modify(self, dim, param_name):
        """Check that the dimension string is only present when the parameter
        to modify is the preview parameter

        :param dim: Dimension string
        :param param_name: The parameter name (of the parameter to be modified)
        :return: True if dimension string is provided and the parameter to modify
        the preview parameter
        """
        if dim:
            if param_name == "preview":
                return True
            else:
                raise Exception(
                    "Please only use the dimension syntax when "
                    "modifying the preview parameter."
                )
        return False

    def modify_dimensions(self, pos_str, dim, check="y"):
        """Modify the plugin preview value. Remove or add dimensions
        to the preview parameter until the provided dimension number
        is reached.

        :param pos_str: The plugin position
        :param dim: The new number of dimensions
        :return True if preview is modified
        """
        pos = self.find_position(pos_str)
        plugin_entry = self.plugin_list.plugin_list[pos]
        parameters = plugin_entry["data"]
        self.check_param_exists(parameters, "preview")
        current_prev_list = pu._dumps(parameters["preview"])
        if not isinstance(current_prev_list, list):
            # Temporarily cover dict instance for preview
            print("This command is only possible for preview "
                  "values of the type list")
            return False
        pu.check_valid_dimension(dim, [])
        if check.lower() == "y":
            while len(current_prev_list) > dim:
                current_prev_list.pop()
            while len(current_prev_list) < dim:
                current_prev_list.append(":")
            parameters["preview"] = current_prev_list
            return True
        return False

    def check_param_exists(self, parameters, pname):
        """Check the parameter is present in the current parameter list

        :param parameters: Dictionary of parameters
        :param pname: Parameter name
        :return:
        """
        if not parameters.get(pname):
            raise Exception(
                f"The {pname} parameter is not available" f" for this plugin."
            )


    def plugin_to_num(self, plugin_val, pl_index):
        """Check the plugin is within the process list and
        return the number in the list.

        :param plugin_val: The dictionary of parameters
        :param pl_index: The plugin index (for use when there are multiple
           plugins of same name)
        :return: A plugin index number of a certain plugin in the process list
        """
        if plugin_val.isdigit():
            return plugin_val
        pl_names = [pl["name"] for pl in self.plugin_list.plugin_list]
        if plugin_val in pl_names:
            # Find the plugin number
            pl_indexes = [i for i, p in enumerate(pl_names) if p == plugin_val]
            # Subtract one to access correct list index. Add one to access
            # correct plugin position
            return str(pl_indexes[pl_index-1] +1)
        else:
            raise Exception("This plugin is not present in this process list.")


    def value(self, value):
        if not value.count(";"):
            try:
                value = eval(value)
            except (NameError, SyntaxError):
                try:
                    value = eval(f"'{value}'")
                    # if there is one quotation mark there will be an error
                except EOFError:
                    raise EOFError(
                        "There is an end of line error. Please check your"
                        ' input for the character "\'".'
                    )
                except SyntaxError:
                    raise SyntaxError(
                        "There is a syntax error. Please check your input."
                    )
                except:
                    raise Exception("Please check your input.")
        return value

    def convert_to_ascii(self, value):
        ascii_list = []
        for v in value:
            ascii_list.append(v.encode("ascii", "ignore"))
        return ascii_list

    def on_and_off(self, str_pos, index):
        print(("switching plugin %s %s" % (str_pos, index)))
        status = True if index == "ON" else False
        pos = self.find_position(str_pos)
        self.plugin_list.plugin_list[pos]["active"] = status

    def convert_pos(self, str_pos):
        """ Converts the display position (input) to the equivalent numerical
        position and updates the display position if required.

        :param str_pos: the plugin display position (input) string.
        :returns: the equivalent numerical position of str_pos and and updated\
            str_pos.
        :rtype: (pos, str_pos)
        """
        pos_list = self.get_split_positions()
        num = re.findall(r"\d+", str_pos)[0]
        letter = re.findall("[a-z]", str_pos)
        entry = [num, letter[0]] if letter else [num]

        # full value already exists in the list
        if entry in pos_list:
            index = pos_list.index(entry)
            return self.inc_positions(index, pos_list, entry, 1)

        # only the number exists in the list
        num_list = [pos_list[i][0] for i in range(len(pos_list))]
        if entry[0] in num_list:
            start = num_list.index(entry[0])
            if len(entry) == 2:
                if len(pos_list[start]) == 2:
                    idx = int([i for i in range(len(num_list)) if
                               (num_list[i] == entry[0])][-1]) + 1
                    entry = [entry[0], str(chr(ord(pos_list[idx - 1][1]) + 1))]
                    return idx, ''.join(entry)
                if entry[1] == 'a':
                    self.plugin_list.plugin_list[start]['pos'] = entry[0] + 'b'
                    return start, ''.join(entry)
                else:
                    self.plugin_list.plugin_list[start]['pos'] = entry[0] + 'a'
                    return start + 1, entry[0] + 'b'
            return self.inc_positions(start, pos_list, entry, 1)

        # number not in list
        entry[0] = str(int(num_list[-1]) + 1 if num_list else 1)
        if len(entry) == 2:
            entry[1] = "a"
        return len(self.plugin_list.plugin_list), "".join(entry)

    def increment_positions(self):
        """Update old process lists that start plugin numbering from 0 to
        start from 1."""
        for plugin in self.plugin_list.plugin_list:
            str_pos = plugin["pos"]
            num = str(int(re.findall(r"\d+", str_pos)[0]) + 1)
            letter = re.findall("[a-z]", str_pos)
            plugin["pos"] = "".join([num, letter[0]] if letter else [num])

    def get_positions(self):
        """ Get a list of all current plugin entry positions. """
        elems = self.plugin_list.plugin_list
        pos_list = []
        for e in elems:
            pos_list.append(e["pos"])
        return pos_list

    def get_param_arg_str(self, pos_str, subelem):
        """Get the name of the parameter so that the display lists the
        correct item when the parameter order has been updated

        :param pos_str: The plugin position
        :param subelem: The parameter
        :return: The plugin.parameter_name argument
        """
        pos = self.find_position(pos_str)
        current_parameter_list = self.plugin_list.plugin_list[pos]["param"]
        current_parameter_list_ordered = pu.set_order_by_visibility(
            current_parameter_list
        )
        param_name = pu.param_to_str(subelem, current_parameter_list_ordered)
        param_argument = pos_str + "." + param_name
        return param_argument

    def get_split_positions(self):
        """ Separate numbers and letters in positions. """
        positions = self.get_positions()
        split_pos = []
        for i in range(len(positions)):
            num = re.findall(r"\d+", positions[i])[0]
            letter = re.findall("[a-z]", positions[i])
            split_pos.append([num, letter[0]] if letter else [num])
        return split_pos

    def find_position(self, pos):
        """ Find the numerical index of a position (a string). """
        pos_list = self.get_positions()
        if not pos_list:
            print("There are no items to access in your list.")
            raise Exception("Please add an item to the process list.")
        else:
            if pos not in pos_list:
                raise ValueError("Incorrect plugin position.")
            return pos_list.index(pos)

    def inc_positions(self, start, pos_list, entry, inc):
        if len(entry) == 1:
            self.inc_numbers(start, pos_list, inc)
        else:
            idx = [
                i
                for i in range(start, len(pos_list))
                if pos_list[i][0] == entry[0]
            ]
            self.inc_letters(idx, pos_list, inc)
        return start, "".join(entry)

    def inc_numbers(self, start, pos_list, inc):
        for i in range(start, len(pos_list)):
            pos_list[i][0] = str(int(pos_list[i][0]) + inc)
            self.plugin_list.plugin_list[i]["pos"] = "".join(pos_list[i])

    def inc_letters(self, idx, pos_list, inc):
        for i in idx:
            pos_list[i][1] = str(chr(ord(pos_list[i][1]) + inc))
            self.plugin_list.plugin_list[i]["pos"] = "".join(pos_list[i])

    def split_plugin_string(self, start, stop, subelem_view=False):
        """Find the start and stop number for the plugin range selected.

        :param start: Plugin starting index (including a subelem value
          if permitted)
        :param stop: Plugin stopping index
        :param subelem_view: False if subelem value not permitted
        :return: range_dict containing start stop (and possible subelem)
        """
        range_dict = {}
        if start:
            if subelem_view and "." in start:
                start, stop, subelem = self._split_subelem(start)
                range_dict["subelem"] = subelem
            else:
                start, stop = self._get_start_stop(start, stop)
            range_dict["start"] = start
            range_dict["stop"] = stop
        return range_dict

    def _get_start_stop(self, start, stop):
        """Find the start and stop number for the plugin range selected """
        start = self.find_position(start)
        stop = self.find_position(stop) + 1 if stop else start + 1
        return start, stop

    def _split_subelem(self, start, config_disp=True):
        """Separate the start string containing the plugin number,
        parameter(subelement), dimension and command

        :param start: The plugin to start at
        :param config_disp: True if command and dimension arguments
          are not permitted
        :return: start plugin, range_dict containing a subelem
            if a parameter is specified
        """
        start, subelem, dim, command = self.separate_plugin_subelem(
            start, config_disp
        )
        start, stop = self._get_start_stop(start, "")
        return start, stop, subelem

    def _check_command_valid(self, plugin_param, config_disp):
        """Check the plugin_param string length

        :param plugin_param: The string containing plugin number, parameter,
         and command
        :param config_disp: bool, True if command and dimension arguments are
          not permitted
        """
        if config_disp:
            if not 1 < len(plugin_param) < 3:
                raise ValueError(
                    "Use either 'plugin_pos.param_name' or"
                    " 'plugin_pos.param_no'"
                )
        else:
            # The modify command is being used
            if len(plugin_param) <= 1:
                raise ValueError(
                    "Please enter the plugin parameter to modify"
                    ". Either 'plugin_pos.param_name' or"
                    " 'plugin_pos.param_no'"
                )
            if not 1 < len(plugin_param) < 5:
                raise ValueError(
                    "Enter 'plugin_pos.param_no.dimension'. "
                    "Following the dimension, use start/stop/step"
                    " eg. '1.1.dim1.start' "
                )

    def separate_plugin_subelem(self, plugin_param, config_disp):
        """Separate the plugin number,parameter (subelement) number
        and additional command if present.

        :param plugin_param: A string supplied by the user input which
         contains the plugin element to edit/display. eg "1.1.dim.command"
        :param config_disp: bool, True if command and dimension arguments are
          not permitted

        :returns plugin: The number of the plugin element
                 subelem: The number of the parameter
                 dim: The dimension
                 command: The supplied command, eg expand or a dimension
                          string
        """
        plugin_param = plugin_param.split(".")
        plugin = plugin_param[0]
        # change str plugin name to a number
        start = self.find_position(plugin)
        self._check_command_valid(plugin_param, config_disp)
        subelem = plugin_param[1]
        if len(plugin_param) > 2:
            dim = self.dim_str_to_int(plugin_param[2])
            command = str(dim)
            if len(plugin_param) == 4:
                self._check_command_str(plugin_param[3])
                command += "." + plugin_param[3]
        else:
            dim, command = "", ""
        return plugin, subelem, dim, command

    def _check_command_str(self, command_str):
        """Check the additional 1.1.dim.command for slice or 'expand'
        keywords
        """
        command_list = ["expand", "start", "stop", "step", "chunk"]
        if command_str not in command_list:
            raise ValueError(
                "Following the dimension, use start/stop/step eg.  "
                "'1.1.dim1.start' "
            )
        return command_str

    def insert(self, plugin, pos, str_pos, replace=False):
        plugin_dict = self.create_plugin_dict(plugin)
        plugin_dict["pos"] = str_pos
        if replace:
            self.plugin_list.plugin_list[pos] = plugin_dict
        else:
            self.plugin_list.plugin_list.insert(pos, plugin_dict)

    def create_plugin_dict(self, plugin):
        tools = plugin.get_plugin_tools()
        plugin_dict = {}
        plugin_dict["name"] = plugin.name
        plugin_dict["id"] = plugin.__module__
        plugin_dict["data"] = plugin.parameters
        plugin_dict["active"] = True
        plugin_dict["tools"] = tools
        plugin_dict["param"] = tools.get_param_definitions()
        plugin_dict["doc"] = tools.docstring_info
        return plugin_dict

    def get(self, pos):
        return self.plugin_list.plugin_list[pos]

    def _separate_dimension_and_slice(self, command_str):
        """Check the start stop step command

        param command_str: a string '1.1' containing the dimension
            and slice number seperated by a full stop

        :returns dim, slice
        """
        if isinstance(command_str, str) and "." in command_str:
            # If the slice value is included
            slice_dict = {"start": 0, "stop": 1, "step": 2, "chunk": 3}
            _slice = slice_dict[command_str.split(".")[1]]
            dim = int(command_str.split(".")[0])
        else:
            dim = int(command_str)
            _slice = ""
        return dim, _slice

    def dim_str_to_int(self, dim_str):
        """Check the additional 1.1.dim keyword

        :param dim: A string 'dim1' specifying the dimension

        :return: dim - An integer dimension value
        """
        number = "".join(l for l in dim_str if l.isdigit())
        letters = "".join(l for l in dim_str if l.isalpha())

        if letters == "dim" and number.strip():
            dim = int(number)
        else:
            raise ValueError(
                "Following the second decimal place, please "
                "specify a dimension 1.1.dim1 or 1.preview.dim1"
            )
        return dim

    def modify_preview(self, parameters, param_name, value, dim, _slice):
        """ Check the entered value is valid and edit preview"""
        slice_list = [0, 1, 2, 3]
        type_check_value = pu._dumps(value)
        current_preview_value = pu._dumps(parameters[param_name])
        pu.check_valid_dimension(dim, current_preview_value)
        if _slice in slice_list:
            # Modify this dimension and slice only
            if param_u._preview_dimension_singular(type_check_value):
                value = self._modify_preview_dimension_slice(
                    value, current_preview_value, dim, _slice
                )
            else:
                raise ValueError(
                    "Invalid preview dimension slice value. Please "
                    "enter a float, an integer or a string including "
                    "only start, mid and end keywords."
                )
        else:
            # If the entered value is a valid dimension value
            if param_u._preview_dimension(type_check_value):
                # Modify the whole dimension
                value = self._modify_preview_dimension(
                    value, current_preview_value, dim
                )
            else:
                raise ValueError(
                    "Invalid preview dimension value. Please "
                    "enter a float, an integer or slice notation."
                )
        return value

    def _modify_preview_dimension_slice(self, value, current_val, dim, _slice):
        """Modify the preview dimension slice value at the dimension (dim)
        provided

        :param value: The new value
        :param current_value: The current preview parameter value
        :param dim: The dimension to modify
        :param _slice: The slice value to modify
        :return: The modified value
        """
        if not current_val:
            current_val = self._set_empty_list(
                dim, self._set_empty_dimension_slice(value, _slice)
            )
        else:
            current_val[dim - 1] = self._modified_slice_notation(
                current_val[dim - 1], value, _slice
            )
        return current_val

    def _modified_slice_notation(self, old_value, value, _slice):
        """Change the current value at the provided slice

        :param old_value: Previous slice notation
        :param value: New value to set
        :param _slice: Slice to modify
        :return: Changed value (str/int)
        """
        old_value = self._set_incomplete_slices(str(old_value), _slice)
        if pu.is_slice_notation(old_value):
            start_stop_split = old_value.split(":")
            return self._get_modified_slice(start_stop_split, value, _slice)
        elif _slice == 0:
            # If there is no slice notation, only allow first slice to
            # be modified
            return value
        else:
            raise Exception(
                "There is no existing slice notation to modify."
            )

    def _get_modified_slice(self, start_stop_split, value, _slice):
        if all(v == "" for v in start_stop_split):
            return self._set_empty_dimension_slice(value, _slice)
        else:
            start_stop_split[_slice] = str(value)
            start_stop_split = ":".join(start_stop_split)
            return start_stop_split

    def _modify_preview_dimension(self, value, current_preview, dim):
        """Modify the preview list value at the dimension provided (dim)

        :param value: The new value
        :param current_value: The current preview parameter list value
        :param dim: The dimension to modify
        :return: The modified value
        """
        if not current_preview:
            return self._set_empty_list(dim, value)
        current_preview[dim - 1] = value
        # Save the altered preview value
        return current_preview

    def _set_empty_dimension_slice(self, value, _slice):
        """Set the empty dimension and insert colons to indicate
        the correct slice notation.

        :param value: New value to set
        :param _slice: start/stop/step/chunk value
        :return: String for the new value
        """
        return _slice * ":" + str(value)

    def _set_incomplete_slices(self, old_value, _slice):
        """Append default slice values.to the current string value, in order
         to allow later slice values to be set

        :param old_value: Current string value with slice notation
        :param _slice: slice notation index to be edited
        :return: String with default slice notation entries set
        """
        while old_value.count(":") < _slice:
            old_value += ":"
        return old_value

    def _set_empty_list(self, dim, value):
        """If the dimension is 1 then allow the whole empty list
        to be set.

        :param dim: Dimension to be altered
        :param value: New value
        :return: List containing new value
        """
        if dim == 1:
            return [value]
        else:
            raise ValueError("You have not set earlier dimensions")

    def level(self, level):
        """ Set the visibility level of parameters """
        if level:
            self.disp_level = level
            print(f"Level set to '{level}'")
        else:
            print(f"Level is set at '{self.disp_level}'")

    def remove(self, pos):
        if pos >= self.size:
            raise Exception(
                "Cannot remove plugin %s as it does not exist."
                % self.plugin_list.plugin_list[pos]["name"]
            )
        pos_str = self.plugin_list.plugin_list[pos]["pos"]
        self.plugin_list.plugin_list.pop(pos)
        pos_list = self.get_split_positions()
        self.inc_positions(pos, pos_list, pos_str, -1)

    def check_iterative_loops(self, positions, direction):
        """
        When a plugin is added, removed, or moved, check if any iterative loops
        should be removed or shifted
        """
        def moved_plugin(old_pos, new_pos):
            is_in_loop = self.plugin_list.check_pos_in_iterative_loop(old_pos)
            if is_in_loop and old_pos != new_pos:
                self.plugin_list.remove_associated_iterate_group_dict(
                    old_pos, -1)

            if_will_be_in_loop = \
                self.plugin_list.check_pos_in_iterative_loop(new_pos)
            if if_will_be_in_loop and old_pos != new_pos:
                self.plugin_list.remove_associated_iterate_group_dict(
                    new_pos, -1)

            # shift any relevant loops
            if new_pos < old_pos:
                self.plugin_list.shift_range_iterative_loops(
                    [new_pos, old_pos], 1)
            elif new_pos > old_pos:
                self.plugin_list.shift_range_iterative_loops(
                    [old_pos, new_pos], -1)

        def added_removed_plugin(pos, direction):
            is_in_loop = self.plugin_list.check_pos_in_iterative_loop(pos)
            if is_in_loop:
                # delete the associated loop
                self.plugin_list.remove_associated_iterate_group_dict(pos,
                    direction)

            # check if there are any iterative loops in the process list
            do_loops_exist = len(self.plugin_list.iterate_plugin_groups) > 0
            if do_loops_exist:
                if direction == -1:
                    # shift the start+end of all loops after the plugin down by
                    # 1
                    self.plugin_list.shift_subsequent_iterative_loops(pos, -1)
                elif direction == 1:
                    # shift the start+end of all loops after the plugin up by 1
                    self.plugin_list.shift_subsequent_iterative_loops(pos, 1)

        if direction == 0:
            # a plugin has been moved
            moved_plugin(positions[0], positions[1])
        else:
            # a plugin has been added or removed
            added_removed_plugin(positions[0], direction)

    @property
    def size(self):
        return len(self.plugin_list.plugin_list)

    def display_iterative_loops(self):
        self.plugin_list.print_iterative_loops()