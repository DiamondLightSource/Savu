
#!/bin/bash

echo "Entering build.sh"
echo "CC: $CC"
which gcc
$CC --version


export LIBRARY_PATH="${PREFIX}/lib"

export CONFIGURE_ARGS="--enable-parallel ${CONFIGURE_ARGS}"
export CC=mpicc
# --as-needed appears to cause problems with fortran compiler detection
# due to missing libquadmath
# unclear why required libs are stripped but still linked
export FFLAGS="${FFLAGS:-} -Wl,--no-as-needed -Wl,--disable-new-dtags"
export LDFLAGS="${LDFLAGS} -Wl,--no-as-needed -Wl,--disable-new-dtags"

echo "CC: $CC"
which gcc
$CC --version
./configure --prefix="${PREFIX}" \
            ${CONFIGURE_ARGS} \
            --with-pic \
            --host="${HOST}" \
            --build="${BUILD}" \
            --with-zlib="${PREFIX}" \
            --with-pthread=yes  \
            --with-default-plugindir="${PREFIX}/lib/hdf5/plugin" \
            --enable-build-mode=production \
	    --disable-cxx \
	    --disable-fortran \
	    --disable-fortran2003

# allow oversubscribing with openmpi in make check
export OMPI_MCA_rmaps_base_oversubscribe=yes

make -j "${CPU_COUNT}" ${VERBOSE_AT}
make check RUNPARALLEL="${RECIPE_DIR}/mpiexec.sh -n 2"
make install

rm -rf $PREFIX/share/hdf5_examples
