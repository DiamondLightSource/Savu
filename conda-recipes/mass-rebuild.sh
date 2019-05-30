#!/bin/sh

set -e -x

module purge
module load python/3.7

# our conda interpreter
CONDA=$(which conda)

# sregistry setup
# AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are necessary for this to work...
# come and ask me for them, export them in your shell, but never commit them!
export SREGISTRY_S3_BUCKET=singularity-savu
export SREGISTRY_DATABASE=/dls/tmp/$USER/singularity
export SREGISTRY_STORAGE=/dls/tmp/$USER/singularity/shub

# singularity
export SINGULARITY_CACHEDIR=/scratch/singularity
export SINGULARITY_TMPDIR=/scratch/tmp

# pull our centos6 conda build image in
sregistry pull s3://centos6/conda-build
CENTOS6_CONDA_BUILD=$(sregistry get centos6/conda-build)

SINGULARITY_EXEC="singularity exec -B /scratch,/dls_sw/apps"

# FFTW -> https://jira.diamond.ac.uk/browse/SCI-8695
$SINGULARITY_EXEC $CENTOS6_CONDA_BUILD $CONDA build --user savu-dep fftw

# OpenMPI -> https://jira.diamond.ac.uk/browse/SCI-8694
$SINGULARITY_EXEC $CENTOS6_CONDA_BUILD $CONDA build --user savu-dep openmpi

# HDF5 -> https://jira.diamond.ac.uk/browse/SCI-8696
$SINGULARITY_EXEC $CENTOS6_CONDA_BUILD $CONDA build --user savu-dep -c savu-dep hdf5

