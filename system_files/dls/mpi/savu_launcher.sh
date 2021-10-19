#!/bin/bash

all_args=$*
original_command="savu_mpi $all_args"

# function for checking which data centre
# assuming only gpfs03 in new data centre - to be updated
function is_gpfs03 ()
{
  file=$1
  return=$2
  check=$3
  pathtofile=`readlink -f $file`
  if [ "$check" = true ] && [ ! -f $pathtofile ] ; then
	if [ ! -d $pathtofile ]; then
		echo $file": No such file or directory"
		return 1
	fi
  fi

  gpfs03="$(df $pathtofile | grep gpfs03)"
  if [ ! "$gpfs03" ] ; then
	eval "$return"=false
  else
    eval "$return"=true
  fi
}

# input optional arguments
zocalo=false
keep=false
cpu=false
while getopts ":t:i:s:z:ck::" opt; do
	case ${opt} in
		t ) type=$OPTARG ;;
		i ) infile=$OPTARG ;;
		s ) version=$OPTARG ;;
        z ) zocalo=$OPTARG ;;
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
	module load savu
    version=default
else
	module load savu/$version
fi


# set output log/error file prefix
outname=savu

# If this is developer mode
if [ -n "${infile+set}" ]; then
	echo "Running Savu in developer mode"
    dev_mode=true
    type=STANDARD
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


	# check cluster and data path are compatible
	is_gpfs03 $data_file gpfs03 false
	if { [ "$gpfs03" = true ] && [ $cluster != 'hamilton' ] ; \
			} || { [ "$gpfs03" = false ] && [ $cluster == 'hamilton' ] ; }; then
		echo "The data is not visible on "$cluster
		exit 1
	fi


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

	# which project?
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

	# determine the cluster from the data path
    is_gpfs03 $data_file gpfs03 true # ***********************Error here for folders

	if [ "$gpfs03" = false ] ; then
		cluster=cluster
		# determine cluster setup based on type
		case $type in
			'AUTO') gpu_arch=Kepler ; nNodes=1 ;;
			'PREVIEW') gpu_arch=Kepler ; nNodes=1 ;;
			'BIG') gpu_arch=Pascal ; nNodes=8 ;;
			'') type="STANDARD"; gpu_arch=Kepler ; nNodes=4 ;;
			 *) echo -e "\nUnknown 'type' optional argument"
			    echo -e "Please choose from 'AUTO' or 'PREVIEW'"
				exit 1 ;;
		esac

	else
		cluster='hamilton'
		# determine cluster setup based on type

		case $project in
			"k11") gpu_arch='Volta' ;;
			*) gpu_arch='Pascal' ;;
		esac

		case $type in
			'AUTO') nNodes=1 ;;
			'PREVIEW') nNodes=1 ;;
			'BIG') nNodes=4 ;;
			'') type="STANDARD"; nNodes=2 ;;
			 *) echo -e "\nUnknown 'type' optional argument\n"
			    echo -e "Please choose from 'AUTO' or 'PREVIEW'" 
				exit 1 ;;
		esac
	fi

fi


# which cluster?
case $cluster in
	'test_cluster')
    	module load global/testcluster-quiet
		cluster_queue=test-medium.q ;;
  	'cluster')
		module load global/cluster-quiet
		cluster_queue=high.q
	    	# which gpu architecture?
		case $gpu_arch in
			'Fermi')
				cluster_queue=$cluster_queue@@com07
				cpus_per_node=12
				gpus_per_node=2 ;;
     		'Kepler')
				cluster_queue=$cluster_queue@@com10
				cpus_per_node=20
				gpus_per_node=4 ;;
     		'Pascal')
				cluster_queue=$cluster_queue@@com14
				cpus_per_node=20
				gpus_per_node=2 ;;
			*) echo -ne "\nERROR: Unknown GPU architecture for the cluster. "
			   echo -e "Please choose from 'Fermi', 'Kepler' or 'Pascal'\n"
  			   exit 1 ;;
		esac ;;
	'hamilton')
		module load hamilton-quiet
		cluster_queue=all.q
		cpus_per_node=40
		if [ $dev_mode==false ]; then
			cpus_to_use_per_node=30
		fi
		gpus_per_node=4

    	# which gpu architecture?
		if [ -z $gpu_arch ] ; then
			case $project in
				"k11") gpu_arch='Volta' ;;
				*) gpu_arch='Pascal' ;;
			esac
		elif [ $gpu_arch != 'Pascal' ] && [ $gpu_arch != 'Volta' ] ; then
			echo -ne "\nERROR: Unknown GPU architecture for Hamilton. "
			echo -e "Please choose from 'Pascal' or 'Volta'\n"
			exit 1
		fi ;;
	*)	echo "Unknown cluster, please choose from 'test_cluster', 'cluster' or 'hamilton'"
		exit 1 ;;
