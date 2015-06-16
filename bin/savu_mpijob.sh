#!/bin/bash
module load global/cluster
module load python/ana
source activate mpi2
module load openmpi/1.6.5

savupath=$1
datafile=$2
processfile=$3
outfile=$4
nCPUs=$5

export PYTHONPATH=$savupath:$PYTHONPATH
filename=$savupath/savu/tomo_recon_mpi.py

UNIQHOSTS=${TMPDIR}/machines-u
awk '{print $1 }' ${PE_HOSTFILE} | uniq > ${UNIQHOSTS}
uniqslots=$(wc -l <${UNIQHOSTS})
echo "number of uniq hosts: ${uniqslots}"
echo "running on these hosts:"
cat ${UNIQHOSTS}

processes=`bc <<< "$((uniqslots*nCPUs))"`

nCPUs=$((nCPUs-1))
CPUs=CPU0

if [ $nCPUs -gt 0 ]; then
	for i in $(eval echo {1..$nCPUs})
  	do
		echo $i
		CPUs=$CPUs,CPU$i
	done
fi


echo "Processes running are : ${processes}"

mpirun -np ${processes} \
       -x LD_LIBRARY_PATH \
       --hostfile ${UNIQHOSTS} \
       python $filename $savupath$datafile $savupath$processfile $outfile -n $CPUs

