#!/bin/bash

# unset unused old fortran flags
unset F90 F77

# remove --as-needed, which causes problems for downstream builds,
# seen in failures in petsc, slepc, and hdf5 at least
export LDFLAGS="${LDFLAGS/-Wl,--as-needed/}"

# this might not be needed?
export FCFLAGS="$FFLAGS"

#export CC=/usr/bin/gcc
#export CXX=/usr/bin/g++
#export FC=/usr/bin/gfortran
#export LD=/usr/bin/ld

# avoid absolute-paths in compilers
export CC=$(basename "$CC")
export CXX=$(basename "$CXX")
export FC=$(basename "$FC")

if [ $(uname) == Darwin ]; then
    if [[ ! -z "$CONDA_BUILD_SYSROOT" ]]; then
        export CFLAGS="$CFLAGS -isysroot $CONDA_BUILD_SYSROOT"
        export CXXFLAGS="$CXXFLAGS -isysroot $CONDA_BUILD_SYSROOT"
    fi
    export LDFLAGS="$LDFLAGS -Wl,-rpath,$PREFIX/lib"
fi

export LIBRARY_PATH="$PREFIX/lib:/lib64"

#export CPPFLAGS="$CPPFLAGS -I/usr/include"
#export LIBS="$LIBS -L/lib64 -libverbs"
export LDFLAGS="$LDFLAGS -Wl,-rpath,$PREFIX/lib,-rpath-link,/lib64"

./configure --prefix=$PREFIX \
            --disable-dependency-tracking \
            --with-wrapper-cflags="-I$PREFIX/include" \
            --with-wrapper-cxxflags="-I$PREFIX/include" \
            --with-wrapper-fflags="-I$PREFIX/include" \
            --with-wrapper-fcflags="-I$PREFIX/include" \
            --with-wrapper-ldflags="-L$PREFIX/lib -Wl,-rpath,$PREFIX/lib" \
            --disable-wrapper-rpath \
            --disable-wrapper-runpath \
            --enable-orterun-prefix-by-default \
            --enable-mpirun-prefix-by-default \
            --with-verbs=/usr \
            --with-verbs-libdir=/usr/lib64 \
	    --enable-mpi-fortran=no \
            --with-sge

make -j"${CPU_COUNT:-1}"
make install
