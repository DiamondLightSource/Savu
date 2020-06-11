#!/bin/bash
set -ex

export OMPI_MCA_plm=isolated
export OMPI_MCA_btl_vader_single_copy_mechanism=none
export OMPI_MCA_rmaps_base_oversubscribe=yes

#export CPPFLAGS="$CPPFLAGS -I/usr/include"
#export LIBS="$LIBS -L/lib64 -L/usr/lib64 -libverbs"
#export LDFLAGS="$LDFLAGS -Wl,-rpath -Wl,/lib64"
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/lib64"

command -v mpiexec
MPIEXEC="${PWD}/mpiexec.sh"

pushd "tests"

command -v ompi_info
ompi_info

$MPIEXEC --help

$MPIEXEC -n 4 python test_exec.py


command -v mpicc
mpicc -show

mpicc $CFLAGS $LDFLAGS helloworld.c -o helloworld_c
$MPIEXEC -n 4 ./helloworld_c

popd
