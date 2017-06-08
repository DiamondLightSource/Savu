#!/bin/bash

# set compiler wrapper
mpicc=$(command -v mpicc)
mpi=`dirname $mpicc`

# set anaconda distribution
ana_path=$(command -v anaconda)
ana_path=${ana_path%/bin/anaconda}
hdf5_version=1.8.15.1
hdf5_version_short=1.8.15
hdf5_build_no=100

export LD_LIBRARY_PATH=$mpi/lib:$mpi/include:$ana_path/lib:$LD_LIBRARY_PATH
export LD_RUN_PATH=$LD_LIBRARY_PATH
export PYTHONPATH=$PYTHONPATH:$ana_path/lib/python2.7/site-packages
export PATH=$PATH:$ana_path/bin/
export CC=$mpicc

$PYTHON setup.py configure --hdf5=$ana_path
$PYTHON setup.py configure --hdf5-version=$hdf5_version_short
$PYTHON setup.py configure --mpi
$PYTHON setup.py build
$PYTHON setup.py install
