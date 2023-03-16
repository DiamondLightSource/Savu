#!/bin/bash

all_args=$*
original_command="savu_mpi $all_args"

# input optional arguments
keep=false
while getopts ":t:i:s:z:ck::" opt; do
	case ${opt} in
		s ) version=$OPTARG ;;
        k ) keep=$OPTARG ;;
		\? ) echo "Invalid option: $OPTARG" 1>&2 ;;
		: ) echo "Invalid option: $OPTARG requires an argument" 1>&2 ;;
	esac
done
shift $((OPTIND -1))

# check the Savu version flag has been passed
if [ -z $version ] ; then
	echo -ne "\n*** Loading the latest stable version of Savu as "
	echo -e "a specific version has not been requested ***\n"
	# TODO: Hardcoded `savu/5.0-tomo` as this uses `openmpi/4.1.2` which is
	# compatible with SLURM
	module load savu/5.0-tomo
	version="5.0-tomo"
else
	module load savu/$version
fi

# set output log/error file prefix
outname=savu

# parse additional command line arguments
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
data_file=$1
process_file=$2
outpath=$3
shift 3
options=$@

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

# function to create folders and exit on error
function create_folder()
{
  folder=$1
  mkdir -p $folder
  if [ $? -ne 0 ] ; then
    exit 1
  fi
}

# get the Savu path
DIR="$(cd "$(dirname "$0")" && pwd)"
filepath=$DIR'/savu_mpijob.sh'
savupath=$(python -c "import savu, os; print (savu.__path__[0])")
savupath=${savupath%/savu}

# set the suffix
arg_parse "-suffix" suffix $options
options=${options//"-suffix $suffix"/}
if [ ! $suffix ] ; then
  suffix=""
else
  suffix=_$suffix
fi

# Set output and intermediate file paths
basename=`basename $data_file`
# set the output folder
arg_parse "-f" foldername $options
if [ ! $foldername ] ; then
  IFS=. read path ext <<<"${basename##*-}"
  foldername=$(date +%Y%m%d%H%M%S)"_$(basename $path)"$suffix
fi
outfolder=$outpath/$foldername
logfolder="$outpath/$foldername/run_log"

# create the output folder
if [ ! -d $outfolder ]; then
  #echo -e "\t Creating the output folder "$outfolder
  create_folder $outfolder
fi

# create the log folder
if [ ! -d $logfolder ]; then
  create_folder $logfolder
fi

# create the user log
userlogfile="$logfolder/user.log"
touch $userlogfile

# set the intermediate folder
arg_parse "-d" interfolder $options
delete=false
if [ ! $interfolder ] ; then
	arg_parse "--tmp" interfolder $options
fi

if [ ! $interfolder ] ; then
	interfolder=$logfolder
else
	interfolder=$interfolder/$foldername
	if [ ! -d $interfolder ]; then
		create_folder $interfolder
	fi
    if [ ! $keep == true ] ; then
		delete=$interfolder
	fi
fi

# When Savu runs, it will copy the process list file from its original location
# to the log folder; create a modified command with the path to the copy of the
# process list file that will exist once Savu has begun running, and put it into
# a log file
basename=`basename $process_file`
log_process_file=$logfolder/$basename
modified_command=${original_command/$process_file/$log_process_file}

# =========================== sbatch =======================================

# `sbatch` args
out_file_base="$interfolder/$outname.o"
out_file_slurm_jobid="$out_file_base%j"
sbatch_args="--output $out_file_slurm_jobid"

# savu_mpijob.sh args
# Use the original process list file for the Savu run, but use the copy of the
# process list file for generating the command that goes into a log file that
# will reproduce the run
mpijob_args="$filepath $version $savupath $data_file $process_file $outpath \
$delete"
mpijob_args_log_process_file="$filepath $version $savupath $data_file \
$log_process_file $outpath $delete"

# savu args
savu_args="$options -c -f $outfolder -s graylog2.diamond.ac.uk -p 12203 \
--facility_email scientificsoftware@diamond.ac.uk -l $outfolder"

# Collect all args for `sbatch` command
args="${sbatch_args} ${mpijob_args} ${savu_args}"
sbmt_cmd="sbatch $args"
# Save the output text of the job submission in a variable to get the job ID
# later
job_output_str=$($sbmt_cmd)

# =========================== end sbatch ===================================

# copy original command to the log folder
command_file="$logfolder/run_command.txt"

cat > $command_file <<ENDFILE
# The script location
$(dirname $0)
# The directory the script was executed from
$PWD
# The original savu_mpi command used is the following (note that the -s savu_version flag defines the Savu environment)
$original_command
# Please use the command below to reproduce the obtained results exactly. The -s savu_version flag will set the correct Savu environment for you automatically
$modified_command
# The sbatch run command is the following:
sbatch $sbatch_args $mpijob_args_log_process_file $savu_args
ENDFILE

# get the job number here
# The output text of the job submission is the string "Submitted batch job
# <JOBID>", where <JOBID> is the job ID consisting of an unknown number of
# integers, so can find the ID with a regex
regex="Submitted\ batch\ job\ ([0-9]*)$"
[[ $job_output_str =~ $regex ]]
jobnumber=${BASH_REMATCH[1]}
out_file="$out_file_base$jobnumber"

ln -s $out_file /dls/tmp/savu/$outname.o$jobnumber

echo -e "\n\t************************************************************************"
echo -e "\n\t\t\t *** THANK YOU FOR USING SAVU! ***"
tput setaf 6
echo -e "\n\t Your job has been submitted to the cluster with job number $jobnumber."
tput setaf 3
echo -e "\n\t\t* Monitor the status of your job on the cluster:"
tput sgr0
echo -e "\t\t   >> sstat $jobnumber"
tput setaf 3
echo -e "\n\t\t* Monitor the progression of your Savu job:"
tput sgr0
echo -e "\t\t   >> tail -f $logfolder/user.log"
echo -e "\t\t   >> Ctrl+C (to quit)"
tput setaf 6
echo -e "\n\t For a more detailed log file see: "
echo -e "\t   $out_file"
tput sgr0
echo -e "\n\t************************************************************************\n"
