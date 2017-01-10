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


class BaseType(object):

    def __getitem__(self, index):
        """ Override __getitem__ and map to the relevant files """
        raise NotImplementedError("__getitem__ must be implemented.")

    def get_shape(self):
        """ Get full stiched shape of a stack of files"""
        raise NotImplementedError("get_shape must be implemented.")

    def add_base_class_with_instance(self, base, inst):
        """ Add a base class instance to a class (merging of two data types).

        :params class base: a class to add as a base class
        :params instance inst: a instance of the base class
        """
        cls = self.__class__
        namespace = self.__class__.__dict__.copy()
        self.__dict__.update(inst.__dict__)
        self.__class__ = cls.__class__(cls.__name__, (cls, base), namespace)
