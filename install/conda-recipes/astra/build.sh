#!/bin/bash

nvcc=`command -v nvcc`
cuda=${nvcc%/bin/nvcc}

DIR="$(cd "$(dirname "$0")" && pwd)"
export PATH=$DIR/build/linux:$PATH

ana_path=`command -v anaconda`
ana_path=${ana_path%/bin/anaconda}
prefix=$anapath/lib/python2.7/site-packages/astra

cd $DIR/build/linux

if [ "$cuda" ]; then
    ./configure --with-cuda=$cuda --with-python --prefix=$prefix
else
    echo "cuda has not been found."
    ./configure --with-python --prefix=$prefix
fi

make
make install

