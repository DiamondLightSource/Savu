#!/bin/bash
#set things up for versions, patches, releases etc.
export PATCH_HDF="hdf5-"$VERSION_HDF
export RELEASE_HDF=${PATCH_HDF%.*}
# get openmpi version
openmpi_ver_string=$(mpicxx --showme:version)
openmpi_version=$(echo $openmpi_ver_string | sed -ne 's/[^0-9]*\(\([0-9]\.\)\{0,4\}[0-9][^.]\).*/\1/p')
VERSION_TMP=$VERSION_HDF"_openmpi"$openmpi_version
export VERSION_HDF=$VERSION_TMP

numpy_full=$(python -c "import numpy; print(numpy.__version__)")
export NUMPY_VER="${numpy_full:0:4}"
python_full=$(python --version)
export PYTHON_VER="${python_full:7:3}"

conda build . --python $PYTHON_VER --numpy $NUMPY_VER
