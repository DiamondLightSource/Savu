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
.. module:: base_type
   :platform: Unix
   :synopsis: A base module for different data types.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import inspect

import savu.plugins.utils as pu


class BaseType(object):

    def __init__(self):
        self._clone_args = {}
        self._map_args = {}
        self.base_data_args()

    def __getitem__(self, index):
        """ Override __getitem__ and map to the relevant files """
        raise NotImplementedError("__getitem__ must be implemented.")

    def get_shape(self):
        """ Get full stitched shape of a stack of files"""
        raise NotImplementedError("get_shape must be implemented.")

    def add_base_class_with_instance(self, base, inst):
        """ Add a base class instance to a class (merging of two data types).

        :params class base: a class to add as a base class
        :params instance inst: an instance of the base class
        """
        cls = self.__class__
        namespace = self.__class__.__dict__.copy()
        self.__dict__.update(inst.__dict__)
        self.__class__ = cls.__class__(cls.__name__, (cls, base), namespace)

    def base_data_args(self):
        """ Create a dictionary of required input arguments, required for
        checkpointing. """
        cls = self.__class__.__module__ + '.' + self.__class__.__name__
        args, kwargs, extras = self.clone_data_args([], {}, [])
        self._clone_args = self._set_parameters(args, kwargs, cls, cls, extras)

        args, kwargs, cls_path, extras = self.map_input_args([], {}, cls, [])
        self._map_args = self._set_parameters(
                args, kwargs, cls, cls_path, extras)

    def _set_parameters(self, args, kwargs, cls, cls_path, extras):
        mod = '.'.join(cls_path.split('.')[:-1])
        cls = cls_path.split('.')[-1]
        func = pu.load_class(mod, cls).__init__

        argspec = inspect.getfullargspec(func)
        if len(argspec[0])-1 != len(args) + len(list(kwargs.keys())):
            raise Exception('Incorrect number of input arguments mapped.')

        data_lists = [True if isinstance(a, list) and isinstance(a[0], int)
                      else False for a in args]

        # If there are multiple data objects this is incompatible with
        # checkpointing.
        ddict = {}
        if args.count('self') > 2 or data_lists.count(True):
            ddict = None
        else:
            ddict['args'] = args
            ddict['kwargs'] = kwargs
            ddict['cls'] = cls_path
            ddict['extras'] = extras
        return ddict

    def clone_data_args(self, args, kwargs, extras):
        """ Gather all information required to keep this dataset after a
        plugin has completed (may require a conversion to a different
        data_type.
        """
        raise NotImplementedError("clone_data_args must be implemented.")

    def map_input_args(self, args, kwargs, cls, extras):
        """ Gather all information required to recreate a datatype: For
        checkpointing and cloning """
        args, kwargs, extras = self.clone_data_args(args, kwargs, extras)
        return args, kwargs, cls, extras

    def get_clone_args(self):
        return self._clone_args

    def get_map_args(self):
        return self._map_args

    def create_next_instance(self, newObj):
        dtype_dict = self.get_map_args()
        if dtype_dict is None:
            return None
        args, kwargs, cls, extras = self._get_parameters(dtype_dict)
        args = [newObj if isinstance(a, str) and a == 'self'
                else a for a in args]

        cls_split = cls.split('.')
        mod = '.'.join(cls_split[:-1])
        name = cls_split[-1]
        cls_inst = pu.load_class(mod, cls_name=name)
        newObj.data = cls_inst(*args, **kwargs)
        self._base_post_clone_updates(newObj.data, extras)

    def _base_post_clone_updates(self, obj, extras):
        self.__update_extra_params(obj, extras)
        self._post_clone_updates()

    def _post_clone_updates(self):
        pass

    def _get_parameters(self, dtype_dict):
        args = dtype_dict['args']
        kwargs = dtype_dict['kwargs']
        extras = dtype_dict['extras']
        args = [self._str_to_value(self, a) for a in args]

        extras = self.__get_extras_vals(extras)
        for key, value in kwargs.items():
            kwargs[key] = self._str_to_value(self, value)
        return args, kwargs, dtype_dict['cls'], extras

    def _str_to_value(self, obj, val):
        if not isinstance(val, str):
            return val
        if val == 'self':
            return val
        val = 'self' if val == 'DATA_OBJECT' else val
        val = val.replace('self.', '')
        temp = getattr(obj, val, val)
        return temp() if inspect.ismethod(temp) else temp

    def __get_extras_vals(self, vals):
        extras = {}
        for key in vals:
            extras[key] = getattr(self, key)
        return extras

    def __update_extra_params(self, newObj, extras):
        for key, value in extras.items():
            setattr(newObj, key, value)
