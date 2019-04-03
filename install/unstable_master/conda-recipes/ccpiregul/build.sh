#!/bin/bash
mkdir build
cd build
git clone https://github.com/vais-ral/CCPi-Regularisation-Toolkit.git
export CIL_VERSION=19.03
conda build CCPi-Regularisation-Toolkit/recipe/ --numpy 1.15 --python 2.7 --no-test
conda install -y -q --use-local ccpi-regulariser=${CIL_VERSION}
cd ../
rm -r -f build
