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
        self._input_args = {}
        self.base_map_input_args()

    def __getitem__(self, index):
        """ Override __getitem__ and map to the relevant files """
        raise NotImplementedError("__getitem__ must be implemented.")

    def get_shape(self):
        """ Get full stiched shape of a stack of files"""
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

    def base_map_input_args(self):
        """ Create a dictionary of required input arguments, required for
        checkpointing. """
        cls = self.__class__.__module__ + '.' + self.__class__.__name__
        args, kwargs, cls_path = self.map_input_args([], {}, cls)

        mod = '.'.join(cls_path.split('.')[:-1])
        cls = cls_path.split('.')[-1]
        func = pu.load_class(mod, cls).__init__

        argspec = inspect.getargspec(func)
        if len(argspec[0])-1 != len(args) + len(kwargs.keys()):
            raise Exception('Incorrect number of input arguments mapped.')

        data_lists = [True if isinstance(a, list) and isinstance(a[0], int)
                      else False for a in args]

        # If there are multiple data objects this is incompatible with
        # checkpointing.
        if args.count('self') > 2 or data_lists.count(True):
            self._input_args = None
        else:
            self._input_args['args'] = args
            self._input_args['kwargs'] = kwargs
            self._input_args['cls'] = cls_path

    def map_input_args(self, args, kwargs):
        """ Create a dictionary of required input arguments, required for
        checkpointing. """
        raise NotImplementedError("map_required_inputs must be implemented.")

    def get_required_args(self):
        return self._input_args

    def create_clone(self, newObj):
        dtype_dict = self.get_required_args()
        if dtype_dict is None:
            return None
        args, kwargs, cls = self._get_clone_parameters()
        args = [newObj if a == 'self' else a for a in args]
        cls_split = cls.split('.')
        mod = '.'.join(cls_split[:-1])
        name = cls_split[-1]
        cls_inst = pu.load_class(mod, cls_name=name)
        newObj.data = cls_inst(*args, **kwargs)

    def _get_clone_parameters(self):
        dtype_dict = self.get_required_args()
        args = dtype_dict['args']
        kwargs = dtype_dict['kwargs']
        args = [self.__str_to_value(self, a) for a in args]
        for key, value in kwargs.iteritems():
            kwargs[key] = self.__str_to_value(self, value)
        return args, kwargs, dtype_dict['cls']

    def __str_to_value(self, obj, val):
        if not isinstance(val, str):
            return val
        if val == 'self':
            return val
        val = 'self' if val == 'DATA_OBJECT' else val
        val = val.replace('self.', '')
        temp = getattr(obj, val, val)
        return temp() if inspect.ismethod(temp) else temp
