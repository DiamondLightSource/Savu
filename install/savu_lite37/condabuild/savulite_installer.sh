#!/bin/bash

conda install --yes conda-build anaconda-client setuptools
conda build . -c https://conda.anaconda.org/conda-forge/ -c https://conda.anaconda.org/astra-toolbox/label/dev/ -c https://conda.anaconda.org/savu-dep/ -c https://conda.anaconda.org/ccpi/
