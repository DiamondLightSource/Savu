#!/bin/sh

set -e -x

module purge
module load python/3.8

# our conda interpreter
CONDA=$(which conda)
IMAGE=centos7/conda-build
LOCAL_IMAGE=/scratch/singularity/images/savu-conda.simg

# sregistry setup
export SREGISTRY_GOOGLE_STORAGE_BUCKET=singularity-savu
export SREGISTRY_DATABASE=/dls/science/users/$USER/singularity
export SREGISTRY_STORAGE=${SREGISTRY_DATABASE}/shub
export GOOGLE_APPLICATION_CREDENTIALS=$HOME/.singularity-savu-google-storage.json

# activate google-storage backend
sregistry backend activate google-storage

# singularity
export SINGULARITY_CACHEDIR=/scratch/singularity
export SINGULARITY_TMPDIR=/scratch/tmp

# if the remote image in the GCP bucket needs to get a rebuild, remove it and its local copy with:
#
#sregistry delete -f google-storage://$IMAGE
#sregistry rm $IMAGE
#
# this will trigger a rebuild on the next line!


# pull our centos7 conda build image in if necessary. If it doesn't exist in the bucket, build it locally and push it (if possible)
sregistry get $IMAGE || \
 	sregistry pull google-storage://$IMAGE || ( \
	rm -f $LOCAL_IMAGE && \
	sudo --preserve-env=SINGULARITY_CACHEDIR,SINGULARITY_TMPDIR singularity build $LOCAL_IMAGE Singularity && \
	sregistry add --copy --name $IMAGE $LOCAL_IMAGE && (\
	sregistry push --name $IMAGE $LOCAL_IMAGE || \
	echo "Could not push to google-storage bucket!"))



# get its location on the file system (somewhere in SREGISTRY_STORAGE)
CENTOS7_CONDA_BUILD=$(sregistry get $IMAGE)

SINGULARITY_EXEC="singularity exec -B /scratch,/dls_sw/apps"

# FFTW -> https://jira.diamond.ac.uk/browse/SCI-8695
$SINGULARITY_EXEC $CENTOS7_CONDA_BUILD $CONDA build --user savu-dep fftw

# OpenMPI -> https://jira.diamond.ac.uk/browse/SCI-8694
$SINGULARITY_EXEC $CENTOS7_CONDA_BUILD $CONDA build --user savu-dep openmpi

# HDF5 -> https://jira.diamond.ac.uk/browse/SCI-8696
$SINGULARITY_EXEC $CENTOS7_CONDA_BUILD $CONDA build --user savu-dep -c savu-dep hdf5

# mpi4py -> https://jira.diamond.ac.uk/browse/SCI-8711
$SINGULARITY_EXEC $CENTOS7_CONDA_BUILD $CONDA build --user savu-dep -c savu-dep --python 2.7 mpi4py

# h5py -> https://jira.diamond.ac.uk/browse/SCI-8713
$SINGULARITY_EXEC $CENTOS7_CONDA_BUILD $CONDA build --user savu-dep -c savu-dep --python 2.7 h5py
