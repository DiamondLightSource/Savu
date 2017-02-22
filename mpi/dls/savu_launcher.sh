#!/bin/bash
module load savu/1.2
module load global/cluster-quiet

# function for parsing optional arguments
function arg_parse ()
{
  flag=$1
  return=$2
  while [[ $# -gt 3 ]] ; do
    if [ $3 == $flag ] ; then
      eval "$return"=$4
    fi
    shift
  done
}

echo -e "\t SAVU_LAUNCHER:: Running Job"

# set parameters
datafile=$1
processfile=$2
outpath=$3
shift 3
options=$@

outname=savu
nNodes=2
nCoresPerNode=20
nGPUs=4

# get the Savu path
DIR="$(cd "$(dirname "$0")" && pwd)"
filepath=$DIR'/savu_mpijob.sh'
savupath=$(python -c "import savu, os; print savu.__path__[0]")
savupath=${savupath%/savu}

echo -e "\t The Savu path is:" $savupath

M=$((nNodes*nCoresPerNode))

# set the output folder
arg_parse "-f" foldername "$@"
if [ ! $foldername ] ; then
  IFS=. read path ext <<<"${datafile##*-}"
  foldername=$(date +%Y%m%d%H%M%S)"_$(basename $path)"
fi
outfolder=$outpath/$foldername

# create the output folder
if [ ! -d $outfolder ]; then
  echo -e "\t Creating the output folder "$outfolder
  mkdir -p $outfolder;
fi
# create the user log
touch $outfolder/user_log.txt

# set the intermediate folder
arg_parse "-d" interfolder "$@"
if [ ! $interfolder ] ; then
  interfolder=$outfolder
fi

qsub -jsv /dls_sw/apps/sge/common/JSVs/tomo_recon_test.pl \
     -N $outname -j y -o $interfolder -e $interfolder -pe openmpi $M -l exclusive \
     -l infiniband -l gpu=4 -l gpu_arch=Kepler $filepath $savupath $datafile \
     $processfile $outpath $nCoresPerNode $nGPUs $options -c \
     -f $outfolder -s cs04r-sc-serv-14 -l $outfolder > /dls/tmp/savu/$USER.out


# get the job number here
filename=`echo $outname.o`
jobnumber=`awk '{print $3}' /dls/tmp/savu/$USER.out | head -n 1`

echo -e "\n\t************************************************************************"
tput setaf 6
echo -e "\n\t Your job has been submitted to the cluster with job number "$jobnumber"."
tput setaf 3
echo -e "\n\t\t* Monitor the status of your job on the cluster:"
tput sgr0
echo -e "\t\t   >> module load global/cluster"
echo -e "\t\t   >> qstat"
tput setaf 3
echo -e "\n\t\t* Monitor the progression of your Savu job:"
tput sgr0
echo -e "\t\t   >> tail -f $outfolder/user_log.txt"
echo -e "\t\t   >> Ctrl+C (to quit)"
tput setaf 6
echo -e "\n\t For a more detailed log file see: "
echo -e "\t   $interfolder/savu.o$jobnumber"
tput sgr0
echo -e "\n\t************************************************************************\n"

