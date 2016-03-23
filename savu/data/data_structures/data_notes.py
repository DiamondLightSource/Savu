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


def _set_preview_note():
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


def image_key():
    """
        This is a helper function to be used after :meth:`savu.data.\
data_structures.data_create.DataCreate.create_dataset`,

            >>> out_dataset.create_dataset(in_dataset)
            >>> out_dataset.trim_output_data(in_dataset, image_key=0)

        if in_dataset is a plugin input dataset with an image_key and 0 is the
        data index.
    """


def _create():
    """
    .. note:: **Creating a dataset**
            Each new dataset requires the following information:

            * ``shape``
            * ``axis_labels``
            * ``patterns``

        This function can be used to setup the required information in one
        of two ways:

            1. Passing a ``Data`` object as the only argument: All required
            information is coped from this data object. For example,

                >>> out_dataset[0].create_dataset(in_dataset[0])

            2. Passing kwargs: ``shape`` and ``axis_labels`` are required
            (see above for other optional arguments). For example,

                >>> out_dataset[0].create_dataset(axis_labels=labels, \
shape=new_shape)

        .. warning:: If ``pattern`` keyword is not used, patterns must be added
            after  :meth:`~savu.data.data_structures.data_create.DataCreate.\
create_dataset` by calling :func:`~savu.data.data_structures.data.Data.\
add_pattern`.
    """


def _shape():
    """
    .. note::
        **``shape`` keyword argument**
            Options to pass are:

            1. Data object: Copy shape from the Data object.
            2. tuple: Define shape explicity.
    """


def axis_labels():
    """
    .. note::
        **``axis_labels`` keyword argument**
            Options to pass are:

            1. Data object: Copy all labels from the Data object.
            2. {Data_obj: list}: Copy labels from the Data object and then
                remove or insert.
                * To remove dimensions: list = ['dim1', 'dim2', ...]
                    For example, to remove the first and last axis_labels from
                    the copied list:

                    >>> out_dataset.create_dataset(axis_labels=\
{in_dataset: ['1', '-1']), shape=new_shape})


                * To add/replace dimensions: list = \
['dim1.name.unit', 'dim2.name.unit', ...]. For example,

                    >>> out_dataset.create_dataset(axis_labels={in_dataset: \
['2.det_x.pixel', '3.det_y.pixel']}, shape=new_shape)

            3. list: Where each element is of the form 'dim.name.unit'. For
            example,

                >>> out_dataset.create_dataset(axis_labels=['1.rotation.deg', \
'2.det_x.pixel', '3.det_y.pixel'], shape=new_shape)

    """
