#!/bin/bash
module load global/testcluster
#module load global/cluster

module load python/anaconda-cctbx

module load cuda/5.0

#source activate mpi2
source activate mpi5
module load openmpi/1.6.5
export PYTHONPATH=$PYTHONPATH:/home/clb02321/DAWN_stable/FastXRF/src/
#export LD_LIBRARY_PATH=/dls_sw/prod/tools/RHEL6-x86_64/openmpi/1-6-5/prefix/lib:$LD_LIBRARY_PATH

savupath=$1
datafile=$2
processfile=$3
outfile=$4
nCPUs=$5
nGPUs=2

export PYTHONPATH=$savupath:$PYTHONPATH
filename=$savupath/savu/tomo_recon.py

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
		CPUs=$CPUs,CPU$i
	done
fi

#CPUs=$CPUs,GPU0,GPU1
#echo CPUs


echo "Processes running are : ${processes}"

mpirun -np ${processes} \
       -mca btl self,openib,sm \
       -mca orte_forward_job_control 1 \
       -x LD_LIBRARY_PATH \
       --hostfile ${UNIQHOSTS} \
       python $filename $datafile $processfile $outfile -n $CPUs

