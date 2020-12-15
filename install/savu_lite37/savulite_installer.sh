#!/bin/bash

conda config --add channels default
conda config --prepend channels conda-forge
conda config --prepend channels astra-toolbox/label/dev
conda config --prepend channels ccpi
conda config --prepend channels dkazanc
conda config --set anaconda_upload no
conda config --set channel_priority flexible
conda config --set auto_activate_base false
conda config --set show_channel_urls true
conda config --set unsatisfiable_hints true

conda install --yes conda-build anaconda-client setuptools
conda build .
