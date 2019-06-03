#!/bin/sh

set -e -x

module purge
module load python/3.7

# our conda interpreter
CONDA=$(which conda)
IMAGE=centos6/conda-build
LOCAL_IMAGE=/scratch/singularity/images/savu-conda.simg

# sregistry setup
# AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are necessary for this to work...
# come and ask me for them, export them in your shell, but never commit them!
export SREGISTRY_S3_BUCKET=singularity-savu
export SREGISTRY_DATABASE=/dls/tmp/$USER/singularity
export SREGISTRY_STORAGE=/dls/tmp/$USER/singularity/shub

# activate S3 backend
sregistry backend activate s3

# singularity
export SINGULARITY_CACHEDIR=/scratch/singularity
export SINGULARITY_TMPDIR=/scratch/tmp

# if the remote image in the S3 bucket needs to get a rebuild, remove it and its local copy with:
#
#sregistry delete s3://$IMAGE
#sregistry rm $IMAGE
#
# this will trigger a rebuild on the next line!


# pull our centos6 conda build image in if necessary. If it doesn't exist in the bucket, build it locally and push it (if possible)
sregistry get $IMAGE || \
 	sregistry pull s3://$IMAGE || ( \
	rm -f $LOCAL_IMAGE && \
	sudo --preserve-env=SINGULARITY_CACHEDIR,SINGULARITY_TMPDIR singularity build $LOCAL_IMAGE Singularity && \
	sregistry add --copy --name $IMAGE $LOCAL_IMAGE && (\
	sregistry push --name $IMAGE $LOCAL_IMAGE || \
	echo "Could not push to S3 bucket!"))



# get its location on the file system (somewhere in SREGISTRY_STORAGE)
CENTOS6_CONDA_BUILD=$(sregistry get $IMAGE)

SINGULARITY_EXEC="singularity exec -B /scratch,/dls_sw/apps"

# FFTW -> https://jira.diamond.ac.uk/browse/SCI-8695
$SINGULARITY_EXEC $CENTOS6_CONDA_BUILD $CONDA build --user savu-dep fftw

# OpenMPI -> https://jira.diamond.ac.uk/browse/SCI-8694
$SINGULARITY_EXEC $CENTOS6_CONDA_BUILD $CONDA build --user savu-dep openmpi

# HDF5 -> https://jira.diamond.ac.uk/browse/SCI-8696
$SINGULARITY_EXEC $CENTOS6_CONDA_BUILD $CONDA build --user savu-dep -c savu-dep hdf5

# mpi4py -> https://jira.diamond.ac.uk/browse/SCI-8711
$SINGULARITY_EXEC $CENTOS6_CONDA_BUILD $CONDA build --user savu-dep -c savu-dep --python 2.7 mpi4py

# h5py -> https://jira.diamond.ac.uk/browse/SCI-8713
$SINGULARITY_EXEC $CENTOS6_CONDA_BUILD $CONDA build --user savu-dep -c savu-dep --python 2.7 h5py
