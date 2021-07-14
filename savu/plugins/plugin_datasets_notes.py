# Copyright 2015 Diamond Light Source Ltd.
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
.. module:: plugin_datasets_notes
   :platform: Unix
   :synopsis: A module containing extended doc strings for the data module.
.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""


def datasets_notes():
    """ Get {0} objects associated with the {1}_datasets.

    :returns: A list of all {0} objects associated with {1}_datasets for the
        current plugin.
    :rtype: list({0})
    """


def two_datasets_notes():
    """ Get {0} objects associated with in_datasets and
    out_datasets.

    :returns: Two lists of all {0} objects associated with
        in_datasets and out_datasets respectively.
    :rtype: list({0}(in_datasets)), list({0}(out_datasets))
    """


def mData_notes():
    """ Get a list of meta_data objects associated with the {0}_datasets.

    :returns: All MetaData objects associated with {0} data objects.
    :rtype: list(MetaData)
    """
