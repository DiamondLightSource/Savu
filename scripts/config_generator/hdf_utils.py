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
.. module:: parameter_utils
   :platform: Unix
   :synopsis: Utilities for checking hdf/nxs files

.. moduleauthor:: Nghia Vo <scientificsoftware@diamond.ac.uk>

"""

import h5py
import numpy as np
from collections import deque

PIPE = "│"
ELBOW = "└──"
TEE = "├──"
PIPE_PREFIX = "│   "
SPACE_PREFIX = "    "
TOMO_DATA = "entry1/tomo_entry/data/data"
ROTATION_ANGLE = "entry1/tomo_entry/data/rotation_angle"
IMAGE_KEY = "entry1/tomo_entry/instrument/detector/image_key"


def get_hdf_information(file_path, display=False):
    """
    Get information of datasets in a hdf/nxs file.

    Parameters
    ----------
    file_path : str
        Path to the file.
    display : bool
        Print the results onto the screen if True.

    Returns
    -------
    list_key : str
        Keys to the datasets.
    list_shape : tuple of int
        Shapes of the datasets.
    list_type : str
        Types of the datasets.
    """
    hdf_object = h5py.File(file_path, 'r')
    keys = []
    hdf_object.visit(keys.append)
    list_key, list_shape, list_type = [], [], []
    for key in keys:
        try:
            data = hdf_object[key]
            if isinstance(data, h5py.Group):
                list_tmp = list(data.items())
                if list_tmp:
                    for key2, _ in list_tmp:
                        list_key.append(key + "/" + key2)
                else:
                    list_key.append(key)
            else:
                list_key.append(data.name)
        except KeyError:
            list_key.append(key)
            pass
    for i, key in enumerate(list_key):
        try:
            data = hdf_object[list_key[i]]
            if isinstance(data, h5py.Dataset):
                shape, dtype = data.shape, data.dtype
            else:
                shape, dtype = None, None
            if isinstance(data, list):
                if len(data) == 1:
                    if not isinstance(data, np.ndarray):
                        dtype = str(list(data)[0])
                        dtype.replace("b'", "'")
            list_shape.append(shape)
            list_type.append(dtype)
        except KeyError:
            list_shape.append(None)
            list_type.append(None)
            pass
    hdf_object.close()
    if display:
        if list_key:
            for i, key in enumerate(list_key):
                print(key + " : " + str(list_shape[i]) + " : " + str(
                    list_type[i]))
        else:
            print("Empty file !!!")
    return list_key, list_shape, list_type


def find_hdf_key(file_path, pattern, display=False):
    """
    Find datasets matching the name-pattern in a hdf/nxs file.

    Parameters
    ----------
    file_path : str
        Path to the file.
    pattern : str
        Pattern to find the full names of the datasets.
    display : bool
        Print the results onto the screen if True.

    Returns
    -------
    list_key : str
        Keys to the datasets.
    list_shape : tuple of int
        Shapes of the datasets.
    list_type : str
        Types of the datasets.
    """
    hdf_object = h5py.File(file_path, 'r')
    list_key, keys = [], []
    hdf_object.visit(keys.append)
    for key in keys:
        try:
            data = hdf_object[key]
            if isinstance(data, h5py.Group):
                list_tmp = list(data.items())
                if list_tmp:
                    for key2, _ in list_tmp:
                        list_key.append(key + "/" + key2)
                else:
                    list_key.append(key)
            else:
                list_key.append(data.name)
        except KeyError:
            pass
    list_dkey, list_dshape, list_dtype = [], [], []
    for _, key in enumerate(list_key):
        if pattern in key:
            list_dkey.append(key)
            try:
                data = hdf_object[key]
                if isinstance(data, h5py.Dataset):
                    shape, dtype = data.shape, data.dtype
                else:
                    shape, dtype = None, None
                if isinstance(data, list):
                    if len(data) == 1:
                        if not isinstance(data, np.ndarray):
                            dtype = str(list(data)[0])
                            dtype.replace("b'", "'")
                list_dtype.append(dtype)
                list_dshape.append(shape)
            except KeyError:
                list_dtype.append(None)
                list_dshape.append(None)
                pass
    hdf_object.close()
    if display:
        if list_dkey:
            for i, key in enumerate(list_dkey):
                print(key + " : " + str(list_dshape[i]) + " : " + str(
                    list_dtype[i]))
        else:
            print("Can't find datasets with keys matching the "
                  "pattern: {}".format(pattern))
    return list_dkey, list_dshape, list_dtype


def _get_subgroups(hdf_object, key=None):
    """
    Supplementary method for building the tree view of a hdf5 file.
    Return the name of subgroups.
    """
    list_group = []
    if key is None:
        for group in hdf_object.keys():
            list_group.append(group)
        if len(list_group) == 1:
            key = list_group[0]
        else:
            key = ""
    else:
        if key in hdf_object:
            try:
                obj = hdf_object[key]
                if isinstance(obj, h5py.Group):
                    for group in hdf_object[key].keys():
                        list_group.append(group)
            except KeyError:
                pass
    if len(list_group) > 0:
        list_group = sorted(list_group)
    return list_group, key


def _add_branches(tree, hdf_object, key, key1, index, last_index, prefix,
                  connector, level, add_shape):
    """
    Supplementary method for building the tree view of a hdf5 file.
    Add branches to the tree.
    """
    shape = None
    key_comb = key + "/" + key1
    if add_shape is True:
        if key_comb in hdf_object:
            try:
                obj = hdf_object[key_comb]
                if isinstance(obj, h5py.Dataset):
                    shape = str(obj.shape)
            except KeyError:
                shape = str("-> ???External-link???")
    if shape is not None:
        tree.append(f"{prefix}{connector} {key1} {shape}")
    else:
        tree.append(f"{prefix}{connector} {key1}")
    if index != last_index:
        prefix += PIPE_PREFIX
    else:
        prefix += SPACE_PREFIX
    _make_tree_body(tree, hdf_object, prefix=prefix, key=key_comb,
                    level=level, add_shape=add_shape)


def _make_tree_body(tree, hdf_object, prefix="", key=None, level=0,
                    add_shape=True):
    """
    Supplementary method for building the tree view of a hdf5 file.
    Create the tree body.
    """
    entries, key = _get_subgroups(hdf_object, key)
    num_ent = len(entries)
    last_index = num_ent - 1
    level = level + 1
    if num_ent > 0:
        if last_index == 0:
            key = "" if level == 1 else key
            if num_ent > 1:
                connector = PIPE
            else:
                connector = ELBOW if level > 1 else ""
            _add_branches(tree, hdf_object, key, entries[0], 0, 0, prefix,
                          connector, level, add_shape)
        else:
            for index, key1 in enumerate(entries):
                connector = ELBOW if index == last_index else TEE
                if index == 0:
                    tree.append(prefix + PIPE)
                _add_branches(tree, hdf_object, key, key1, index, last_index,
                              prefix, connector, level, add_shape)


def get_hdf_tree(file_path, add_shape=True, display=True):
    """
    Get the tree view of a hdf/nxs file.

    Parameters
    ----------
    file_path : str
        Path to the file.
    add_shape : bool
        Including the shape of a dataset to the tree if True.
    display : bool
        Print the tree onto the screen if True.

    Returns
    -------
    list of string
    """
    hdf_object = h5py.File(file_path, 'r')
    tree = deque()
    _make_tree_body(tree, hdf_object, add_shape=add_shape)
    if display:
        for entry in tree:
            print(entry)
    return tree


def check_tomo_data(file_path):
    """
    To check:
    - If paths to datasets in a hdf/nxs file following the Diamond-tomo data
      convention.
    - Shapes between datasets are consistent.
    """
    path1, shape1, _ = find_hdf_key(file_path, TOMO_DATA)
    path2, shape2, _ = find_hdf_key(file_path, ROTATION_ANGLE)
    path3, shape3, _ = find_hdf_key(file_path, IMAGE_KEY)
    msg = []
    got_it = True
    if not path1:
        msg.append(" -> Can't find the path: '{0}' "
                   "to tomo-data".format(TOMO_DATA))
        got_it = False
    else:
        if not shape1:
            msg.append(" -> Empty data in: '{0}'".format(TOMO_DATA))
            got_it = False
        else:
            shape1 = shape1[0][0]
    if not path2:
        msg.append(" -> Can't find the path: '{0}' to "
                   "rotation angles".format(ROTATION_ANGLE))
        got_it = False
    else:
        if not shape2:
            msg.append(" -> Empty data in: '{0}'".format(ROTATION_ANGLE))
            got_it = False
        else:
            shape2 = list(shape2)[0][0]
    if not path3:
        msg.append(" -> Can't find the path: '{0}' to "
                   "image-keys".format(IMAGE_KEY))
        got_it = False
    else:
        if not shape3:
            msg.append(" -> Empty data in: '{0}'".format(IMAGE_KEY))
            got_it = False
        else:
            shape3 = list(shape3)[0][0]
    if shape1 != shape2:
        msg.append(" -> Number of projections: {0} is not the same as the"
                   " number of rotation-angles: {1}".format(shape1, shape2))
        got_it = False
    if shape1 != shape3:
        msg.append(" -> Number of projections: {0} is not the same as the"
                   " number of image-keys: {1}".format(shape1, shape3))
        got_it = False
    if shape2 != shape3:
        msg.append(" -> Number of rotation-angles: {0} is not the same as the"
                   " number of image-keys: {1}".format(shape2, shape3))
        got_it = False
    if got_it is True:
        print("=============================================================")
        print("Paths to datasets following the default names used by "
              "NxTomoLoader:")
        print("   Path to tomo-data: '{0}'. Shape: {1}".format(
            path1[0], shape1))
        print("   Path to rotation-angles: '{0}'. Shape: {1}".format(
            path2[0], shape2))
        print("   Path to image-keys: '{0}'. Shape: {1}".format(
            path3[0], shape3))
        print("=============================================================")
    else:
        print("=========================!!!WARNING!!!=======================")
        for entry in msg:
            print("  " + entry)
        print("=============================================================")
