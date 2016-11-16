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
Turns the astra root directory into a module, which sets relevant paths 
and imports pyastra.  This avoids having to set the paths when using Savu.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import os, sys
os.environ['LD_LIBRARY_PATH'] = __path__[0] + '/../../lib:' + os.environ['LD_LIBRARY_PATH']
try:
    os.execv(sys.argv[0], sys.argv)
except Exception, exc:
    print 'Failed re-exec:', exc
    sys.exit(1)

#-----------------------------------------------------------------------
#Copyright 2013 Centrum Wiskunde & Informatica, Amsterdam
#
#Author: Daniel M. Pelt
#Contact: D.M.Pelt@cwi.nl
#Website: http://dmpelt.github.io/pyastratoolbox/
#
#
#This file is part of the Python interface to the
#All Scale Tomographic Reconstruction Antwerp Toolbox ("ASTRA Toolbox").
#
#The Python interface to the ASTRA Toolbox is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#The Python interface to the ASTRA Toolbox is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with the Python interface to the ASTRA Toolbox. If not, see <http://www.gnu.org/licenses/>.
#
#-----------------------------------------------------------------------


from . import matlab as m
from .creators import astra_dict,create_vol_geom, create_proj_geom, create_backprojection, create_sino, create_reconstruction, create_projector,create_sino3d_gpu, create_backprojection3d_gpu
from .functions import data_op, add_noise_to_sino, clear, move_vol_geom
from .extrautils import clipCircle
from . import data2d
from . import astra
from . import data3d
from . import algorithm
from . import projector
from . import projector3d
from . import matrix
from . import log
from .optomo import OpTomo


import os
try:
    astra.set_gpu_index(int(os.environ['ASTRA_GPU_INDEX']))
except KeyError:
    pass

