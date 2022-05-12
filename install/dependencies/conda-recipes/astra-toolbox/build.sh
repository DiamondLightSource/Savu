#!/bin/bash

nvcc=`command -v nvcc`
cuda=${nvcc%/bin/nvcc}

cd $SRC_DIR/build/linux
chmod +x autogen.sh
./autogen.sh

if [ "$cuda" ]; then
  ./configure --with-cuda=$cuda \
              --with-python \
              --with-install-type=module
else
    echo "cuda has not been found will configure without it."
    ./configure --with-python \
                --with-install-type=module
fi

make -j 4
make install
