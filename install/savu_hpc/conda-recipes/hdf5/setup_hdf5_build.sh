#!/bin/bash
#set things up for versions, releases etc.
export PATCH_HDF="hdf5-"$VERSION_HDF
export RELEASE_HDF=${PATCH_HDF%.*}
# get openmpi version
openmpi_ver_string=$(mpicxx --showme:version)
openmpi_version=$(echo $openmpi_ver_string | sed -ne 's/[^0-9]*\(\([0-9]\.\)\{0,4\}[0-9][^.]\).*/\1/p')
VERSION_TMP=$VERSION_HDF"_openmpi"$openmpi_version
export VERSION_HDF=$VERSION_TMP

conda build . --numpy 1.15 --python 3.7
