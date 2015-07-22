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


def distributed_process(plugin, data, output, processes, process, params, kernel):
    print "IN THE DISTRIBUTED_PROCESS FUNCTION"
    params = set_params(output, params, kernel, plugin)

    context = data.data.context
    context.register(kernel)
    print ("The kernel", kernel, "has been registered")
    iters_key = context.apply(local_process, (data.data.key, params), {'kernel': kernel})
    
    return iters_key
    
def local_process(frames, params, kernel):
    print "IN THE LOCAL PROCESS FUNCTION"
    from distarray.localapi import LocalArray
    recon = kernel(frames, params)
    res = LocalArray(frames.distribution, buf=recon)        
    return proxyize(res)  # noqa
    
    
def reconstruction_set_up(d_array, params):
    print "IN reconstruction_set_up FUNCTION"   

    frames = np.asarray(d_array)

    param_name = ['centre_of_rotations', 'angles', 'output', 'plugin']
    for name in param_name: 
        for p in params:
            globals()[name] = p
    
    temp_output = np.zeros_like(frames)#, dtype=np.int32) # *** what type?
    for i in range(len(frames)):
        frame_centre_of_rotation = centre_of_rotations[i]
        sinogram = frames[:, i, :]
        reconstruction = \
            plugin.reconstruct(sinogram, frame_centre_of_rotation, angles,
                             (output.data.shape[0], output.data.shape[2]),
                             (output.data.shape[0]/2,
                              output.data.shape[2]/2))
        temp_output[:, i, :] = reconstruction
    
    return temp_output
    
    
def filter_set_up(d_array, params):
    frames = np.asarray(d_array)
    param_name = []
    for name in param_name: 
        for p in params:
            globals()[name] = p
         
    # *** to be completed
    pass 
    

def timeseries_correction_set_up(d_array, params):
    print "IN TIMESERIES_CORRECTION_SET_UP FUNCTION"

    frames = np.asarray(d_array)

    param_name = ['dark', 'flat']
    for name in param_name: 
        for p in params:
            globals()[name] = p
            
    temp_output = np.zeros_like(frames)#, dtype=np.int32) # *** what type?

    #*** why was rotation angle in here?

    for i in range(len(frames)):
        projection = frames[i, :, :]
        projection = (projection-dark)/flat  # (flat-dark)
        projection[projection <= 0.0] = 1;
        temp_output[i, :, :] = projection
    
    return temp_output


def set_params(output, params, kernel, plugin):
    str_kernel = str(kernel)
    if 'reconstruction' in str_kernel:
        params = [params[0], params[1], output, plugin]
    elif 'timeseries' in str_kernel:
        params = [params[0], params[1]]
    elif 'filter' in str_kernel:
        params = [params[0], params[1]]
    return params   