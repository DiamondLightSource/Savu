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
import tempfile
import os

import savu.plugins.utils as pu

from savu.data.structures import Data
from savu.data.structures import RawTimeseriesData, ProjectionData, VolumeData


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

    :returns:  a RawTimeseriesData Object containing the example data.

    """
    path = get_test_data_path('24737.nxs')
    raw_timeseries_data = RawTimeseriesData()
    raw_timeseries_data.populate_from_nexus(path)
    return raw_timeseries_data


def get_projection_test_data():
    """Gets the test data and returns it in the ProjectionData Structure

    :returns:  a ProjectionData Object containing the example data.

    """
    path = get_test_data_path('projections.h5')
    projection_data = ProjectionData()
    projection_data.populate_from_h5(path)
    return projection_data


def get_appropriate_input_data(plugin):
    data = []
    if plugin.required_data_type() == RawTimeseriesData:
        data.append(get_nexus_test_data())
    elif plugin.required_data_type() == ProjectionData:
        data.append(get_projection_test_data())
    elif plugin.required_data_type() == Data:
        data.append(get_nexus_test_data())
        data.append(get_projection_test_data())
    return data


def get_appropriate_output_data(plugin, data, mpi=False, file_name=None):
    output = []
    temp_file = file_name
    if temp_file is None:
        temp_file = tempfile.NamedTemporaryFile(suffix='.h5', delete=False)
        temp_file = temp_file.name

    if plugin.output_data_type() == RawTimeseriesData:
        output.append(pu.get_raw_data(data[0], temp_file,
                                      plugin.name, mpi))

    elif plugin.output_data_type() == ProjectionData:
        output.append(pu.get_projection_data(data[0], temp_file,
                                             plugin.name, mpi))

    elif plugin.output_data_type() == VolumeData:
        output.append(pu.get_volume_data(data[0], temp_file,
                                         plugin.name, mpi))

    elif plugin.output_data_type() == Data:
        for datum in data:
            if file_name is None:
                temp_file = tempfile.NamedTemporaryFile(suffix='.h5',
                                                        delete=False)
                temp_file = temp_file.name

            if isinstance(datum, RawTimeseriesData):
                output.append(pu.get_raw_data(datum, temp_file,
                                              plugin.name, mpi))

            elif isinstance(datum, ProjectionData):
                output.append(pu.get_projection_data(datum,
                                                     temp_file, plugin.name,
                                                     mpi))

            elif isinstance(datum, VolumeData):
                output.append(pu.get_volume_data(datum, temp_file,
                                                 plugin.name, mpi))
    return output
