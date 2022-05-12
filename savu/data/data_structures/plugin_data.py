# Copyright 201i Diamond Light Source Ltd.
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
.. module:: plugin_data
   :platform: Unix
   :synopsis: Contains the PluginData class. Each Data set used in a plugin \
       has a PluginData object encapsulated within it, for the duration of a \
       plugin run.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""
import sys
import copy
import h5py
import logging
import numpy as np

from savu.data.meta_data import MetaData
from savu.data.data_structures.data_add_ons import Padding


class PluginData(object):
    """ The PluginData class contains plugin specific information about a Data
    object for the duration of a plugin.  An instance of the class is
    encapsulated inside the Data object during the plugin run
    """

    def __init__(self, data_obj, plugin=None):
        self.data_obj = data_obj
        self._preview = None
        self.data_obj._set_plugin_data(self)
        self.meta_data = MetaData()
        self.padding = None
        self.pad_dict = None
        self.shape = None
        self.core_shape = None
        self.multi_params = {}
        self.extra_dims = []
        self._plugin = plugin
        self.fixed_dims = True
        self.split = None
        self.boundary_padding = None
        self.no_squeeze = False
        self.pre_tuning_shape = None
        self._frame_limit = None
        self._increase_rank = 0

    def _get_preview(self):
        return self._preview

    def get_total_frames(self):
        """ Get the total number of frames to process (all MPI processes).

        :returns: Number of frames
        :rtype: int
        """
        temp = 1
        slice_dir = \
            self.data_obj.get_data_patterns()[
                self.get_pattern_name()]["slice_dims"]
        for tslice in slice_dir:
            temp *= self.data_obj.get_shape()[tslice]
        return temp

    def __set_pattern(self, name, first_sdim=None):
        """ Set the pattern related information in the meta data dict.
        """
        pattern = self.data_obj.get_data_patterns()[name]
        self.meta_data.set("name", name)
        self.meta_data.set("core_dims", pattern['core_dims'])
        self.__set_slice_dimensions(first_sdim=first_sdim)

    def get_pattern_name(self):
        """ Get the pattern name.

        :returns: the pattern name
        :rtype: str
        """
        try:
            name = self.meta_data.get("name")
            return name
        except KeyError:
            raise Exception("The pattern name has not been set.")

    def get_pattern(self):
        """ Get the current pattern.

        :returns: dict of the pattern name against the pattern.
        :rtype: dict
        """
        pattern_name = self.get_pattern_name()
        return {pattern_name: self.data_obj.get_data_patterns()[pattern_name]}

    def __set_shape(self):
        """ Set the shape of the plugin data processing chunk.
        """
        core_dir = self.data_obj.get_core_dimensions()
        slice_dir = self.data_obj.get_slice_dimensions()
        dirs = list(set(core_dir + (slice_dir[0],)))
        slice_idx = dirs.index(slice_dir[0])
        dshape = self.data_obj.get_shape()
        shape = []
        for core in set(core_dir):
            shape.append(dshape[core])
        self.__set_core_shape(tuple(shape))

        mfp = self._get_max_frames_process()
        if mfp > 1 or self._get_no_squeeze():
            shape.insert(slice_idx, mfp)
        self.shape = tuple(shape)

    def _set_shape_transfer(self, slice_size):
        dshape = self.data_obj.get_shape()
        shape_before_tuning = self._get_shape_before_tuning()
        add = [1]*(len(dshape) - len(shape_before_tuning))
        slice_size = slice_size + add

        core_dir = self.data_obj.get_core_dimensions()
        slice_dir = self.data_obj.get_slice_dimensions()
        shape = [None]*len(dshape)
        for dim in core_dir:
            shape[dim] = dshape[dim]
        i = 0
        for dim in slice_dir:
            shape[dim] = slice_size[i]
            i += 1
        return tuple(shape)

    def __get_slice_size(self, mft):
        """ Calculate the number of frames transfer in each dimension given
            mft. """
        dshape = list(self.data_obj.get_shape())

        if 'fixed_dimensions' in list(self.meta_data.get_dictionary().keys()):
            fixed_dims = self.meta_data.get('fixed_dimensions')
            for d in fixed_dims:
                dshape[d] = 1

        dshape = [dshape[i] for i in self.meta_data.get('slice_dims')]
        size_list = [1]*len(dshape)
        i = 0

        while(mft > 1 and i < len(size_list)):
            size_list[i] = min(dshape[i], mft)
            mft //= np.prod(size_list) if np.prod(size_list) > 1 else 1
            i += 1
            
        # case of fixed integer max_frames, where max_frames > nSlices
        if mft > 1:
            size_list[0] *= mft

        self.meta_data.set('size_list', size_list)
        return size_list

    def set_bytes_per_frame(self):
        """ Return the size of a single frame in bytes. """
        nBytes = self.data_obj.get_itemsize()
        dims = list(self.get_pattern().values())[0]['core_dims']
        frame_shape = [self.data_obj.get_shape()[d] for d in dims]
        b_per_f = np.prod(frame_shape)*nBytes
        return frame_shape, b_per_f

    def get_shape(self):
        """ Get the shape of the data (without padding) that is passed to the
        plugin process_frames method.
        """
        return self.shape

    def _set_padded_shape(self):
        pass

    def get_padded_shape(self):
        """ Get the shape of the data (with padding) that is passed to the
        plugin process_frames method.
        """
        return self.shape

    def get_shape_transfer(self):
        """ Get the shape of the plugin data to be transferred each time.
        """
        return self.meta_data.get('transfer_shape')

    def __set_core_shape(self, shape):
        """ Set the core shape to hold only the shape of the core dimensions
        """
        self.core_shape = shape

    def get_core_shape(self):
        """ Get the shape of the core dimensions only.

        :returns: shape of core dimensions
        :rtype: tuple
        """
        return self.core_shape

    def _set_shape_before_tuning(self, shape):
        """ Set the shape of the full dataset used during each run of the \
        plugin (i.e. ignore extra dimensions due to parameter tuning). """
        self.pre_tuning_shape = shape

    def _get_shape_before_tuning(self):
        """ Return the shape of the full dataset used during each run of the \
        plugin (i.e. ignore extra dimensions due to parameter tuning). """
        return self.pre_tuning_shape if self.pre_tuning_shape else\
            self.data_obj.get_shape()

    def __check_dimensions(self, indices, core_dir, slice_dir, nDims):
        if len(indices) is not len(slice_dir):
            sys.exit("Incorrect number of indices specified when accessing "
                     "data.")

        if (len(core_dir)+len(slice_dir)) is not nDims:
            sys.exit("Incorrect number of data dimensions specified.")

    def __set_slice_dimensions(self, first_sdim=None):
        """ Set the slice dimensions in the pluginData meta data dictionary.\
        Reorder pattern slice_dims to ensure first_sdim is at the front.
        """
        pattern = self.data_obj.get_data_patterns()[self.get_pattern_name()]
        slice_dims = pattern['slice_dims']

        if first_sdim:
            slice_dims = list(slice_dims)
            first_sdim = \
                self.data_obj.get_data_dimension_by_axis_label(first_sdim)
            slice_dims.insert(0, slice_dims.pop(slice_dims.index(first_sdim)))
            pattern['slice_dims'] = tuple(slice_dims)

        self.meta_data.set('slice_dims', tuple(slice_dims))

    def get_slice_dimension(self):
        """
        Return the position of the slice dimension in relation to the data
        handed to the plugin.
        """
        core_dirs = self.data_obj.get_core_dimensions()
        slice_dir = self.data_obj.get_slice_dimensions()[0]
        return list(set(core_dirs + (slice_dir,))).index(slice_dir)

    def get_data_dimension_by_axis_label(self, label, contains=False):
        """
        Return the dimension of the data in the plugin that has the specified
        axis label.
        """
        label_dim = self.data_obj.get_data_dimension_by_axis_label(
                label, contains=contains)
        plugin_dims = self.data_obj.get_core_dimensions()
        if self._get_max_frames_process() > 1 or self.max_frames == 'multiple':
            plugin_dims += (self.get_slice_dimension(),)
        return list(set(plugin_dims)).index(label_dim)

    def set_slicing_order(self, order):  # should this function be deleted?
        """
        Reorder the slice dimensions.  The fastest changing slice dimension
        will always be the first one stated in the pattern key ``slice_dir``.
        The input param is a tuple stating the desired order of slicing
        dimensions relative to the current order.
        """
        slice_dirs = self.data_obj.get_slice_dimensions()
        if len(slice_dirs) < len(order):
            raise Exception("Incorrect number of dimensions specifed.")
        ordered = [slice_dirs[o] for o in order]
        remaining = [s for s in slice_dirs if s not in ordered]
        new_slice_dirs = tuple(ordered + remaining)
        self.get_pattern()['slice_dir'] = new_slice_dirs

    def get_core_dimensions(self):
        """
        Return the position of the core dimensions in relation to the data
        handed to the plugin.
        """
        core_dims = self.data_obj.get_core_dimensions()
        first_slice_dim = (self.data_obj.get_slice_dimensions()[0],)
        plugin_dims = np.sort(core_dims + first_slice_dim)
        return np.searchsorted(plugin_dims, np.sort(core_dims))

    def set_fixed_dimensions(self, dims, values):
        """ Fix a data direction to the index in values list.

        :param list(int) dims: Directions to fix
        :param list(int) value: Index of fixed directions
        """
        slice_dirs = self.data_obj.get_slice_dimensions()
        if set(dims).difference(set(slice_dirs)):
            raise Exception("You are trying to fix a direction that is not"
                            " a slicing direction")
        self.meta_data.set("fixed_dimensions", dims)
        self.meta_data.set("fixed_dimensions_values", values)
        self.__set_slice_dimensions()
        shape = list(self.data_obj.get_shape())
        for dim in dims:
            shape[dim] = 1
        self.data_obj.set_shape(tuple(shape))
        #self.__set_shape()

    def _get_fixed_dimensions(self):
        """ Get the fixed data directions and their indices

        :returns: Fixed directions and their associated values
        :rtype: list(list(int), list(int))
        """
        fixed = []
        values = []
        if 'fixed_dimensions' in self.meta_data.get_dictionary():
            fixed = self.meta_data.get("fixed_dimensions")
            values = self.meta_data.get("fixed_dimensions_values")
        return [fixed, values]

    def _get_data_slice_list(self, plist):
        """ Convert a plugin data slice list to a slice list for the whole
        dataset, i.e. add in any missing dimensions.
        """
        nDims = len(self.get_shape())
        all_dims = self.get_core_dimensions() + self.get_slice_dimension()
        extra_dims = all_dims[nDims:]
        dlist = list(plist)
        for i in extra_dims:
            dlist.insert(i, slice(None))
        return tuple(dlist)

    def _get_max_frames_process(self):
        """ Get the number of frames to process for each run of process_frames.

        If the number of frames is not divisible by the previewing ``chunk``
        value then amend the number of frames to gcd(frames, chunk)

        :returns: Number of frames to process
        :rtype: int
        """
        if self._plugin and self._plugin.chunk > 1:
            frame_chunk = self.meta_data.get("max_frames_process")
            chunk = self.data_obj.get_preview().get_starts_stops_steps(
                key='chunks')[self.get_slice_directions()[0]]
            self.meta_data.set('max_frames_process', math.gcd(frame_chunk, chunk))
        return self.meta_data.get("max_frames_process")

    def _get_max_frames_transfer(self):
        """ Get the number of frames to transfer for each run of
        process_frames. """
        return self.meta_data.get('max_frames_transfer')

    def _set_no_squeeze(self):
        self.no_squeeze = True

    def _get_no_squeeze(self):
        return self.no_squeeze

    def _set_rank_inc(self, n):
        """ Increase the rank of the array passed to the plugin by n.

        :param int n: Rank increment.
        """
        self._increase_rank = n

    def _get_rank_inc(self):
        """ Return the increased rank value

        :returns: Rank increment
        :rtype: int
        """
        return self._increase_rank

    def _set_meta_data(self):
        fixed, _ = self._get_fixed_dimensions()
        sdir = \
            [s for s in self.data_obj.get_slice_dimensions() if s not in fixed]
        shape = self.data_obj.get_shape()
        shape_before_tuning = self._get_shape_before_tuning()

        diff = len(shape) - len(shape_before_tuning)
        if diff:
            shape = shape_before_tuning
            sdir = sdir[:-diff]

        if 'fix_total_frames' in list(self.meta_data.get_dictionary().keys()):
            frames = self.meta_data.get('fix_total_frames')
        else:
            frames = np.prod([shape[d] for d in sdir])

        base_names = [p.__name__ for p in self._plugin.__class__.__bases__]
        processes = self.data_obj.exp.meta_data.get('processes')

        if 'GpuPlugin' in base_names:
            n_procs = len([n for n in processes if 'GPU' in n])
        else:
            n_procs = len(processes)

        # Fixing f_per_p to be just the first slice dimension for now due to
        # slow performance from HDF5 when not slicing multiple dimensions
        # concurrently
        #f_per_p = np.ceil(frames/n_procs)
        f_per_p = np.ceil(shape[sdir[0]]/n_procs)
        self.meta_data.set('shape', shape)
        self.meta_data.set('sdir', sdir)
        self.meta_data.set('total_frames', frames)
        self.meta_data.set('mpi_procs', n_procs)
        self.meta_data.set('frames_per_process', f_per_p)
        frame_shape, b_per_f = self.set_bytes_per_frame()
        self.meta_data.set('bytes_per_frame', b_per_f)
        self.meta_data.set('bytes_per_process', b_per_f*f_per_p)
        self.meta_data.set('frame_shape', frame_shape)

    def __log_max_frames(self, mft, mfp, check=True):
        logging.debug("Setting max frames transfer for plugin %s to %d" %
                      (self._plugin, mft))
        logging.debug("Setting max frames process for plugin %s to %d" %
                      (self._plugin, mfp))
        self.meta_data.set('max_frames_process', mfp)
        if check:
            self.__check_distribution(mft)
        # (((total_frames/mft)/mpi_procs) % 1)

    def __check_distribution(self, mft):
        warn_threshold = 0.85
        nprocs = self.meta_data.get('mpi_procs')
        nframes = self.meta_data.get('total_frames')
        temp = (((nframes/mft)/float(nprocs)) % 1)
        if temp != 0.0 and temp < warn_threshold:
            shape = self.meta_data.get('shape')
            sdir = self.meta_data.get('sdir')
            logging.warning('UNEVEN FRAME DISTRIBUTION: shape %s, nframes %s ' +
                         'sdir %s, nprocs %s', shape, nframes, sdir, nprocs)

    def _set_padding_dict(self):
        if self.padding and not isinstance(self.padding, Padding):
            self.pad_dict = copy.deepcopy(self.padding)
            self.padding = Padding(self)
            for key in list(self.pad_dict.keys()):
                getattr(self.padding, key)(self.pad_dict[key])

    def plugin_data_setup(self, pattern, nFrames, split=None, slice_axis=None,
                          getall=None, fixed_length=True):
        """ Setup the PluginData object.

        :param str pattern: A pattern name
        :param int nFrames: How many frames to process at a time.  Choose from
         'single', 'multiple', 'fixed_multiple' or an integer (an integer
         should only ever be passed in exceptional circumstances)
        :keyword str slice_axis: An axis label associated with the fastest
         changing (first) slice dimension.
        :keyword list[pattern, axis_label] getall: A list of two values.  If
         the requested pattern doesn't exist then use all of "axis_label"
         dimension of "pattern" as this is equivalent to one slice of the
         original pattern.
        :keyword fixed_length: Data passed to the plugin is automatically
         padded to ensure all plugin data has the same dimensions. Set this
         value to False to turn this off.

        """

        if pattern not in self.data_obj.get_data_patterns() and getall:
            pattern, nFrames = self.__set_getall_pattern(getall, nFrames)

        # slice_axis is first slice dimension
        self.__set_pattern(pattern, first_sdim=slice_axis)
        if isinstance(nFrames, list):
            nFrames, self._frame_limit = nFrames
        self.max_frames = nFrames
        self.split = split
        if not fixed_length:
            self._plugin.fixed_length = fixed_length

    def __set_getall_pattern(self, getall, nFrames):
        """ Set framework changes required to get all of a pattern of lower
        rank.
        """
        pattern, slice_axis = getall
        dim = self.data_obj.get_data_dimension_by_axis_label(slice_axis)
        # ensure data remains the same shape when 'getall' dim has length 1
        self._set_no_squeeze()
        if nFrames == 'multiple' or (isinstance(nFrames, int) and nFrames > 1):
            self._set_rank_inc(1)
        nFrames = self.data_obj.get_shape()[dim]
        return pattern, nFrames

    def plugin_data_transfer_setup(self, copy=None, calc=None):
        """ Set up the plugin data transfer frame parameters.
        If copy=pData (another PluginData instance) then copy """
        chunks = \
            self.data_obj.get_preview().get_starts_stops_steps(key='chunks')
        if not copy and not calc:
            mft, mft_shape, mfp = self._calculate_max_frames()
        elif calc:
            max_mft = calc.meta_data.get('max_frames_transfer')
            max_mfp = calc.meta_data.get('max_frames_process')
            max_nProc = int(np.ceil(max_mft/float(max_mfp)))
            nProc = max_nProc
            mfp = 1 if self.max_frames == 'single' else self.max_frames
            mft = nProc*mfp
            mft_shape = self._set_shape_transfer(self.__get_slice_size(mft))
        elif copy:
            mft = copy._get_max_frames_transfer()
            mft_shape = self._set_shape_transfer(self.__get_slice_size(mft))
            mfp = copy._get_max_frames_process()

        self.__set_max_frames(mft, mft_shape, mfp)

        if self._plugin and mft \
                and (chunks[self.data_obj.get_slice_dimensions()[0]] % mft):
            self._plugin.chunk = True
        self.__set_shape()

    def _calculate_max_frames(self):
        nFrames = self.max_frames
        self.__perform_checks(nFrames)
        td = self.data_obj._get_transport_data()
        mft, size_list = td._calc_max_frames_transfer(nFrames)
        self.meta_data.set('size_list', size_list)
        mfp = td._calc_max_frames_process(nFrames)
        if mft:
            mft_shape = self._set_shape_transfer(list(size_list))
        return mft, mft_shape, mfp

    def __set_max_frames(self, mft, mft_shape, mfp):
        self.meta_data.set('max_frames_transfer', mft)
        self.meta_data.set('transfer_shape', mft_shape)
        self.meta_data.set('max_frames_process', mfp)
        self.__log_max_frames(mft, mfp)
        # Retain the shape if the first slice dimension has length 1
        if mfp == 1 and self.max_frames == 'multiple':
            self._set_no_squeeze()

    def _get_plugin_data_size_params(self):
        nBytes = self.data_obj.get_itemsize()
        frame_shape = self.meta_data.get('frame_shape')
        total_frames = self.meta_data.get('total_frames')
        tbytes = nBytes*np.prod(frame_shape)*total_frames

        params = {'nBytes': nBytes, 'frame_shape': frame_shape,
                  'total_frames': total_frames, 'transfer_bytes': tbytes}
        return params

    def __perform_checks(self, nFrames):
        options = ['single', 'multiple']
        if not np.issubdtype(type(nFrames), np.int64) and nFrames not in options:
            e_str = ("The value of nFrames is not recognised.  Please choose "
            + "from 'single' and 'multiple' (or an integer in exceptional "
            + "circumstances).")
            raise Exception(e_str)

    def get_frame_limit(self):
        return self._frame_limit

    def get_current_frame_idx(self):
        """ Returns the index of the frames currently being processed.
        """
        global_index = self._plugin.get_global_frame_index()
        count = self._plugin.get_process_frames_counter()
        mfp = self.meta_data.get('max_frames_process')
        start = global_index[count]*mfp
        index = np.arange(start, start + mfp)
        nFrames = self.get_total_frames()
        index[index >= nFrames] = nFrames - 1
        return index
