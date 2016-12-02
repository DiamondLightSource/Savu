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

