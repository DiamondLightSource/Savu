#!/bin/bash
mkdir build
cd build
git clone https://github.com/vais-ral/CCPi-Reconstruction.git
export CIL_VERSION=19.03
conda build CCPi-Reconstruction/recipes/library --numpy 1.15 --python 2.7
conda install -y -q --use-local cil_reconstruction=${CIL_VERSION}
cd ../
rm -r -f build
