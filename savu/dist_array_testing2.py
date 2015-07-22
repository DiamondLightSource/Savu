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

import json
from time import time
from contextlib import closing
from math import sqrt, floor

import numpy

from distarray.globalapi import Context, Distribution
from distarray.globalapi.distarray import DistArray

def numpy_julia_calc(z, c, z_max, n_max):
    z = numpy.asarray(z)
    counts = numpy.zeros_like(z, dtype=numpy.int32)
    hits = numpy.zeros_like(z, dtype=numpy.bool)
    mask = numpy.zeros_like(z, dtype=numpy.bool)
    n = 0

    while not numpy.all(hits) and n < n_max:
        z = z * z + c
        mask = (abs(z) > z_max) & (~hits)
        counts[mask] = n
        hits |= mask
        z[hits] = 0
        n += 1
    counts[~hits] = n_max
    return counts


def create_complex_plane(context, resolution, dist, re_ax, im_ax):
    import numpy as np

    def fill_complex_plane(arr, re_ax, im_ax, resolution):
        """Fill in points on the complex coordinate plane."""
        re_step = float(re_ax[1] - re_ax[0]) / resolution[0]
        im_step = float(im_ax[1] - im_ax[0]) / resolution[1]
        for i in arr.distribution[0].global_iter:
            for j in arr.distribution[1].global_iter:
                arr.global_index[i, j] = complex(re_ax[0] + re_step * i,
                                                 im_ax[0] + im_step * j)

    # Create an empty distributed array.
    distribution = Distribution(context, (resolution[0], resolution[1]),
                                dist=dist)
    complex_plane = context.empty(distribution, dtype=np.complex64)
    context.apply(fill_complex_plane,
                  (complex_plane.key, re_ax, im_ax, resolution))
    return complex_plane


def local_julia_calc(la, c, z_max, n_max, kernel):
    from distarray.localapi import LocalArray
    counts = kernel(la, c, z_max, n_max)
    res = LocalArray(la.distribution, buf=counts)
    return proxyize(res)  # noqa


def distributed_julia_calc(distarray, c, z_max, n_max, kernel=numpy_julia_calc):

    context = distarray.context
    iters_key = context.apply(local_julia_calc,
                              (distarray.key, c, z_max, n_max),
                              {'kernel': kernel})
    iters_da = DistArray.from_localarrays(iters_key[0], context=context,
                                          dtype=numpy.int32)
    return iters_da


def do_julia_run(context, dist, dimensions, c, complex_plane, z_max, n_max,
                 benchmark_numpy=False, kernel=numpy_julia_calc):

    num_engines = len(context.targets)
    # Calculate the number of iterations to escape for each point.
    if benchmark_numpy:
        complex_plane_nd = complex_plane.tondarray()
        t0 = time()
        num_iters = kernel(complex_plane_nd, c, z_max=z_max, n_max=n_max)
        t1 = time()
        iters_list = [numpy.asscalar(numpy.asarray(num_iters).sum())]
    else:
        t0 = time()
        num_iters = distributed_julia_calc(complex_plane, c,
                                           z_max=z_max, n_max=n_max,
                                           kernel=kernel)
        t1 = time()

        # Iteration count.
        def local_sum(la):
            return numpy.asscalar(la.ndarray.sum())
        iters_list = context.apply(local_sum, (num_iters.key,))

    # Print results.
    dist_text = dist if dist == 'numpy' else '-'.join(dist)

    return (t0, t1, dist_text, dimensions[0], str(c), num_engines, iters_list)

def do_julia_runs(repeat_count, engine_count_list, dist_list, resolution_list,
                  c_list, re_ax, im_ax, z_max, n_max, output_filename,
                  kernel=numpy_julia_calc, scaling="strong"):

    max_engine_count = max(engine_count_list)
    with closing(Context()) as context:
        # Check that we have enough engines available.
        num_engines = len(context.targets)
    if max_engine_count > num_engines:
        msg = 'Require %d engines, but only %d are available.' % (
            max_engine_count, num_engines)
        raise ValueError(msg)

    # Loop over everything and time the calculations.
    results = []
    hdr = (('Start', 'End', 'Dist', 'Resolution', 'c', 'Engines', 'Iters'))
    print("(n/n_runs: time)", hdr)
    # progress stats
    n_regular_runs = repeat_count * (len(resolution_list) * len(c_list) *
                                     len(engine_count_list) * len(dist_list))
    n_numpy_runs = repeat_count * (len(resolution_list) * len(c_list))
    n_runs = n_regular_runs + n_numpy_runs
    prog_fmt = "({:d}/{:d}: {:0.3f}s)"
    n = 0
    for i in range(repeat_count):
        for resolution in resolution_list:
            dimensions = (resolution, resolution)
            for c in c_list:
                with closing(Context(targets=[0])) as context:
                    # numpy julia run
                    complex_plane = create_complex_plane(context, dimensions,
                                                         'bn', re_ax, im_ax)
                    result = do_julia_run(context, 'numpy', dimensions, c,
                                          complex_plane, z_max, n_max,
                                          benchmark_numpy=True, kernel=kernel)
                    #results.append({h: r for h, r in zip(hdr, result)})
                    n += 1
                    print(prog_fmt.format(n, n_runs, result[1] - result[0]), result)
                for engine_count in engine_count_list:
                    if scaling == "weak":
                        factor = sqrt(engine_count)
                        dimensions = (int(floor(resolution * factor)),) * 2
                    for dist in dist_list:
                        targets = list(range(engine_count))
                        print targets
                        with closing(Context(targets=targets)) as context:
                            context.register(kernel)
                            complex_plane = create_complex_plane(context,
                                                                 dimensions,
                                                                 dist, re_ax,
                                                                 im_ax)
                            result = do_julia_run(context, dist, dimensions, c,
                                                  complex_plane, z_max, n_max,
                                                  benchmark_numpy=False,
                                                  kernel=kernel)
                            #results.append({h: r for h, r in zip(hdr, result)})
                            n += 1
                            print(prog_fmt.format(n, n_runs, result[1] - result[0]), result)
                            with open(output_filename, 'wt') as fp:
                                json.dump(results, fp, sort_keys=True,
                                          indent=4, separators=(',', ': '))
    return results


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
    
    with closing(Context()) as context:
        # use all available targets
        engine_count_list = list(range(1, len(context.targets) + 1))
        print context.targets
        
    engine_count_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    dist_list = ['bn', 'cn', 'bb', 'cc']
    c_list = [complex(-0.045, 0.45)]  # This Julia set has many points inside
                                      # needing all iterations.
    re_ax = (-1.5, 1.5)
    im_ax = (-1.5, 1.5)
    z_max = 2.0
    n_max = 100
    repeat_count = 1
    resolution_list = [100]
    output_filename = 'testing'
    scaling = 1    
    
    results = do_julia_runs(repeat_count, engine_count_list, dist_list,
                            resolution_list, c_list, re_ax, im_ax, z_max,
                            n_max, output_filename=output_filename,
                            kernel=numpy_julia_calc,
                            scaling=scaling)