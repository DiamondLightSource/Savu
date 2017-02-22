module load savu/1.2

savupath=$1
datafile=$2
processfile=$3
outfile=$4
nCPUs=$5
nGPUs=$6
shift 6

export PYTHONPATH=$savupath:$PYTHONPATH
filename=$savupath/savu/tomo_recon.py

UNIQHOSTS=${TMPDIR}/machines-u
awk '{print $1 }' ${PE_HOSTFILE} | uniq > ${UNIQHOSTS}
uniqslots=$(wc -l <${UNIQHOSTS})
echo "number of uniq hosts: ${uniqslots}"
echo "running on these hosts:"
cat ${UNIQHOSTS}

typeset TMP_FILE=$( mktemp )
touch "${TMP_FILE}"
cp -p ${UNIQHOSTS} "${TMP_FILE}"
sed -e 's/$/ slots=${nCPUs}/' -i ${TMP_FILE}

processes=`bc <<< "$((uniqslots*nCPUs))"`

for i in $(seq 0 $((nGPUs-1))); do GPUs+="GPU$i " ; done
for i in $(seq 0 $((nCPUs-1-nGPUs))); do CPUs+="CPU$i " ; done
CPUs=$(echo $GPUs$CPUs | tr ' ' ,)
echo $CPUs

echo "Processes running are : ${processes}"

mpirun -np ${processes} \
       -mca btl self,openib,sm \
       -x LD_LIBRARY_PATH \
       --hostfile ${UNIQHOSTS} \
       python $filename $datafile $processfile $outfile -n $CPUs -v $@
