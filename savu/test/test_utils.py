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
.. module:: test_utils
   :platform: Unix
   :synopsis: utilities for the test framework

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""

import inspect
import os
from savu.data.structures import RawTimeseriesData


def get_test_data_path(name):
    """Gets the full path to the test data

    :param name: The name of the test file.
    :type name: str
    :returns:  The full path to the example data.

    """
    path = inspect.stack()[0][1]
    return '/'.join(os.path.split(path)[0].split(os.sep)[:-2] +
                    ['test_data', name])


def get_nexus_test_data():
    """Gets the test data and returns it in the RawData Structure

    :returns:  a RawData Object containing the example data.

    """
    path = get_test_data_path('24737.nxs')
    raw_timeseries_data = RawTimeseriesData()
    raw_timeseries_data.populate_from_nexus(path)
    return raw_timeseries_data
