#!/bin/bash

module load global/cluster # "Loads up UGE for DLS cluster" ***change this

echo "SAVU_LAUNCHER:: Running Job"

# filepaths from command line
datafile=$1
processfile=$2
outpath=$3
shift 3

# additional options passed at runtime (see >> savu --help)
options=$@

outname=savu        # the name of the qsub job
nNodes=2            # the number of nodes ***change this
nCoresPerNode=20    # the number of cores per node ***change this

# set relevant filepaths
DIR="$(cd "$(dirname "$0")" && pwd)"
filepath=`command -v savu_mpijob.sh`
savupath=${DIR%/mpi}

# total number of processes
M=$((nNodes*nCoresPerNode))

# set log file path 
log_path=/dls/tmp/savu # ***change this
while [[ $# -gt 1 ]]
do
if [ $1 == "-l" ]; then
  log_path=$2
fi
shift
done

# submit a batch job to your cluster
# node exclusivity is required
# log files are useful for profiling
# ***change this
qsub -N $outname -sync y -j y -o $log_path -e $log_path -pe openmpi $M -l exclusive\
     -l infiniband -l gpu=1 -q medium.q@@com10 $filepath $savupath $datafile $processfile $outpath $nCoresPerNode $@> tmp.txt

# =================== a more detailed description ===================================
#qsub -N $outname         `# name of the qsub job` \
#     -sync y             `# wait for the job to complete before returning` \
#     -j y                `# merge standard error stream to standard output stream` \
#     -o $log_path        `# path used for standard output stream` \
#     -e $log_path        `# path used for standard error stream` \
#     -pe openmpi $M      `# set the parallel environment to openmpi` \
#     -l exclusive        `# node exclusivity` \
#     -l infiniband       `# infiniband connection` \
#     -l gpu=1            `# this job requires gpu nodes` \
#     -q medium.q@@com10  `# specify the queue` \
#     $filepath $savupath $datafile $processfile $outpath $nCoresPerNode $options > /dls/tmp/savu/$USER.out  `# launch the mpi job`

echo "SAVU_LAUNCHER:: Job Complete, preparing output..."

# output the log file contents
filename=`echo $outname.o`
jobnumber=`awk '{print $3}' /dls/tmp/savu/$USER.out | head -n 1`
filename=/dls/tmp/savu/$filename$jobnumber

while [ ! -f $filename ]
do
  sleep 2
done

echo "SAVU_LAUNCHER:: Output ready, spooling now"
cat $filename
echo "SAVU_LAUNCHER:: Process complete"