esac

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
processes=$((nNodes*cpus_per_node))

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
    if [ ! $type == 'AUTO' ] && [ ! $type == 'PREVIEW' ] && [ ! $keep == true ] ; then
		delete=$interfolder
	fi
fi

# check all files are in the same data centre
is_gpfs03 $data_file is_gpfs03_in false
is_gpfs03 $interfolder is_gpfs03_inter false
is_gpfs03 $outfolder is_gpfs03_out false
if ! ([ $is_gpfs03_in = $is_gpfs03_inter ] && [ $is_gpfs03_inter = $is_gpfs03_out ]) ; then
tput setaf 3
	echo -e "\n\t**************************** ERROR MESSAGE ****************************"
tput setaf 1
#tput sgr0
	echo -e "\tAll the input and output data locations must be in the same data centre."
	echo -e "\tPlease email scientific.software@diamond.ac.uk for more information."

tput setaf 3
	echo -e "\t***********************************************************************\n"
tput sgr0
	exit 1
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
# replace the original process list path with the process list resaved into the log file
modified_command=${original_command/$orig_process_file/$log_process_file}

# =========================== qsub =======================================
# general arguments
# openmpi-savu stops greater than requested number of nodes being assigned to the job if memory
# requirements are not satisfied.'

qsub_args="-N $outname -j y -o $interfolder -e $interfolder -pe openmpi-savu $processes -l exclusive \
-q $cluster_queue -P $project"

# blocking
if [ $zocalo == true ] ; then
	qsub_args="${qsub_args} -sync y"
fi

# gpu processing
if [ $cpu == false ] ; then
	#qsub_args="${qsub_args} -l gpu=$gpus_per_node -l gpu_arch=$gpu_arch"
	qsub_args="${qsub_args} -l gpu=$gpus_per_node -l gpu_arch=$gpu_arch"
fi

# savu_mpijob.sh args
mpijob_args="$filepath $version $savupath $data_file $process_file $outpath $cpus_to_use_per_node \
$gpus_to_use_per_node $delete"

# savu args
savu_args="$options -c -f $outfolder -s graylog2.diamond.ac.uk -p 12203 \
--facility_email scientificsoftware@diamond.ac.uk -l $outfolder"

args="${qsub_args} ${mpijob_args} ${savu_args}"

case $cluster in
	"test_cluster")
		sbmt_cmd="qsub -l infiniband $args" ;;
	"cluster")
		# RAM com10 252G com14 252G ~ 12G per core  - m_mem_free requested in JSV script
		sbmt_cmd="qsub -jsv /dls_sw/cluster/common/JSVs/savu_20191122.pl -l infiniband $args" ;;
	"hamilton")
		# RAM 384G per core (but 377G available?) ~ 9G per core
		# requesting 7G per core as minimum (required to be available on startup),but will use all
		# memory unless system jobs need it (then could be rolled back to the minimum 7G)
		sbmt_cmd="qsub -l m_mem_free=7G $args" ;;
esac

$sbmt_cmd > /dls/tmp/savu/$USER.out

# =========================== end qsub ===================================

# copy original command to the log folder
command_file="$logfolder/run_command.txt"

cat > $command_file <<ENDFILE
# The original savu_mpi command used is the following (note that the -s savu_version flag defines the Savu environment)
$original_command
# Please use the command below to reproduce the obtained results exactly. The -s savu_version flag will set the correct Savu environment for you automatically
$modified_command
# The qsub run command is the following:
$sbmt_cmd
ENDFILE

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

if [ $cluster == 'hamilton' ] ; then
  echo -e "\t\t   >> module load hamilton"
else
  echo -e "\t\t   >> module load global/cluster"
fi

echo -e "\t\t   >> qstat"
tput setaf 3
echo -e "\n\t\t* Monitor the progression of your Savu job:"
tput sgr0
echo -e "\t\t   >> tail -f $logfolder/user.log"
echo -e "\t\t   >> Ctrl+C (to quit)"
tput setaf 6
echo -e "\n\t For a more detailed log file see: "
echo -e "\t   $interfolder/savu.o$jobnumber"
tput sgr0
echo -e "\n\t************************************************************************\n"

