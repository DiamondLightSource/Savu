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
.. module:: plugin
   :platform: Unix
   :synopsis: Base class for all plugins used by Savu

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""

import logging


class Plugin(object):
    """
    The base class from which all plugins should inherit.

    """

    def __init__(self):
        super(Plugin, self).__init__()

    def setup(self, data):
        """
        This method is called after the plugin has been created by the
        pipeline framework
        """
        logging.error("Setup needs to be implemented")
        raise NotImplementedError("Setup needs to be implemented")
