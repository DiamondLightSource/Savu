#!/bin/bash
mkdir build
cd build
git clone git@github.com:dkazanc/ToMoBAR.git
conda build ToMoBAR/Wrappers/Python/conda-recipe --numpy 1.15 --python 2.7
conda install -y -q --use-local tomobar
cd ../
rm -r -f build
