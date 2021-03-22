#!/bin/bash

export LD_RUN_PATH=$LD_LIBRARY_PATH

# set compiler wrapper
mpicc=$(command -v mpicc)
mpi=${mpicc%/bin/mpicc}
export LD_LIBRARY_PATH=$mpi:$mpi/lib:$mpi/include:$LD_LIBRARY_PATH
export LD_RUN_PATH=$LD_LIBRARY_PATH

# check anaconda distribution
# ana_path=$(command -v savu)

CC=$mpicc ./configure --with-zlib --enable-parallel --enable-shared --prefix=$PREFIX
make -j$(nproc)
make install

rm -rf $PREFIX/share/hdf5_examples
