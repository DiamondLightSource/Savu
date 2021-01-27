#!/usr/bin/env bash

export LDFLAGS="${LDFLAGS} -L${PREFIX}/lib"
export CFLAGS="${CFLAGS} -I${PREFIX}/include -O3 -fomit-frame-pointer -fstrict-aliasing -ffast-math"

CONFIGURE="./configure --prefix=$PREFIX --with-pic --enable-threads --disable-static"

if [[ `uname` == Darwin ]] && [[ "$CC" != "clang" ]]
then
    CONFIGURE=${CONFIGURE}" --enable-openmp"
elif [[ `uname` == Linux ]]
then
    CONFIGURE=${CONFIGURE}" --enable-openmp"
fi

# (Note exported LDFLAGS and CFLAGS vars provided above.)
BUILD_CMD="make -j${CPU_COUNT}"
INSTALL_CMD="make install"

# Test suite
# tests are performed during building as they are not available in the
# installed package.
# Additional tests can be run with "make smallcheck" and "make bigcheck"
TEST_CMD="eval cd tests && make check-local && cd -"

#
# We build 3 different versions of fftw:
#
build_cases=(
    # single
    "$CONFIGURE --enable-float --enable-sse --enable-sse2 --enable-avx"
    # double
    "$CONFIGURE --enable-sse2 --enable-avx"
    # long double (SSE2 and AVX not supported)
    "$CONFIGURE --enable-long-double"
)

# first build shared objects
for config in "${build_cases[@]}"
do
    :
    $config --enable-shared --disable-static
    ${BUILD_CMD}
    ${INSTALL_CMD}
    ${TEST_CMD}
done

