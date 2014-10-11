#!/bin/bash
module load global/cluster
module load python/ana
source activate mpi2
module load openmpi/1.6.5
#export LD_LIBRARY_PATH=/dls_sw/prod/tools/RHEL6-x86_64/openmpi/1-6-5/prefix/lib:$LD_LIBRARY_PATH

echo "Start Check Output"
which mpicc
echo $LD_LIBRARY_PATH
which python
echo "END Check Output"


#MPIRUN=/dls_sw/prod/tools/RHEL6-x86_64/openmpi/1-6-5/prefix/bin/mpirun
#PYTHON=/dls_sw/prod/tools/RHEL6-x86_64/defaults/bin/dls-python

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
       python /home/ssg37927/Savu/savu/mpi_test/dls/framework_file_test_runner.py $@