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
Get the Savu version
"""

# from pkg_resources import get_distribution
#
# __version__ = get_distribution('savu').version

import os

path = os.path.abspath(os.path.dirname(__file__))
thepath = path + '/../install/'
thepath = thepath if os.path.exists(thepath) else path + '/install/'

with open(thepath + 'latest_version.txt', 'r') as f:
    version_file = f.readline().strip()
    with open(thepath + version_file, 'r') as f2:
        __version__ = f2.readline().strip()

__install__ = 'install/' + '_'.join(__version__.split('.')) + '_install'
