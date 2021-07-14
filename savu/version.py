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
import os
import pathlib

# for the savu_installer
savu_path = pathlib.Path(__file__).parent.absolute()
__install__ = "install/savu_hpc/savu_installer"
with open(os.path.join(
        os.path.join(savu_path, "..", __install__, "version.txt"))) as f:
    __version__ = f.readline().strip()
