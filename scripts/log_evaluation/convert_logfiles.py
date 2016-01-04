#import GraphicalThreadProfiler as gtp
import GraphicalThreadProfiler_multi as gtpm

import fnmatch
from os import listdir
from os.path import isfile, join

''' temporary file for converting all folders of log files when changes are
    made to the visualisation files '''
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# single only
#dir_path = '/dls/science/users/qmm55171/final_logs/testing/log_files/'
#all_files = [ f for f in listdir(dir_path) if isfile(join(dir_path,f)) ]
#files = [(dir_path + '/' + f) for f in all_files]
#
#for file in files:
#    gtp.convert(file)

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# multi only
#path = '/dls/science/users/qmm55171/final_logs/'
#dir_path = [path + 'new_mpi_params/no_chunking/log_files/',
#            path + 'original_mpi_params/no_chunking/log_files/',
#            path + 'original_mpi_params/chunk_true/log_files/']

dir_path = ['/dls/science/users/qmm55171/final_logs/testing/log_files/']

for dir in dir_path:
    all_files = [f for f in listdir(dir) if isfile(join(dir, f))]
    files = [(dir + '/' + f) for f in all_files]
    wildcard_files = [(dir + '/' + f.split('.')[0] + '*') for f in all_files]

    for wildcard in set(wildcard_files):
        print wildcard
        matching_files = []
        for file in files:
            if fnmatch.fnmatch(file, wildcard):
                matching_files.append(file)
                print file
        print matching_files
        gtpm.convert(matching_files)

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
