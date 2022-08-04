#!/bin/bash

echo "SAVU_PRE_RUN_MPI_LOCAL:: Running Job"

nNodes=1
nCoresPerNode=`lscpu --all --parse=CORE,SOCKET | grep -E "^[0-9]" | wc -l`
nGPUs=$(nvidia-smi -L | wc -l)

echo "***********************************************"
echo -e "\tRunning on $nCoresPerNode CPUs and $nGPUs GPUs"
echo "***********************************************"

datafile=$1
outpath=$2
shift 2
options=$@

savupath=$(python -c "import savu, os; print (savu.__path__[0])")
savupath=${savupath%/savu}
echo "savupath is:" $savupath

nCPUs=$((nNodes*nCoresPerNode))
nCPUs=4

# launch mpi job
filename=$savupath/savu/pre_run.py

echo "running on host: "$HOSTNAME
echo "Processes running are : ${nCPUs}"

processes=`bc <<< "$nCPUs"`

for i in $(seq 0 $((nGPUs-1))); do GPUs+="GPU$i " ; done
for i in $(seq 0 $((nCPUs-1-nGPUs))); do CPUs+="CPU$i " ; done
CPUs=$(echo $GPUs$CPUs | tr ' ' ,)

echo "running the savu pre-run mpi local job"
mpirun -np $nCPUs -mca btl ^openib python $filename $datafile $outpath -n $CPUs $options

echo "SAVU_PRE_RUN_MPI_LOCAL:: Process complete"
