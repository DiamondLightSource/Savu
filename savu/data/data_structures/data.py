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
.. module:: data
   :platform: Unix
   :synopsis: The Data class dynamically inherits from transport specific data\
   class and holds the data array, along with associated information.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import savu.core.utils as cu
from savu.data.meta_data import MetaData
import savu.data.data_structures.utils as dsu
from savu.data.data_structures.preview import Preview
from savu.data.data_structures.data_create import DataCreate


class Data(DataCreate):
    """The Data class dynamically inherits from transport specific data class
    and holds the data array, along with associated information.
    """

    def __init__(self, name, exp):
        super(Data, self).__init__(name)
        self.meta_data = MetaData()
        self.related = {}
        self.pattern_list = self.__get_available_pattern_list()
        self.data_info = MetaData()
        self.__initialise_data_info(name)
        self._preview = Preview(self)
        self.exp = exp
        self.group_name = None
        self.group = None
        self._plugin_data_obj = None
        self.raw = None
        self.backing_file = None
        self.data = None
        self.next_shape = None
        self.orig_shape = None
        self.previous_pattern = None
        self.transport_data = None

#    def get_data(self, related):
#        return self.related[related].data

    def __initialise_data_info(self, name):
        """ Initialise entries in the data_info meta data.
        """
        self.data_info.set('name', name)
        self.data_info.set('data_patterns', {})
        self.data_info.set('shape', None)
        self.data_info.set('nDims', None)

    def _set_plugin_data(self, plugin_data_obj):
        """ Encapsulate a PluginData object.
        """
        self._plugin_data_obj = plugin_data_obj

    def _clear_plugin_data(self):
        """ Set encapsulated PluginData object to None.
        """
        self._plugin_data_obj = None

    def _get_plugin_data(self):
        """ Get encapsulated PluginData object.
        """
        if self._plugin_data_obj is not None:
            return self._plugin_data_obj
        else:
            raise Exception("There is no PluginData object associated with "
                            "the Data object.")

    def get_preview(self):
        """ Get the Preview instance associated with the data object
        """
        return self._preview

    def _set_transport_data(self, transport):
        """ Import the data transport mechanism

        :returns: instance of data transport
        :rtype: transport_data
        """
        transport_data = "savu.data.transport_data." + transport + \
                         "_transport_data"
        transport_data = cu.import_class(transport_data)
        self.transport_data = transport_data(self)
        self.data_info.set('transport', transport)

    def _get_transport_data(self):
        return self.transport_data

    def __deepcopy__(self, memo):
        """ Copy the data object.
        """
        name = self.data_info.get('name')
        return dsu._deepcopy_data_object(self, Data(name, self.exp))

    def get_data_patterns(self):
        """ Get data patterns associated with this data object.

        :returns: A dictionary of associated patterns.
        :rtype: dict
        """
        return self.data_info.get('data_patterns')

    def _set_previous_pattern(self, pattern):
        self.previous_pattern = pattern

    def get_previous_pattern(self):
        return self.previous_pattern

    def set_shape(self, shape):
        """ Set the dataset shape.
        """
        self.data_info.set('shape', shape)
        self.__check_dims()

    def set_original_shape(self, shape):
        """ Set the original data shape before previewing
        """
        self.orig_shape = shape
        self.set_shape(shape)

    def get_original_shape(self):
        """
        Returns the original shape of the data before previewing
        
        Returns
        -------
        tuple
            Original data shape.
        """
        return self.orig_shape

    def get_shape(self):
        """ Get the dataset shape

        :returns: data shape
        :rtype: tuple
        """
        shape = self.data_info.get('shape')
        return shape

    def __check_dims(self):
        """ Check the ``shape`` and ``nDims`` entries in the data_info
        meta_data dictionary are equal.
        """
        nDims = self.data_info.get("nDims")
        shape = self.data_info.get('shape')
        if nDims:
            if len(shape) != nDims:
                error_msg = ("The number of axis labels, %d, does not "
                             "coincide with the number of data "
                             "dimensions %d." % (nDims, len(shape)))
                raise Exception(error_msg)

    def _set_name(self, name):
        self.data_info.set('name', name)

    def get_name(self, orig=False):
        """ Get data name.

        :keyword bool orig: Set this flag to true to return the original cloned
            dataset name if this dataset is a clone
        :returns: the name associated with the dataset
        :rtype: str
        """
        if orig:
            dinfo = self.data_info.get_dictionary()
            return dinfo['clone'] if 'clone' in dinfo.keys() else dinfo['name']
        return self.data_info.get('name')

    def __get_available_pattern_list(self):
        """ Get a list of ALL pattern names that are currently allowed in the
        framework.
        """
        pattern_list = dsu.get_available_pattern_types()
        return pattern_list

    def add_pattern(self, dtype, **kwargs):
        """ Add a pattern.

        :params str dtype: The *type* of pattern to add, which can be anything
            from the :const:`savu.data.data_structures.utils.pattern_list`
            :const:`pattern_list`
            :data:`savu.data.data_structures.utils.pattern_list`
            :data:`pattern_list`:
        :keyword tuple core_dims: Dimension indices of core dimensions
        :keyword tuple slice_dims: Dimension indices of slice dimensions
        """
        if dtype in self.pattern_list:
            nDims = 0
            for args in kwargs:
                dlen = len(kwargs[args])
                if not dlen:
                    raise Exception("Pattern Error: Pattern %s must have at"
                                    " least one %s" % (dtype, args))
                nDims += len(kwargs[args])
                self.data_info.set(['data_patterns', dtype, args],
                                   kwargs[args])

            self.__convert_pattern_dimensions(dtype)
            if self.get_shape():
                diff = len(self.get_shape()) - nDims
                if diff:
                    pattern = {dtype: self.get_data_patterns()[dtype]}
                    self._set_data_patterns(pattern)
                    nDims += diff
            try:
                if nDims != self.data_info.get("nDims"):
                    actualDims = self.data_info.get('nDims')
                    err_msg = ("The pattern %s has an incorrect number of "
                               "dimensions: %d required but %d specified."
                               % (dtype, actualDims, nDims))
                    raise Exception(err_msg)
            except KeyError:
                self.data_info.set('nDims', nDims)
        else:
            raise Exception("The data pattern '%s'does not exist. Please "
                            "choose from the following list: \n'%s'",
                            dtype, str(self.pattern_list))

    def add_volume_patterns(self, x, y, z):
        """ Adds volume patterns

        :params int x: dimension to be associated with x-axis
        :params int y: dimension to be associated with y-axis
        :params int z: dimension to be associated with z-axis
        """
        self.add_pattern("VOLUME_XZ", **self.__get_dirs_for_volume(x, z, y))

        if y:
            self.add_pattern(
                "VOLUME_YZ", **self.__get_dirs_for_volume(y, z, x))
            self.add_pattern(
                "VOLUME_XY", **self.__get_dirs_for_volume(x, y, z))

        if self.data_info.get("nDims") > 3 and y:
            self.add_pattern("VOLUME_3D", **self.__get_dirs_for_volume_3D())

    def __get_dirs_for_volume(self, dim1, dim2, sdir, dim3=None):
        """ Calculate core_dir and slice_dir for a volume pattern.
        """
        all_dims = range(self.data_info.get("nDims"))
        vol_dict = {}
        vol_dict['core_dims'] = (dim1, dim2)
        slice_dir = [sdir] if type(sdir) is int else []
        for ddir in all_dims:
            if ddir not in [dim1, dim2, sdir]:
                slice_dir.append(ddir)                
        vol_dict['slice_dims'] = tuple(slice_dir)
        return vol_dict

    def __get_dirs_for_volume_3D(self):
        # create volume 3D pattern here
        patterns = self.get_data_patterns()
        cdim = []
        for v in ['VOLUME_YZ', 'VOLUME_XY', 'VOLUME_XZ']:
            cdim += (patterns[v]['core_dims'])
            
        cdim = set(cdim)
        sdim = tuple(set(range(self.data_info.get("nDims"))).difference(cdim))
        return {"core_dims": tuple(cdim), "slice_dims": sdim}

    def set_axis_labels(self, *args):
        """ Set the axis labels associated with each data dimension.

        :arg str: Each arg should be of the form ``name.unit``. If ``name`` is\
        a data_obj.meta_data entry, it will be output to the final .nxs file.
        """
        self.data_info.set('nDims', len(args))
        axis_labels = []
        for arg in args:
            if isinstance(arg, dict):
                axis_labels.append(arg)
            else:
                try:
                    axis = arg.split('.')
                    axis_labels.append({axis[0]: axis[1]})
                except:
                    # data arrives here, but that may be an error
                    pass
        self.data_info.set('axis_labels', axis_labels)

    def get_axis_labels(self):
        """ Get axis labels.

        :returns: Axis labels
        :rtype: list(dict)
        """
        return self.data_info.get('axis_labels')

    def get_data_dimension_by_axis_label(self, name, contains=False, exists=False):
        """ Get the dimension of the data associated with a particular
        axis_label.

        :param str name: The name of the axis_label
        :keyword bool contains: Set this flag to true if the name is only part
            of the axis_label name
        :keyword bool exists: Set to True to return False rather than Exception
        :returns: The associated axis number
        :rtype: int
        """
        axis_labels = self.data_info.get('axis_labels')
        for i in range(len(axis_labels)):
            if contains is True:
                for names in list(axis_labels[i].keys()):
                    if name in names:
                        return i
            else:
                if name in list(axis_labels[i].keys()):
                    return i
        if exists:
            return False
        raise Exception("Cannot find the specifed axis label.")

    def _finalise_patterns(self):
        """ Adds a main axis (fastest changing) to SINOGRAM and PROJECTON
        patterns.
        """
        check = 0        
        check += self.__check_pattern('SINOGRAM')
        check += self.__check_pattern('PROJECTION')

        if check == 2 and len(self.get_shape()) > 2:
            self.__set_main_axis('SINOGRAM')
            self.__set_main_axis('PROJECTION')

    def __check_pattern(self, pattern_name):
        """ Check if a pattern exists.
        """
        patterns = self.get_data_patterns()
        try:
            patterns[pattern_name]
        except KeyError:
            return 0
        return 1

    def __convert_pattern_dimensions(self, dtype):
        """ Replace negative indices in pattern kwargs.
        """
        pattern = self.get_data_patterns()[dtype]
        if 'main_dir' in list(pattern.keys()):
            del pattern['main_dir']

        nDims = sum([len(i) for i in list(pattern.values())])
        for p in pattern:
            ddirs = pattern[p]
            pattern[p] = self._non_negative_directions(ddirs, nDims)

    def _non_negative_directions(self, ddirs, nDims):
        """ Replace negative indexing values with positive counterparts.

        :params tuple(int) ddirs: data dimension indices
        :params int nDims: The number of data dimensions
        :returns: non-negative data dimension indices
        :rtype: tuple(int)
        """
        index = [i for i in range(len(ddirs)) if ddirs[i] < 0]
        list_ddirs = list(ddirs)
        for i in index:
            list_ddirs[i] = nDims + ddirs[i]
        return tuple(list_ddirs)

    def __set_main_axis(self, pname):
        """ Set the ``main_dir`` pattern kwarg to the fastest changing
        dimension
        """
        patterns = self.get_data_patterns()
        n1 = 'PROJECTION' if pname == 'SINOGRAM' else 'SINOGRAM'
        d1 = patterns[n1]['core_dims']
        d2 = patterns[pname]['slice_dims']
        tdir = set(d1).intersection(set(d2))

        # this is required when a single sinogram exists in the mm case, and a
        # dimension is added via parameter tuning.
        if not tdir:
            tdir = [d2[0]]

        self.data_info.set(['data_patterns', pname, 'main_dir'], list(tdir)[0])

    def get_axis_label_keys(self):
        """ Get axis_label names

        :returns: A list containing associated axis names for each dimension
        :rtype: list(str)
        """
        axis_labels = self.data_info.get('axis_labels')
        axis_label_keys = []
        for labels in axis_labels:
            for key in list(labels.keys()):
                axis_label_keys.append(key)
        return axis_label_keys

    def amend_axis_label_values(self, slice_list):
        """ Amend all axis label values based on the slice_list parameter.\
        This is required if the data is reduced.
        """
        axis_labels = self.get_axis_labels()
        for i in range(len(slice_list)):
            label = list(axis_labels[i].keys())[0]
            if label in list(self.meta_data.get_dictionary().keys()):
                values = self.meta_data.get(label)
                preview_sl = [slice(None)]*len(values.shape)
                preview_sl[0] = slice_list[i]
                self.meta_data.set(label, values[tuple(preview_sl)])

    def get_core_dimensions(self):
        """ Get the core data dimensions associated with the current pattern.

        :returns: value associated with pattern key ``core_dims``
        :rtype: tuple
        """
        return list(self._get_plugin_data().get_pattern().values())[0]['core_dims']

    def get_slice_dimensions(self):
        """ Get the slice data dimensions associated with the current pattern.

        :returns: value associated with pattern key ``slice_dims``
        :rtype: tuple
        """
        return list(self._get_plugin_data().get_pattern().values())[0]['slice_dims']

    def get_itemsize(self):
        """ Returns bytes per entry """
        dtype = self.get_dtype()
        if not dtype:
            self.set_dtype(None)
            dtype = self.get_dtype()
        return self.get_dtype().itemsize
