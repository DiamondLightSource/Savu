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
.. module:: utils
   :platform: Unix
   :synopsis: Utilities for plugin management

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""

import sys


def load_plugin(path, name):
    """Load a plugin.

    :param path: The full path in which the plugin resides,\
                    or None if an internal plugin.
    :type path: str.
    :param name: Name of the plugin to import.
    :type name: str.
    :returns:  An instance of the class described by the named plugin

    """

    if (path is not None) and (path not in sys.path):
        sys.path.append(path)
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    clazz = getattr(mod, (name.split('.')[-1]).capitalize())
    instance = clazz()
    return instance
