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
.. module:: plugin_data
   :platform: Unix
   :synopsis: Contains the PluginData class. Each Data set used in a plugin \
       has a PluginData object encapsulated within it, for the duration of a \
       plugin run.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""
import sys
import copy
import logging
import numpy as np
from fractions import gcd

from savu.data.meta_data import MetaData


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
        self.shape_transfer = None
        self.core_shape = None
        self.multi_params = {}
        self.extra_dims = []
        self._plugin = plugin
        self.fixed_dims = True
        self.split = None
        self.boundary_padding = None
        self.no_squeeze = False
        self.pre_tuning_shape = None

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

    def __set_pattern(self, name):
        """ Set the pattern related information in the meta data dict.
        """
        pattern = self.data_obj.get_data_patterns()[name]
        self.meta_data.set("name", name)
        self.meta_data.set("core_dims", pattern['core_dims'])
        self.__set_slice_dimensions()

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

    def __set_shape_transfer(self, slice_size):
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
        self.shape_transfer = tuple(shape)

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
        return self.shape_transfer

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

    def __set_slice_dimensions(self):
        """ Set the slice dimensions in the pluginData meta data dictionary.
        """
        slice_dirs = self.data_obj.get_data_patterns()[
            self.get_pattern_name()]['slice_dims']
        self.meta_data.set('slice_dims', slice_dirs)

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
        if self._get_max_frames_process() > 1:
            plugin_dims += (self.get_slice_dimensions()[0],)
        return list(set(plugin_dims)).index(label_dim)

    def set_slicing_order(self, order):
        """
        Reorder the slice dimensions.  The fastest changing slice dimension
        will always be the first one stated in the pattern key ``slice_dir``.
        The input param is a tuple stating the desired order of slicing
        dimensions relative to the current order.
        """
        slice_dirs = self.get_slice_directions()
        if len(slice_dirs) < len(order):
            raise Exception("Incorrect number of dimensions specifed.")
        ordered = [slice_dirs[o] for o in order]
        remaining = [s for s in slice_dirs if s not in ordered]
        new_slice_dirs = tuple(ordered + remaining)
        self.get_current_pattern()['slice_dir'] = new_slice_dirs

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
        self.__set_shape()

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
        all_dims = self.get_core_directions() + self.get_slice_directions()
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
            self.meta_data.set('max_frames_process', gcd(frame_chunk, chunk))
        return self.meta_data.get("max_frames_process")

    def _get_max_frames_transfer(self):
        """ Get the number of frames to transfer for each run of
        process_frames. """
        return self.meta_data.get('max_frames_transfer')

    def __set_boundary_padding(self, pad):
        self.boundary_padding = pad

    def _get_boundary_padding(self):
        return self.boundary_padding

    def __set_no_squeeze(self):
        self.no_squeeze = True

    def _get_no_squeeze(self):
        return self.no_squeeze

    def __checks_and_boundaries(self, nFrames):
        options = ['single', 'multiple']
        if not isinstance(nFrames, int) and nFrames not in options:
            e_str = "The value of nFrames is not recognised.  Please choose "
            "from 'single' and 'multiple' (or an integer in exceptional "
            "circumstances)."
            raise Exception(e_str)

        max_mft = 32  # max frames that can be transferred from file at a time
        frame_threshold = 32  # no idea if this is a good number
        # min frames required if frames_per_process > frame_threshold
        min_mft = 16
        if isinstance(nFrames, int) and nFrames > max_mft:
            logging.warn("The requested %s frames excedes the maximum "
                         "preferred of %s." % (nFrames, max_mft))
            max_mft = nFrames
        return max_mft, min_mft, frame_threshold

    def __get_max_frames_parameters(self):
        fixed, _ = self._get_fixed_dimensions()
        sdir = \
            [s for s in self.data_obj.get_slice_dimensions() if s not in fixed]
        shape = self.data_obj.get_shape()
        shape_before_tuning = self._get_shape_before_tuning()

        diff = len(shape) - len(shape_before_tuning)
        if diff:
            shape = shape_before_tuning
            sdir = sdir[:-diff]

        frames = np.prod([shape[d] for d in sdir])
        base_names = [p.__name__ for p in self._plugin.__class__.__bases__]
        processes = self.data_obj.exp.meta_data.get('processes')

        if 'GpuPlugin' in base_names:
            n_procs = len([n for n in processes if 'GPU' in n])
        else:
            n_procs = len(processes)

        f_per_p = np.ceil(frames/n_procs)
        return sdir, shape, frames, n_procs, f_per_p

    def __log_max_frames(self, mft, mfp, frames, procs):
        logging.info("Setting max frames transfer for plugin %s to %d" %
                     (self._plugin, mft))
        logging.info("Setting max frames process for plugin %s to %d" %
                     (self._plugin, mft))
        self.meta_data.set('max_frames_process', mfp)
        self.__check_distribution(mft)
        # (((total_frames/mft)/mpi_procs) % 1)

    def _calc_max_frames_transfer(self, nFrames):
        """ The number of frames each process should retrieve from file at a
        time.
        """
        max_mft, min_mft, threshold = self.__checks_and_boundaries(nFrames)
        sdir, shape, total_frames, mpi_procs, frames_per_process = \
            self.__get_max_frames_parameters()

        # find all possible choices of nFrames, being careful with boundaries
        fchoices, size_list = self.__get_frame_choices(
                sdir, min(max_mft, np.prod([shape[d] for d in sdir])))

        if frames_per_process > threshold:
            min_mft = min(max(fchoices), min_mft)
            fchoices = [f for f in fchoices if f >= min_mft]

        mft, idx = self.__find_best_frame_distribution(
            fchoices, total_frames, mpi_procs, idx=True)

        self.__set_shape_transfer(size_list[fchoices.index(mft)])

        if nFrames == 'single':
            self.__log_max_frames(mft, 1, total_frames, mpi_procs)
            return int(mft)

        mfp = nFrames if isinstance(nFrames, int) else min(mft, shape[sdir[0]])

        multi = self.__find_multiples_of_b_that_divide_a(mft, mfp)
        possible = sorted(list(set(set(multi).intersection(set(fchoices)))))

        # closest of fchoices to mfp plus difference as boundary padding
        if not possible:
            mft, _ = self.__find_closest_lower(fchoices[::-1], mfp)
            self.__set_boundary_padding(mfp - mft)
        else:
            mft = self.__find_best_frame_distribution(
                possible[::-1], total_frames, mpi_procs)

        self.__set_shape_transfer(size_list[fchoices.index(mft)])
        self.__log_max_frames(mft, mfp, total_frames, mpi_procs)

        # Retain the shape if the first slice dimension has length 1
        if mfp == 1:
            self.__set_no_squeeze()
        return int(mft)

    def __check_distribution(self, mft):
        sdir, shape, nframes, nprocs, _ = \
            self.__get_max_frames_parameters()
        warn_threshold = 0.85
        temp = (((nframes/mft)/float(nprocs)) % 1)
        if temp != 0.0 and temp < warn_threshold:
            logging.warn('UNEVEN FRAME DISTRIBUTION: shape %s, nframes %s ' +
                         'sdir %s, nprocs %s' % (shape, nframes, sdir, nprocs))

    def __find_closest_lower(self, vlist, value):
        rem = [f if f != 0 else value for f in [m % value for m in vlist]]
        min_val = min(rem, key=lambda x: abs(x-value))
        idx = rem.index(min_val)
        return vlist[idx], idx

    def __get_frame_choices(self, sdir, max_mft):
        """ Find all possible combinations of increasing slice dimension sizes
        with their product less than max_mft and return a list of these
        products. """
        nDims = len(sdir)
        temp = [1]*len(sdir)
        shape = self.data_obj.get_shape()
        idx = 0
        choices = []
        size_list = []

        while(np.prod(temp) <= max_mft):
            dshape = shape[sdir[idx]]
            # could remove this if statement and ensure padding at the end of
            # each slice dimension instead.
            if dshape % temp[idx] == 0 or nDims == 1:
                choices.append(np.prod(temp))
                size_list.append(copy.copy(temp))
            if temp[idx] == dshape:
                idx += 1
                if idx == nDims:
                    break
            temp[idx] += 1

        return choices[::-1], size_list[::-1]

    def __find_multiples_of_b_that_divide_a(self, a, b):
        """ Find all positive multiples of b that divide a. """
        val = 1
        val_list = []
        i = 0
        while(val > 0):
            val = (int(a/b)+i)*b
            val_list.append(val)
            i -= 1
        return val_list[:-1]

    def __find_best_frame_distribution(self, flist, nframes, nprocs,
                                       idx=False):
        """ Determine which of the numbers in the list of possible frame
        chunks gives the best distribution of frames per process. """
        multi_list = [(nframes/float(v))/nprocs for v in flist]
        min_val, closest_lower_idx = self.__find_closest_lower(multi_list, 1)
        if idx:
            return flist[closest_lower_idx], closest_lower_idx
        return flist[closest_lower_idx]

    def plugin_data_setup(self, pattern, nFrames, split=None):
        """ Setup the PluginData object.

        # add more information into here via a decorator!
        :param str pattern: A pattern name
        :param int nFrames: How many frames to process at a time.  Choose from\
            'single', 'multiple', 'fixed_multiple' or an integer (an integer \
            should only ever be passed in exceptional circumstances)
        """
        self.__set_pattern(pattern)
        chunks = \
            self.data_obj.get_preview().get_starts_stops_steps(key='chunks')

        nFrames = self._calc_max_frames_transfer(nFrames)
        self.meta_data.set('max_frames_transfer', nFrames)
        if self._plugin and \
                (chunks[self.data_obj.get_slice_dimensions()[0]] % nFrames):
            self._plugin.chunk = True
        self.__set_shape()
        self.split = split
