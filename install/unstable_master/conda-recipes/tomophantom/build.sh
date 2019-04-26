#!/bin/bash
mkdir build
cd build
git clone https://github.com/dkazanc/TomoPhantom.git
export CIL_VERSION=1.2_1
conda build TomoPhantom/Wrappers/Python/conda-recipe --numpy 1.15 --python 3.7
conda install -y -q --use-local tomophantom
cd ../
rm -r -f build
