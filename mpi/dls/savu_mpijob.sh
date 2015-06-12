#!/bin/bash
module load global/cluster
module load savu
source activate mpi2
module load openmpi/1.6.5

echo "Start Check Output"
which mpicc
which mpirun
echo $LD_LIBRARY_PATH
which python
echo "END Check Output"

UNIQHOSTS=${TMPDIR}/machines-u
awk '{print $1 }' ${PE_HOSTFILE} | uniq > ${UNIQHOSTS}
uniqslots=$(wc -l <${UNIQHOSTS})
echo "number of uniq hosts: ${uniqslots}"
echo "running on these hosts:"
cat ${UNIQHOSTS}

processes=`bc <<< "$uniqslots*6"`

echo "Processes running are : ${processes}"

mpirun -np ${processes} \
       -x LD_LIBRARY_PATH \
       --hostfile ${UNIQHOSTS} \
       python /home/qmm55171/Documents/Git/git_repos/Savu/savu/tomo_recon_mpi.py $@
