#!/bin/bash
#module load global/testcluster
module load global/cluster

module load python/anaconda-savu
source activate savu_mpi1

#module load savu/1.0_new_env
#activate_env

savupath=$1
datafile=$2
processfile=$3
outfile=$4
nCPUs=$5
shift 5
nGPUs=4

if [ $nGPUs -gt $nCPUs ]; then
    nGPUs=$nCPUs
fi


export PYTHONPATH=$savupath:$PYTHONPATH
filename=$savupath/savu/tomo_recon.py

UNIQHOSTS=${TMPDIR}/machines-u
awk '{print $1 }' ${PE_HOSTFILE} | uniq > ${UNIQHOSTS}
uniqslots=$(wc -l <${UNIQHOSTS})
echo "number of uniq hosts: ${uniqslots}"
echo "running on these hosts:"
cat ${UNIQHOSTS}

processes=`bc <<< "$((uniqslots*nCPUs))"`

for i in $(seq 0 $((nGPUs-1))); do GPUs+="GPU$i " ; done
for i in $(seq 0 $((nCPUs-1-nGPUs))); do CPUs+="CPU$i " ; done
#for i in $(seq 0 $((nCPUs-1))); do CPUs+="CPU$i " ; done
CPUs=$(echo $GPUs$CPUs | tr ' ' ,)
echo $CPUs
echo $nCPUs $nGPUs

echo "Processes running are : ${processes}"

mpirun -np ${processes} \
       -mca btl self,openib,sm \
       -mca orte_forward_job_control 1 \
       -x LD_LIBRARY_PATH \
       --hostfile ${UNIQHOSTS} \
       python $filename $datafile $processfile $outfile -n $CPUs -v $@

        #h5perf -i 3 -B 512K -d 1 -e 63M -x 512K -X 512K

