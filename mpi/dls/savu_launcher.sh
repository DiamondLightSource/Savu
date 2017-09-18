#!/bin/bash

version=$1
module load savu/$version
module load global/cluster-quiet
shift 1

PREVIEW=false
BIG=false
echo "LAUNCHING THE SCRIPT"
if [ $1 == 'PREVIEW' ] ; then
    PREVIEW=true
    shift 1
elif [ $1 == 'BIG' ] ; then
    BIG=true
    shift 1
fi

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

if [[ $@ == '--help' ]] ; then
    echo -e "\n\t************************* SAVU HELP MESSAGE ****************************"
    tput setaf 6
    echo -e "\n\t To submit a Savu parallel job to the cluster, please follow the "
    echo -e "\t template below:"
    tput sgr0
    echo -e "\n\t >>> savu_mpi  <in_file>  <process_list>  <out_folder>  <optional_args>"
    tput setaf 6
    echo -e "\n\t For a list of optional arguments type:"
    tput sgr0
    echo -e "\t >>> savu --help"
    tput setaf 6
    echo -e "\n\t It is recommended that you pass the optional arg '-d <temp_dir>', "
    echo -e "\t where temp_dir is the temporary directory for your visit, if you are "
    echo -e "\t running Savu on a full dataset. Ask your local contact for help."
    tput sgr0
    echo -e "\n\t\t\t *** THANK YOU FOR USING SAVU! ***"
    echo -e "\n\t************************************************************************\n"
    tput sgr0
    exit    
fi

# Check required arguments exist
vars=$@
x="${vars%%' -'*}"
[[ $x = $vars ]] && temp=${#vars} || temp=${#x}
args=(${vars:0:$temp})
nargs=${#args[@]}

if [ $nargs != 3 ] ; then
    tput setaf 1    
    echo -e "\n\t************************* SAVU INPUT ERROR ******************************"
    tput setaf 6
    echo -e "\n\t You have entered an incorrect number of input arguments.  Please follow"
    echo -e "\t the template below:"
    tput sgr0
    echo -e "\n\t >>> savu_mpi  <in_file>  <process_list>  <out_folder>  <optional_args>"
    tput setaf 6
    echo -e "\n\t For a list of optional arguments type:"
    tput sgr0
    echo -e "\t >>> savu --help"
#    tput setaf 6
    echo -e "\n\t\t\t *** THANK YOU FOR USING SAVU! ***"
    tput setaf 1
    echo -e "\n\t*************************************************************************\n"
    tput sgr0
    exit
fi

# set parameters
datafile=$1
processfile=$2
outpath=$3
shift 3
options=$@

if [ $BIG = true ] ; then
    echo "RUNNING BIG DATA RECONSTRUCTION"
    cluster=high.q@@com14
    gpu_arch=Pascal
    outname=savu
    nNodes=8
    nCoresPerNode=20
    nGPUs=2
elif [ $PREVIEW = true ] ; then
    cluster=high.q@@com07
    gpu_arch=Fermi
    outname=savu
    nNodes=1
    nCoresPerNode=12
    nGPUs=2
else
    cluster=high.q@@com10
    gpu_arch=Kepler
    outname=savu
    nNodes=4
    nCoresPerNode=20
    nGPUs=4
fi

# get the Savu path
DIR="$(cd "$(dirname "$0")" && pwd)"
filepath=$DIR'/savu_mpijob.sh'
savupath=$(python -c "import savu, os; print savu.__path__[0]")
savupath=${savupath%/savu}

echo -e "\t The Savu path is:" $savupath

M=$((nNodes*nCoresPerNode))

basename=`basename $datafile`
# set the output folder
arg_parse "-f" foldername "$@"
if [ ! $foldername ] ; then
  IFS=. read path ext <<<"${basename##*-}"
  foldername=$(date +%Y%m%d%H%M%S)"_$(basename $path)"
fi
outfolder=$outpath/$foldername

# create the output folder
if [ ! -d $outfolder ]; then
  echo -e "\t Creating the output folder "$outfolder
  mkdir -p $outfolder;
fi
# create the user log
touch $outfolder/user.log

# set the intermediate folder
arg_parse "-d" interfolder "$@"
if [ ! $interfolder ] ; then
  interfolder=$outfolder
else
  interfolder=$interfolder/$foldername
  if [ ! -d $interfolder ]; then
    echo -e "\t Creating the output folder "$interfolder
    mkdir -p $interfolder;
  fi
fi

qsub -jsv /dls_sw/apps/sge/common/JSVs/savu.pl \
     -N $outname -j y -o $interfolder -e $interfolder -pe openmpi $M -l exclusive \
     -l infiniband -l gpu=$nGPUs -l gpu_arch=$gpu_arch -q $cluster $filepath $version $savupath $datafile \
     $processfile $outpath $nCoresPerNode $nGPUs $options -c -f $outfolder -s cs04r-sc-serv-14 \
     --facility_email scientificsoftware@diamond.ac.uk -l $outfolder > /dls/tmp/savu/$USER.out

#qsub -N $outname -j y -o $interfolder -e $interfolder -pe openmpi $M -l exclusive \
#     -l infiniband -l gpu=$nGPUs -l gpu_arch=$gpu_arch -q $cluster -P tomography $filepath $version $savupath $datafile \
#     $processfile $outpath $nCoresPerNode $nGPUs $options -c \
#     -f $outfolder -s cs04r-sc-serv-14 -l $outfolder > /dls/tmp/savu/$USER.out

# get the job number here
filename=`echo $outname.o`
jobnumber=`awk '{print $3}' /dls/tmp/savu/$USER.out | head -n 1`

interpath=`readlink -f $interfolder`
ln -s $interpath/savu.o$jobnumber /dls/tmp/savu/savu.o$jobnumber

echo -e "\n\t************************************************************************"
echo -e "\n\t\t\t *** THANK YOU FOR USING SAVU! ***"
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
echo -e "\t\t   >> tail -f $outfolder/user.log"
echo -e "\t\t   >> Ctrl+C (to quit)"
tput setaf 6
echo -e "\n\t For a more detailed log file see: "
echo -e "\t   $interfolder/savu.o$jobnumber"
tput sgr0
echo -e "\n\t************************************************************************\n"

