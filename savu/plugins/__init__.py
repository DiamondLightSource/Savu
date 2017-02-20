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
All the plugin architecture for Savu is contained here


.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""

from . import absorption_corrections
from . import analysis
from . import azimuthal_integrators
from . import component_analysis
from . import corrections
from . import developing
from . import driver
from . import filters
from . import fitters
from . import fluo_fitters
from . import loaders
from . import basic_operations
from . import ptychography
from . import reconstructions
from . import reshape
from . import savers

