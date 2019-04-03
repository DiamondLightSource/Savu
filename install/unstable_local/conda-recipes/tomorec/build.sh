#!/bin/bash
mkdir build
cd build
git clone git@github.com:dkazanc/TomoRec.git
conda build TomoRec/Wrappers/Python/conda-recipe --numpy 1.15 --python 2.7
conda install -y -q --use-local tomorec
cd ../
rm -r -f build
