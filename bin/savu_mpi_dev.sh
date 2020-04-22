#!/bin/bash

# This script should be used to test Local MPI runs on
# DEVELOPMENT versions of Savu. It takes the path to the
# Savu source to be used as its first argument, and the rest
# are forwarded to Savu itself.
#
# The Python environment containing all the dependencies of Savu
# must already be activated.
#
# Example usage with full paths:
# /scratch/dev/savu/bin/savu_mpi_dev.sh /scratch/dev/savu /scratch/dev/savu/test_data/data/24737.nxs /scratch/dev/savu/test_data/process_lists/ica_test.nxs /scratch/output
#
# Example usage while inside the repository root:
# bin/savu_mpi_local_dev.sh . test_data/data/24737.nxs test_data/process_lists/ica_test.nxs /scratch/output

echo "SAVU_MPI_LOCAL:: Running Job with Savu at $1"

nNodes=1
nCoresPerNode=`lscpu --all --parse=CORE,SOCKET | grep -E "^[0-9]" | wc -l`
nGPUs=$(nvidia-smi -L | wc -l)

echo "***********************************************"
echo -e "\tRunning on $nCoresPerNode CPUs and $nGPUs GPUs"
echo "***********************************************"

savupath=$1
datafile=$2
processfile=$3
outpath=$4
shift 4
options=$@

DIR="$(cd "$(dirname "$0")" && pwd)"
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

echo "running the savu mpi local job with process parameters: $CPUs"

echo "Using python at $(which python)"

OMPI_MCA_opal_cuda_support=true PYTHONPATH=$savupath:$PYTHONPATH mpirun -np $nCPUs --use-hwthread-cpus \
                                                                -mca btl self,vader -mca orte_forward_job_control 1 \
                                                                python $filename $datafile $processfile $outpath -n $CPUs -v $options

echo "SAVU_MPI_LOCAL:: Process complete"
