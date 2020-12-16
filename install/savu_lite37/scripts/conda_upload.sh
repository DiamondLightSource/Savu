#!/bin/bash

PKG_NAME=savu-lite
CONDA_TOKEN=$(cat $HOME/secrets/my_secret.json)

# upload the package to conda
$CONDA/bin/anaconda -v --show-traceback --token $CONDA_TOKEN upload /usr/share/miniconda3/envs/savu/conda-bld/linux-64/savu-lite-3.0-py37_0.tar.bz2 --force --label dev
