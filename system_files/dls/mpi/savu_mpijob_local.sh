#!/bin/bash

# This script should be used to test Local MPI runs on
# RELEASE/Locally installed versions of Savu.
#
# The Python environment containing Savu and all dependencies
# must already be activated.
#
# Example usage:
# savu_mpijob_local.sh test_data/data/24737.nxs test_data/process_lists/ica_test.nxs /scratch/output

echo "SAVU_MPI_LOCAL:: Running Job with Savu at $1"

nNodes=1
nCoresPerNode=`lscpu --all --parse=CORE,SOCKET | grep -Ev "^#" | wc -l`
nGPUs=$(nvidia-smi -L | wc -l)

echo "***********************************************"
echo -e "\tRunning on $nCoresPerNode CPUs and $nGPUs GPUs"
echo "***********************************************"

datafile=$1
processfile=$2
outpath=$3
shift 3
options=$@

savupath=$(python -c "import savu; print(savu.__path__[0])")
savupath=${savupath%/savu}
echo "savupath is:" $savupath

nCPUs=$((nNodes*nCoresPerNode))

# launch mpi job
export PYTHONPATH=$savupath:$PYTHONPATH
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
