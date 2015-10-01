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
.. module:: utils
   :platform: Unix
   :synopsis: Utilities for the DistArray transport mechanism

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import numpy as np


def distributed_process(plugin, in_data, out_data, processes, process, params,
                        kernel):
    params = set_params(in_data, out_data, params, kernel, plugin)
    context = in_data.data.context
    context.register(kernel)
    print ("The kernel", kernel, "has been registered")
    iters_key = context.apply(local_process,
                              (in_data.data.key, out_data.data.key, params),
                              {'kernel': kernel})
    return iters_key


def local_process(frames, output, params, kernel):
    from distarray.localapi import LocalArray
    recon = kernel(frames, output, params)
    res = LocalArray(output.distribution, buf=recon)
    return proxyize(res)  # noqa


def timeseries_correction_set_up(in_darray, out_darray, params):
    print "***IN TIMESERIES CORRECTION SET UP***"
    image_key = params[0]
    plugin = params[1]

    frames = np.asarray(in_darray, dtype=np.float32)
    print (frames.shape, frames.dtype, frames.nbytes)

    data = frames[image_key == 0, :, :]

    # pull out the average dark and flat data
    dark = None
    try:
        dark = np.mean(frames[image_key == 2, :, :], 0)
    except:
        dark = np.zeros((frames.shape[1], frames.shape[2]))
    flat = None
    try:
        flat = np.mean(frames[image_key == 1, :, :], 0)
    except:
        flat = np.ones((frames.shape[1], frames.shape[2]))
    # shortcut to reduce processing
    flat = flat - dark
    flat[flat == 0.0] = 1.0

    for i in range(frames.shape[1]):
    #*** need to change this to find the direction from the plugin
    # (hard coded for now)
        out_darray[:, i, :] = \
            plugin.correction(data[:, i, :], dark[i, :], flat[i, :])

    return out_darray


def reconstruction_set_up(in_darray, out_darray, params):
    print "IN RECONSTRUCTION SET-UP"
    import resource
    print ("the memory usage for this process is",
           resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    frames = np.asarray(in_darray, dtype=np.float32)
    print (frames.shape, frames.dtype, frames.nbytes)
    print "creating output array"
    result = np.asarray(out_darray, dtype=np.float32)
    print (frames.shape, frames.dtype, frames.nbytes)
    print "done"

    print frames.shape
    print result.shape

    print frames.nbytes

    centre_of_rotations = params[0]
    angles = params[1]
    shape = params[2]
    plugin = params[3]

    for i in range(frames.shape[1]):
    #*** need to change this to find the direction from the plugin
    # (hard coded for now)
        print i
        out_darray[:, i, :] = \
            plugin.reconstruct(frames[:, i, :], result[:, i, :],
                               centre_of_rotations[i], angles,
                               (shape[0], shape[2]),
                               (shape[0]/2, shape[2]/2))
    return out_darray


def filter_set_up(in_darray, out_darray, params):
    frames = np.asarray(in_darray)
    pass


def set_params(data, output, params, kernel, plugin):
    str_kernel = str(kernel)
    if 'reconstruction' in str_kernel:
        params = [params[0], params[1], output.shape, plugin]
    elif 'timeseries' in str_kernel:
        params = [params[0], plugin]
    elif 'filter' in str_kernel:
        params = [params[0], params[1]]
    return params
