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
.. module:: data_notes
   :platform: Unix
   :synopsis: A module containing extended doc strings for the data module.
.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""


def set_preview_note():
    """
        Each ``preview_list`` element should be of the form
        ``start:stop:step:chunk``, where ``step`` and ``chunk`` are optional
        (default = 1) but both are required if chunk > 1.

        .. note::
            **start:stop[:step]**
                represents the set of indices specified by:

                >>> indices = range(start, stop[, step])
            For more information see :func:`range`

            **start:stop:step:chunk (chunk > 1)**
                represents the set of indices specified by:

                >>> a = np.tile(np.arange(start, stop, step), (chunk, 1))
                >>> b = np.transpose(np.tile(np.arange(chunk)-chunk/2, \
(a.shape[1], 1)))
                >>> indices = np.ravel(np.transpose(a + b))

                Chunk indicates how many values to take around each value in
                ``range(start, stop, step)``.  It is only available for slicing
                dimensions.

                .. warning:: If any indices are out of range (or negative)
                    then the list is invalid. When chunk > 1, new start and
                    end values will be:

                    >>> new_start = start - int(chunk/2)
                    >>> new_end = range(start, stop, step)[-1] + \
(step - int(chunk/2))

        **accepted values**:
            Each entry is executed using :func:`eval` so simple formulas are\
            allowed and may contain the following keywords:

            * ``:`` is a simplification for 0:end:1:1 (all values)
            * ``mid`` is int(shape[dim]/2)
            * ``end`` is shape[dim]
            * ``midmap`` is the ``mid`` of a mapped dimension (only relevant \
in a 'dimension mapping' loader)
    """
    pass
