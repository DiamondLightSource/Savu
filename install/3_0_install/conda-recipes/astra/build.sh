#!/bin/bash

nvcc=`command -v nvcc`
cuda=${nvcc%/bin/nvcc}

savu_path=`command -v savu`
ana_path=${savu_path%/savu}
prefix=${ana_path%/bin}/lib/python3.6/site-packages/astra
export PATH=$ana_path:$PATH

cd build/linux

if [ "$cuda" ]; then
    ./configure --with-cuda=$cuda --with-python --prefix=$prefix
else
    echo "cuda has not been found."
    ./configure --with-python --prefix=$prefix
fi

make -j 4
make install

