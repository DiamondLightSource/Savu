#!/bin/bash

all_args=$*
original_command="savu_mpi $all_args"

# input optional arguments
keep=false
cpu=false
while getopts ":t:i:s:z:ck::" opt; do
	case ${opt} in
		t ) GPUarch_nodes=$OPTARG ;;
		i ) infile=$OPTARG ;;
		s ) version=$OPTARG ;;
		c ) cpu=true ;;
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

# If this is developer mode
if [ -n "${infile+set}" ]; then
	echo "Running Savu in developer mode"
    dev_mode=true
    GPUarch_nodes=STANDARD
  	# read the values from file (ignoring lines starting with #)
	count=0
	while read -r entry; do
		if [ ! -z "$entry" ] && [[ ! $entry = \#* ]] ; then
		    var[count]=${entry#*=}
		    count=$(( $count + 1 ))
    	fi
  	done < $infile

	cluster=${var[0],,}
	gpu_arch=${var[1],,}
	gpu_arch=${gpu_arch^}
	nNodes=${var[2]}
	cpus_to_use_per_node=${var[3]}
	gpus_to_use_per_node=${var[4]}
	data_file=${var[5]}
	process_file=${var[6]}
	outpath=${var[7]}
	options=${var[8]}
	project=tomography
else
	#echo "Running Savu in production mode"
	# parse additional command line arguments
	# Check required arguments exist
    dev_mode=false
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

	# TODO: For Grid Engine, the code below sets the project based on the
	# filepath of the input data. For SLURM, does setting the "account" in the
	# same way make sense, or is there a more reliable way of doing it?
	pathtodatafile=`readlink -f $data_file`
	if [[ $pathtodatafile == /dls/staging* ]] ; then
		pathtodatafile=${pathtodatafile#/dls/staging}
	fi
	project=`echo $pathtodatafile | grep -o -P '(?<=/dls/).*?(?=/data)'`
	# in the case there is more than once instance of the pattern above
	project=`echo $project | head -n1 | awk '{print $1;}'`
	if [ -z "$project" ] ; then
	  project=tomography
	fi

	# TODO: The only "account" currently available on Wilson is "test05r", so
	# will hardcode that for now
	account=test05r

	# No longer choose number of GPU nodes and GPU architecture based on if the
	# data is on GPFS03 or not, let SLURM config handle this instead.

	# If the number of GPU nodes and GPU architecture is not provided, then
	# default to 2 GPU nodes with Pascal's
	if [[ -z "${GPUarch_nodes}" ]]; then
		GPUarch_nodes="STANDARD"
		arch='Pascal'
		num=2
	else
		arch=${GPUarch_nodes%_*}
		num=${GPUarch_nodes##*_}
	fi
	nNodes=$num

	# Set number of CPUs and GPUs to request
	case $arch in
		'Pascal')
			gpu_arch=Pascal
			cpus_per_node=20
			gpus_per_node=2
			;;
		'Volta')
			gpu_arch=Volta
			cpus_per_node=40
			if [ $dev_mode==false ]; then
				cpus_to_use_per_node=30
			fi
			gpus_per_node=4
			;;
		*)
			echo -e "\nUnknown 'GPUarch_nodes' optional argument"
			echo -e "Please use the following syntax '<GPU_architecture>_<number_of_nodes>'. Example: 'Kepler_2', 'Pascal_2'"
			exit 1
			;;
	esac

	# Previously there was a special case for K11/DIAD for when input data was
	# on GPFS03, to default to using Volta's. For the migration to SLURM (where
	# being aware of GPFS03 in the launcher script is no longer necessary),
	# this has been translated into requesting Volta's for K11/DIAD data.
	if [ $project == k11 ]; then
		gpu_arch=Volta
	fi

	# Set "partition" (the SLURM equivalent of a "queue" in Grid Engine)
	# TODO: Currently on Wilson, cs05r is the only partition which reports
	# having GPU nodes, so have naively chosen this for all jobs, but this may
	# not be correct.
	partition=cs05r
fi

# override cpu and gpu values if the full node is not required
if [ -z $cpus_to_use_per_node ] ; then cpus_to_use_per_node=$cpus_per_node; fi
if [ -z $gpus_to_use_per_node ] ; then gpus_to_use_per_node=$gpus_per_node; fi

if [ $cpus_to_use_per_node -gt $cpus_per_node ] ; then
	echo "The number of CPUs requested per node ($cpus_to_use_per_node) is greater than the maximum ($cpus_per_node)."
	exit 1
fi
if [ $gpus_to_use_per_node -gt $gpus_per_node ] ; then
	echo "The number of GPUs requested per node ($gpus_to_use_per_node) is greater than the maximum ($gpus_per_node)."
	exit 1
fi


# set total processes required
processes=$cpus_per_node

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

# copy process list to the intermediate folder
orig_process_file=$process_file
process_file=`readlink -f $process_file`
basename=`basename $process_file`
cp $process_file $interfolder
process_file=$interfolder/$basename

if [ -n "${infile+set}" ]; then
    # copy infile to the intermediate folder
    orig_in_file=$infile
    infile=`readlink -f $infile`
    basename=`basename $infile`
    cp $infile $interfolder
    infile=$interfolder/$basename
fi

# create a modified command with the new process list path
log_process_file=$logfolder/$basename
# replace the original process list path with the process list resaved into the
# log file
modified_command=${original_command/$orig_process_file/$log_process_file}

# =========================== sbatch =======================================
# general arguments

# openmpi-savu stops greater than requested number of nodes being assigned to
# the job if memory requirements are not satisfied.'
#qsub_args="-N $outname -j y -o $interfolder -e $interfolder -pe openmpi-savu $processes -l exclusive \
#-q $cluster_queue -P $project"
# TODO: How is the "parallel environment" openmpi-savu from Grid Engine
# translated to SLURM?
out_file_base="$interfolder/$outname.o"
out_file_slurm_jobid="$out_file_base%j"
sbatch_args="--job-name=$outname --output $out_file_slurm_jobid --exclusive \
--partition $partition --account=$account --nodes $nNodes \
--ntasks-per-node $processes"

# gpu processing
if [ $cpu == false ] ; then
	#qsub_args="${qsub_args} -l gpu=$gpus_per_node -l gpu_arch=$gpu_arch"
	# TODO: Is this the correct way to use the `--constraint` flag to select
	# the GPU architecture?
	#sbatch_args="$sbatch_args --gpus-per-node=$gpus_per_node --constraint=$gpu_arch"
	sbatch_args="$sbatch_args --gpus-per-node=$gpus_per_node"
fi

# savu_mpijob.sh args
mpijob_args="$filepath $version $savupath $data_file $process_file $outpath \
$cpus_to_use_per_node $gpus_to_use_per_node $delete"

# savu args
savu_args="$options -c -f $outfolder -s graylog2.diamond.ac.uk -p 12203 \
--facility_email scientificsoftware@diamond.ac.uk -l $outfolder"

#args="${qsub_args} ${mpijob_args} ${savu_args}"
args="${sbatch_args} ${mpijob_args} ${savu_args}"

# TODO: Not sure how to request certain things based on the cluster that the
# job will get scheduled on (for example, below has parts that some require
# infiniband, and different amounts of free RAM per CPU core)
#
# Also note that there's a perl script for the science cluster case which is
# apparently requesting 12GB of RAM per CPU core to be free, not sure how to
# migrate this to SLURM either.
#case $cluster in
#	"test_cluster")
#		sbmt_cmd="qsub -l infiniband $args" ;;
#	"cluster")
#		# RAM com10 252G com14 252G ~ 12G per core  - m_mem_free requested in JSV script
#		sbmt_cmd="qsub -jsv /dls_sw/cluster/common/JSVs/savu_20191122.pl -l infiniband $args" ;;
#	"hamilton")
#		# RAM 384G per core (but 377G available?) ~ 9G per core
#		# requesting 7G per core as minimum (required to be available on startup),but will use all
#		# memory unless system jobs need it (then could be rolled back to the minimum 7G)
#		sbmt_cmd="qsub -l m_mem_free=7G $args" ;;
#esac

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
$sbmt_cmd
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
echo -e "\t The computing configuration has been passed as $GPUarch_nodes with $arch GPU and $num node(s)."
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
