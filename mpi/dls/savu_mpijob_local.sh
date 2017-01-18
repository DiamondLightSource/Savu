#!/bin/bash
module load savu/1.2

echo "SAVU_MPI_LOCAL:: Running Job"

nNodes=1
nCoresPerNode=`nproc`
nGPUs=$(python -c "import savu.core.utils as cu; p, count = cu.get_available_gpus(); print count")


echo "***********************************************"
echo -e "\tRunning on $nCoresPerNode CPUs and $nGPUs GPUs"
echo "***********************************************"

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
export PYTHONPATH=$savupath:$PYTHONPATH
filename=$savupath/savu/tomo_recon.py

echo "running on host: "$HOSTNAME
echo "Processes running are : ${nCPUs}"

processes=`bc <<< "$nCPUs"`

for i in $(seq 0 $((nGPUs-1))); do GPUs+="GPU$i " ; done
for i in $(seq 0 $((nCPUs-1-nGPUs))); do CPUs+="CPU$i " ; done
CPUs=$(echo $GPUs$CPUs | tr ' ' ,)

mpirun -np $nCPUs python $filename $datafile $processfile $outpath -n $CPUs -v $options

echo "SAVU_MPI_LOCAL:: Process complete"
exit
