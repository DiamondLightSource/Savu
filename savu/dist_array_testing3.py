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
.. module:: tomo_recon
   :platform: Unix
   :synopsis: runner for tests using the different transport mechanisms

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""
import logging
import optparse
import sys
import os

from savu.data.plugin_info import PluginList
import savu.plugins.utils as pu

MACHINE_NUMBER_STRING = '0'
MACHINE_RANK_NAME = 'cpu1'

import numpy as np

from contextlib import closing
from distarray.globalapi import Context, Distribution
from distarray.globalapi.distarray import DistArray as da

import h5py


# matching 
class Testing(object):
    
    def __init__(self):
        self.data = None
    
# matching 
def load_data(context, filename):
    data = Testing()
    data_key = 'entry1/tomo_entry/instrument/detector/data'

    with h5py.File(filename, 'r') as f:
        dataset = f[data_key]
        array_shape = dataset.shape

    dist = "bnn"
    distribution = Distribution(context, array_shape, dist=dist)
    data.data = context.load_hdf5(filename,
                                  distribution=distribution,
                                  key=data_key)
                                  
    print data.data.context.targets
    print data.data.key

    print('Loaded.')
    return data
    
#def numpy_julia_calc(la):
#    la = np.asarray(la)
#    b = la*3
#    print type(b)
#    return b
def timeseries_correction_set_up(la, params):
    print "IN TIMESERIES_CORRECTION_SET_UP FUNCTION"
    frames = np.asarray(la)
            
    temp_output = np.zeros_like(frames)#, dtype=np.int32) # *** what type?

    for i in range(len(frames)):
        projection = frames[i, :, :]
        temp_output[i, :, :] = projection
    
    return temp_output



#def local_julia_calc(la, kernel):
#    from distarray.localapi import LocalArray
#    counts = kernel(la)
#    res = LocalArray(la.distribution, buf=counts)
#    return proxyize(res) # noqa    
def local_process(frames, params, kernel):
    print "IN THE LOCAL PROCESS FUNCTION"
    from distarray.localapi import LocalArray
    recon = kernel(frames, params)
    res = LocalArray(frames.distribution, buf=recon)        
    return proxyize(res)  # noqa



# matching
#def distributed_julia_calc(la, kernel=numpy_julia_calc):
#    context = la.context
#    context.register(kernel)
#    iters_key = context.apply(local_julia_calc, (la.key,), {'kernel': kernel})
#    iters_da = DistArray.from_localarrays(iters_key[0], context=context, dtype=np.int32)
#    #return iters_da
#    return iters_da
def distributed_process(data, output, processes, process, params, kernel=timeseries_correction_set_up):
    print "IN THE DISTRIBUTED_PROCESS FUNCTION"

    context = data.context    
    context.register(kernel)
    iters_key = context.apply(local_process, (data.key, params), {'kernel': kernel})
    output = da.from_localarrays(iters_key[0], context=context, dtype=np.int32)
    return output
    

if __name__ == '__main__':

    usage = "%prog [options] input_file output_directory"
    version = "%prog 0.1"
    parser = optparse.OptionParser(usage=usage, version=version)
    parser.add_option("-n", "--names", dest="names", help="Process names",
                      default="CPU1,CPU2,CPU3,CPU4,CPU5,CPU6,CPU7,CPU8",
                      type='string')
    parser.add_option("-f", "--filename", dest="process_filename",
                      help="The filename of the process file",
                      default="/home/ssg37927/Savu/test_data/process01.nxs",
                      type='string')
    parser.add_option("-l", "--log2db", dest="log2db",
                      help="Set logging to go to a database",
                      default=False,
                      action="store_true")
    (options, args) = parser.parse_args()


    # Check basic items for completeness
    if len(args) is not 3:
        print("filename, process file and output path needs to be specified")
        print("Exiting with error code 1 - incorrect number of inputs")
        sys.exit(1)

    if not os.path.exists(args[0]):
        print("Input file '%s' does not exist" % args[0])
        print("Exiting with error code 2 - Input file missing")
        sys.exit(2)

    if not os.path.exists(args[1]):
        print("Processing file '%s' does not exist" % args[1])
        print("Exiting with error code 3 - Processing file missing")
        sys.exit(3)

    if not os.path.exists(args[2]):
        print("Output Directory '%s' does not exist" % args[2])
        print("Exiting with error code 4 - Output Directory missing")
        sys.exit(4)


    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler(os.path.join(args[2],'log.txt'), mode='w')
    fh.setFormatter(logging.Formatter('L %(relativeCreated)12d M' +
            MACHINE_NUMBER_STRING + ' ' + MACHINE_RANK_NAME +
            ' %(levelname)-6s %(message)s'))
    logger.addHandler(fh)

    logging.info("Starting tomo_recon process")

    plugin_list = PluginList()
    plugin_list.populate_plugin_list(options.process_filename)
    transport = '/home/qmm55171/Documents/Git/git_repos/Savu/savu/data/transports/dist_array'
    #pu.load_transport(transport, plugin_list, args)
    

    input_file = "/mnt/lustre03/testdir/dasc/qmm55171/test_data/24737.nxs"
    processes = "CPU0"
    theProcess = 0

    output_data_type = []
    targets = [0, 1, 2, 3, 4]
    
    with closing(Context()) as context:
        # use all available targets
        engine_count_list = list(range(1, len(context.targets) + 1))     
        
    engine_count_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    targets = list(range(max(engine_count_list)))
    
    
    with closing(Context(targets=targets)) as context:
        in_data = load_data(context, input_file) #        
        A = in_data.data
        result = distributed_process(A, [], processes, theProcess, [])

#    with closing(Context(targets=targets)) as context:
#        in_data = load_hdf5_distarray(context)
#        A = in_data.data
#        result = distributed_julia_calc(A, kernel=kernel)