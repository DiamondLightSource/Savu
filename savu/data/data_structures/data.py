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

import savu.data.data_structures.utils as dsu
import savu.core.utils as cu
from savu.data.meta_data import MetaData
from savu.data.data_structures.data_create import DataCreate
from savu.data.data_structures.preview import Preview


class Data(DataCreate):
    """The Data class dynamically inherits from transport specific data class
    and holds the data array, along with associated information.
    """

    def __init__(self, name, exp):
        super(Data, self).__init__(name)
        self.meta_data = MetaData()
        self.pattern_list = self.__get_available_pattern_list()
        self.data_info = MetaData()
        self.__initialise_data_info(name)
        self._preview = Preview(self)
        self.exp = exp
        self.group_name = None
        self.group = None
        self._plugin_data_obj = None
        self.tomo_raw_obj = None
        #self.data_mapping = None
        self.backing_file = None
        self.data = None
        self.next_shape = None
        #self.mapping = None
        #self.map_dim = []

    def __initialise_data_info(self, name):
        """ Initialise entries in the data_info meta data.
        """
        self.data_info.set_meta_data('name', name)
        self.data_info.set_meta_data('data_patterns', {})
        self.data_info.set_meta_data('shape', None)
        self.data_info.set_meta_data('nDims', None)

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

    def _get_transport_data(self):
        """ Import the data transport mechanism

        :returns: instance of data transport
        :rtype: transport_data
        """
        transport = self.exp.meta_data.get_meta_data("transport")
        transport_data = "savu.data.transport_data." + transport + \
                         "_transport_data"
        return cu.import_class(transport_data)

    def __deepcopy__(self, memo):
        """ Copy the data object.
        """
        name = self.data_info.get_meta_data('name')
        return dsu._deepcopy_data_object(self, Data(name, self.exp))

    def get_data_patterns(self):
        """ Get data patterns associated with this data object.

        :returns: A dictionary of associated patterns.
        :rtype: dict
        """
        return self.data_info.get_meta_data('data_patterns')

    def set_shape(self, shape):
        """ Set the dataset shape.
        """
        self.data_info.set_meta_data('shape', shape)
        self.__check_dims()

    def get_shape(self):
        """ Get the dataset shape

        :returns: data shape
        :rtype: tuple
        """
        shape = self.data_info.get_meta_data('shape')
        return shape

    def __check_dims(self):
        """ Check the ``shape`` and ``nDims`` entries in the data_info
        meta_data dictionary are equal.
        """
        nDims = self.data_info.get_meta_data("nDims")
        shape = self.data_info.get_meta_data('shape')
        if nDims:
            if len(shape) != nDims:
                error_msg = ("The number of axis labels, %d, does not "
                             "coincide with the number of data "
                             "dimensions %d." % (nDims, len(shape)))
                raise Exception(error_msg)

    def get_name(self):
        """ Get data name.

        :returns: the name associated with the dataset
        :rtype: str
        """
        return self.data_info.get_meta_data('name')

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
        :keyword tuple core_dir: Dimension indices of core dimensions
        :keyword tuple slice_dir: Dimension indices of slice dimensions
        """
        if dtype in self.pattern_list:
            nDims = 0
            for args in kwargs:
                nDims += len(kwargs[args])
                self.data_info.set_meta_data(['data_patterns', dtype, args],
                                             kwargs[args])
            
            self.__convert_pattern_directions(dtype)
            if self.get_shape():
                diff = len(self.get_shape()) - nDims
                if diff:
                    pattern = {dtype: self.get_data_patterns()[dtype]}
                    self._add_extra_dims_to_patterns(pattern)
                    nDims += diff
            try:
                if nDims != self.data_info.get_meta_data("nDims"):
                    actualDims = self.data_info.get_meta_data('nDims')
                    err_msg = ("The pattern %s has an incorrect number of "
                               "dimensions: %d required but %d specified."
                               % (dtype, actualDims, nDims))
                    raise Exception(err_msg)
            except KeyError:
                self.data_info.set_meta_data('nDims', nDims)
        else:
            raise Exception("The data pattern '%s'does not exist. Please "
                            "choose from the following list: \n'%s'",
                            dtype, str(self.pattern_list))

    def add_volume_patterns(self, x, y, z):
        """ Adds 3D volume patterns

        :params int x: dimension to be associated with x-axis
        :params int y: dimension to be associated with y-axis
        :params int z: dimension to be associated with z-axis
        """
        self.add_pattern("VOLUME_YZ", **self.__get_dirs_for_volume(y, z, x))
        self.add_pattern("VOLUME_XZ", **self.__get_dirs_for_volume(x, z, y))
        self.add_pattern("VOLUME_XY", **self.__get_dirs_for_volume(x, y, z))

    def __get_dirs_for_volume(self, dim1, dim2, sdir):
        """ Calculate core_dir and slice_dir for a 3D volume pattern.
        """
        all_dims = range(len(self.get_shape()))
        vol_dict = {}
        vol_dict['core_dir'] = (dim1, dim2)
        slice_dir = [sdir]
        # *** need to add this for other patterns
        for ddir in all_dims:
            if ddir not in [dim1, dim2, sdir]:
                slice_dir.append(ddir)
        vol_dict['slice_dir'] = tuple(slice_dir)
        return vol_dict

    def set_axis_labels(self, *args):
        """ Set the axis labels associated with each data dimension.

        :arg str: Each arg should be of the form ``name.unit``. If ``name`` is\
        a data_obj.meta_data entry, it will be output to the final .nxs file.
        """
        self.data_info.set_meta_data('nDims', len(args))
        axis_labels = []
        for arg in args:
            try:
                axis = arg.split('.')
                axis_labels.append({axis[0]: axis[1]})
            except:
                # data arrives here, but that may be an error
                pass
        self.data_info.set_meta_data('axis_labels', axis_labels)

    def get_axis_labels(self):
        """ Get axis labels.

        :returns: Axis labels
        :rtype: list(dict)
        """
        return self.data_info.get_meta_data('axis_labels')

    def find_axis_label_dimension(self, name, contains=False):
        """ Get the dimension of the data associated with a particular
        axis_label.

        :param str name: The name of the axis_label
        :keyword bool contains: Set this flag to true if the name is only part
            of the axis_label name
        :returns: The associated axis number
        :rtype: int
        """
        axis_labels = self.data_info.get_meta_data('axis_labels')
        for i in range(len(axis_labels)):
            if contains is True:
                for names in axis_labels[i].keys():
                    if name in names:
                        return i
            else:
                if name in axis_labels[i].keys():
                    return i
        raise Exception("Cannot find the specifed axis label.")

    def _finalise_patterns(self):
        """ Adds a main axis (fastest changing) to SINOGRAM and PROJECTON
        patterns.
        """
        check = 0
        check += self.__check_pattern('SINOGRAM')
        check += self.__check_pattern('PROJECTION')

        if check is 2 and len(self.get_shape()) > 2:
            self.__set_main_axis('SINOGRAM')
            self.__set_main_axis('PROJECTION')
        elif check is 1:
            pass

    def __check_pattern(self, pattern_name):
        """ Check if a pattern exists.
        """
        patterns = self.get_data_patterns()
        try:
            patterns[pattern_name]
        except KeyError:
            return 0
        return 1

    def __convert_pattern_directions(self, dtype):
        """ Replace negative indices in pattern kwargs.
        """
        pattern = self.get_data_patterns()[dtype]
        if 'main_dir' in pattern.keys():
            del pattern['main_dir']

        nDims = sum([len(i) for i in pattern.values()])
        for p in pattern:
            ddirs = pattern[p]
            pattern[p] = self.non_negative_directions(ddirs, nDims)

    def non_negative_directions(self, ddirs, nDims):
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
        n1 = 'PROJECTION' if pname is 'SINOGRAM' else 'SINOGRAM'
        d1 = patterns[n1]['core_dir']
        d2 = patterns[pname]['slice_dir']
        tdir = set(d1).intersection(set(d2))

        # this is required when a single sinogram exists in the mm case, and a
        # dimension is added via parameter tuning.
        if not tdir:
            tdir = [d2[0]]

        self.data_info.set_meta_data(['data_patterns', pname, 'main_dir'],
                                     list(tdir)[0])

    def get_axis_label_keys(self):
        """ Get axis_label names

        :returns: A list containing associated axis names for each dimension
        :rtype: list(str)
        """
        axis_labels = self.data_info.get_meta_data('axis_labels')
        axis_label_keys = []
        for labels in axis_labels:
            for key in labels.keys():
                axis_label_keys.append(key)
        return axis_label_keys

    def _get_current_and_next_patterns(self, datasets_lists):
        """ Get the current and next patterns associated with a dataset
        throughout the processing chain.
        """
        current_datasets = datasets_lists[0]
        patterns_list = []
        for current_data in current_datasets['out_datasets']:
            current_name = current_data['name']
            current_pattern = current_data['pattern']
            next_pattern = self.__find_next_pattern(datasets_lists[1:],
                                                    current_name)
            patterns_list.append({'current': current_pattern,
                                  'next': next_pattern})
        self.exp.meta_data.set_meta_data('current_and_next', patterns_list)

    def __find_next_pattern(self, datasets_lists, current_name):
        next_pattern = []
        for next_data_list in datasets_lists:
            for next_data in next_data_list['in_datasets']:
                if next_data['name'] == current_name:
                    next_pattern = next_data['pattern']
                    return next_pattern
        return next_pattern

    def get_slice_directions(self):
        """ Get pattern slice_dir of pattern currently associated with the
        dataset (if any).

        :returns: the slicing dimensions.
        :rtype: tuple(int)
        """
        return self._get_plugin_data().get_slice_directions()
