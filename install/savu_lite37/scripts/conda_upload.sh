#!/bin/bash

PKG_NAME=savu-lite
CONDA_TOKEN=$(cat $HOME/secrets/my_secret.json)

# upload the package to conda
find /usr/share/miniconda3/envs/savu/conda-bld/linux-64/ -name *.tar.bz2 | while read file
do
    echo $file
    $CONDA/bin/anaconda -v --show-traceback --token $CONDA_TOKEN upload $file --force --label dev
done
