#!/bin/bash
module load global/cluster
module load python/ana
source activate mpi2
module load openmpi/1.6.5

export PYTHONPATH=/home/ssg37927/savu/Savu:$PYTHONPATH

UNIQHOSTS=${TMPDIR}/machines-u
awk '{print $1 }' ${PE_HOSTFILE} | uniq > ${UNIQHOSTS}
uniqslots=$(wc -l <${UNIQHOSTS})
echo "number of uniq hosts: ${uniqslots}"
echo "running on these hosts:"
cat ${UNIQHOSTS}

processes=`bc <<< "$uniqslots*8"`

echo "Processes running are : ${processes}"

mpirun -np ${processes} \
       -x LD_LIBRARY_PATH \
       --hostfile ${UNIQHOSTS} \
       python /home/ssg37927/savu/Savu/savu/tomo_recon_mpi.py $@