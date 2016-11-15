 # "Loads up UGE for DLS cluster" ***change this
module load global/cluster

# Adds to relevant paths:
# Savu Anaconda distribution
# openmpi 1.6.5
# cuda 7.0
# fftw 3.3.3
# *** change this
module load python/anaconda-savu
# source activate your_anaconda_env 

# sets run parameters
savupath=$1
datafile=$2
processfile=$3
outfile=$4
nCPUs=$5
shift 5
nGPUs=4

# get path to Savu module containing main
filename=`command -v savu`

# output each host name to the log file
UNIQHOSTS=${TMPDIR}/machines-u
awk '{print $1 }' ${PE_HOSTFILE} | uniq > ${UNIQHOSTS}
uniqslots=$(wc -l <${UNIQHOSTS})
echo "number of uniq hosts: ${uniqslots}"
echo "running on these hosts:"
cat ${UNIQHOSTS}

# get the maximum number of processes
processes=`bc <<< "$((uniqslots*nCPUs))"`

# Set the list of CPU/GPU processes for Savu
for i in $(seq 0 $((nGPUs-1))); do GPUs+="GPU$i " ; done
for i in $(seq 0 $((nCPUs-1-nGPUs))); do CPUs+="CPU$i " ; done
CPUs=$(echo $GPUs$CPUs | tr ' ' ,)
echo $CPUs
echo "Processes running are : ${processes}"

# run the mpijob
mpirun -np ${processes} \
       -mca btl self,openib,sm \
       -mca orte_forward_job_control 1 \
       -x LD_LIBRARY_PATH \
       --hostfile ${UNIQHOSTS} \
       python $filename $datafile $processfile $outfile -n $CPUs -v $@

