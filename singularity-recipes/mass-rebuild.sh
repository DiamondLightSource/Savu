#!/bin/bash

set -e -x

# sregistry setup
# AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are necessary for this to work...
# come and ask me for them, export them in your shell, but never commit them!
export SREGISTRY_S3_BUCKET=singularity-savu

if test -e /dls/science/users/$USER ; then
	export SREGISTRY_DATABASE=/dls/science/users/$USER/singularity
	export SREGISTRY_STORAGE=${SREGISTRY_DATABASE}/shub
	mkdir -p ${SREGISTRY_STORAGE}
fi

# activate S3 backend
sregistry backend activate s3

# singularity
if test -e /scratch ; then
	export SINGULARITY_CACHEDIR=/scratch/singularity
	export SINGULARITY_TMPDIR=/scratch/tmp
	SUDO_OPTIONS="--preserve-env=SINGULARITY_CACHEDIR,SINGULARITY_TMPDIR"
fi


# images to get a new build -> they will get built in this order!
declare -a images=("SavuDeps" "SavuCore" "SavuAstra")

for image in "${images[@]}" ; do
	echo "##############################"
	echo "#"
	echo "#   Building $image"
	echo "#"
	echo "##############################"
	LOCAL_IMAGE=${image}.simg
	REGISTRY_IMAGE=${image:4}
	REGISTRY_IMAGE=savu/${REGISTRY_IMAGE,,}

	#
	# remove the image, if it has been built before, including from local registry
	#
	rm -f ${LOCAL_IMAGE}
	sregistry get $REGISTRY_IMAGE && sregistry rm $REGISTRY_IMAGE

	#
	#  build the image
	#
	sudo ${SUDO_OPTIONS} singularity build ${LOCAL_IMAGE} Singularity.${image}

	#
	#  add to local registry
	#
	sregistry add --copy --name ${REGISTRY_IMAGE} ${LOCAL_IMAGE}
done
