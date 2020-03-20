#!/bin/bash

# This script should be used to test Local MPI runs on
# RELEASED versions of Savu. It takes the version of Savu
# as seen in `module avail savu` as it's first argument,
# and forwards the rest of the arguments to Savu itself
#
# Example usage:
# bin/savu_mpi_local.sh 2.4 data.nxs processlist.nxs /scratch/output

echo "SAVU_MPI_LOCAL:: Running Job"

nNodes=1
nCoresPerNode=`grep '^core id' /proc/cpuinfo |sort -u|wc -l`
nGPUs=$(nvidia-smi -L | wc -l)

echo "***********************************************"
echo -e "\tRunning on $nCoresPerNode CPUs and $nGPUs GPUs"
echo "***********************************************"

module load savu/$1
shift 1

datafile=$1
processfile=$2
outpath=$3
shift 3
options=$@

DIR="$(cd "$(dirname "$0")" && pwd)"
savupath=$(python -c "import savu, os; print savu.__path__[0]")
savupath=${savupath%/savu}
echo "savupath is:" $savupath

nCPUs=$((nNodes*nCoresPerNode))

# launch mpi job
filename=$savupath/savu/tomo_recon.py

echo "running on host: "$HOSTNAME
echo "Processes running are : ${nCPUs}"

processes=`bc <<< "$nCPUs"`

for i in $(seq 0 $((nGPUs-1))); do GPUs+="GPU$i " ; done
for i in $(seq 0 $((nCPUs-1-nGPUs))); do CPUs+="CPU$i " ; done
CPUs=$(echo $GPUs$CPUs | tr ' ' ,)

echo "running the savu mpi local job"
PYTHONPATH=$savupath:$PYTHONPATH mpirun -np $nCPUs -mca btl ^openib python $filename $datafile $processfile $outpath -n $CPUs -v $options


echo "SAVU_MPI_LOCAL:: Process complete"

