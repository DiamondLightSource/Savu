#!/bin/bash

# set compiler wrapper
mpicc=$(command -v mpicc)
mpi=${mpicc%/bin/mpicc}

# set anaconda distribution
ana_path=$(command -v anaconda)
ana_path=${ana_path%/bin/anaconda}
hdf5_build_no=1

export LD_LIBRARY_PATH=$mpi/lib:$mpi/include:$ana_path/lib:$LD_LIBRARY_PATH
export LD_RUN_PATH=$LD_LIBRARY_PATH
export CC=$mpicc
export HDF5_MPI="ON"

source $ana_path/bin/activate $ana_path
export PYTHONPATH=$PYTHONPATH:$(python -c 'import site; print(site.getsitepackages()[0])')

echo Running with Python: $(which python)
echo "********************************************************************"
echo $ana_path
conda list --explicit > temppack.txt
checkpack_var=$(grep "hdf5" temppack.txt)
shortened_string=${checkpack_var##*/}
version_explicit_t=${shortened_string%-*}
version_explicit=${version_explicit_t##*-}
version_explicit_HDF5=${version_explicit:0:6}
rm -rf temppack.txt
echo $version_explicit_HDF5
echo "********************************************************************"
$PYTHON setup.py configure --mpi --hdf5=$ana_path --hdf5-version=$version_explicit_HDF5
$PYTHON setup.py build
$PYTHON setup.py install
