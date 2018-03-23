#!/bin/bash
module load openmpi/gcc/4.8.2/1.6.5
module load python/2.7.8
module load python278/scipy
module load python278/numpy

datafile=$1
processfile=$2
outfile=$3
nCPUs=$4

filename=tomo_recon
echo $PYTHONPATH
nCPUs=$((nCPUs-1))
CPUs=CPU0

if [ $nCPUs -gt 0 ]; then
    for i in $(eval echo {1..$nCPUs})
    do
        CPUs=$CPUs,CPU$i
    done
fi
echo "Processes running are : ${processes}"

mpirun $filename $datafile $processfile $outfile -n $CPUs

