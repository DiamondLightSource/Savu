#!/bin/bash
module load global/cluster
#module load python/ana

MPIRUN=/dls_sw/prod/tools/RHEL6-x86_64/openmpi/1-6-5/prefix/bin/mpirun
PYTHON=/dls_sw/prod/tools/RHEL6-x86_64/defaults/bin/dls-python

export PYTHONPATH=/home/ssg37927/Savu:$PYTHONPATH

UNIQHOSTS=${TMPDIR}/machines-u
awk '{print $1 }' ${PE_HOSTFILE} | uniq > ${UNIQHOSTS}
uniqslots=$(wc -l <${UNIQHOSTS})
echo "number of uniq hosts: ${uniqslots}"
echo "running on these hosts:"
cat ${UNIQHOSTS}

processes=`bc <<< "$uniqslots*8"`

echo "Processes running are : ${processes}"

mpirun -np ${processes} \
       --hostfile ${UNIQHOSTS} \
       $PYTHON /home/ssg37927/Savu/savu/mpi_test/dls/framework_test_runner.py $@