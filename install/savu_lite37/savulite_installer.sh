#!/bin/bash

rm -rf ~/.condarc
conda config --add channels defaults
conda config --append channels conda-forge
conda config --append channels astra-toolbox/label/dev
conda config --append channels ccpi
conda config --append channels dkazanc

conda config --set anaconda_upload no
conda config --set channel_priority strict
conda config --set auto_activate_base false
conda config --set show_channel_urls true
conda config --set unsatisfiable_hints true

conda install --yes conda-build anaconda-client setuptools
conda build .
