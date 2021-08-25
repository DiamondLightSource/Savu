#!/bin/bash
export VERSION=4.0_$(date +%Y.%m)
conda install --yes conda-build anaconda-client setuptools
#conda build . -c https://conda.anaconda.org/conda-forge/ -c https://conda.anaconda.org/astra-toolbox/label/dev/ -c https://conda.anaconda.org/savu-dep/ -c https://conda.anaconda.org/ccpi/ --numpy 1.15 --python 3.7 --override-channels
conda build . -c defaults -c conda-forge -c astra-toolbox/label/dev/ -c savu-dep -c ccpi --override-channels
