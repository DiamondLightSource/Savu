#!/bin/bash

count=0
while read -r entry; do
	if [ ! -z "$entry" ]; then
        var[count]=${entry#*=}
        count=$(( $count + 1 ))
    fi
done < $1

version=${var[0]}
echo "module loading savu/"$version
module load savu/$version
module load global/cluster

cluster=high.q@@${var[1]}
gpu_arch=${var[2]}
nodes=${var[3]}
cpus_per_node=${var[4]}
gpus_per_node=${var[5]}
cpus_to_use_per_node=${var[6]}
gpus_to_use_per_node=${var[7]}
input_file=${var[8]}
process_file=${var[9]}
output_folder=${var[10]}
options=${var[11]}
outname=savu
processes=$((nodes*cpus_per_node))

echo -e "\n*******************************************************************************"
echo "Running job on $cluster with $nodes nodes, $cpus_to_use_per_node cpus per node, $gpus_to_use_per_node gpus per node".
echo "Input file: $input_file"
echo "Process list: $process_file"
echo -e "*******************************************************************************\n"


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


# get the Savu path
DIR="$(cd "$(dirname "$0")" && pwd)"
filepath=`command -v savu_mpijob.sh`
savupath=$(python -c "import savu, os; print savu.__path__[0]")
savupath=${savupath%/savu}


# set the output folder
arg_parse "-f" foldername "$@"
if [ ! $foldername ] ; then
  IFS=. read path ext <<<"${input_file##*-}"
  foldername=$(date +%Y%m%d%H%M%S)"_$(basename $path)"
fi
outfolder=$output_folder/$foldername

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
fi

echo $savupath

# gpu_arch = Fermi (com07), Kepler (com10), Pascal (com14)
qsub -N $outname -j y -o $interfolder -e $interfolder -pe openmpi $processes -l exclusive \
     -l infiniband -l gpu=$gpus_per_node -l gpu_arch=$gpu_arch -q $cluster -P tomography \
     $filepath $version $savupath $input_file $process_file $output_folder \
     $cpus_to_use_per_node $gpus_to_use_per_node $options -c \
     -f $outfolder -s cs04r-sc-serv-14 -l $outfolder > /dls/tmp/savu/$USER.out

# get the job number here
filename=`echo $outname.o`
jobnumber=`awk '{print $3}' /dls/tmp/savu/$USER.out | head -n 1`

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

