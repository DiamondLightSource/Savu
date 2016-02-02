#!/bin/bash
datafile=$1
processfile=$2
outpath=$3
outname=savu
nNodes=1
nCPUs=8

filepath=`which savu_mpijob.sh`

echo "SAVU_LAUNCHER:: Running Job"

bsub -Is -n $nCPUs -J savu_launcher -o savu_launcher.out -e savu_launcher.err "sh $filepath $datafile $processfile $outpath $nCPUs"

echo "SAVU_LAUNCHER:: Job Complete, preparing output..."

