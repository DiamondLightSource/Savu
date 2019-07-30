#!/bin/bash

# input optional arguments
while getopts ":t:i:s::" opt; do
	case ${opt} in
		t ) type=$OPTARG ;;
		i ) infile=$OPTARG ;;
		s ) version=$OPTARG ;;
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
else
	module load savu/$version
fi


# set output log/error file prefix
outname=savu

# If this is developer mode
if [ -n "${infile+set}" ]; then
	echo "Running Savu in developer mode"
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
	nNodes=${var[2]}
	cpus_to_use_per_node=${var[3]}
	gpus_to_use_per_node=${var[4]}
	data_file=${var[5]}
	process_file=${var[6]}
	outpath=${var[7]}
	options=${var[8]}
	project=tomography


	# check cluster and data path are compatible
	pathtodatafile=`readlink -f $data_file`
	gpfs03="$(df $pathtodatafile | grep gpfs03)"
	if { [ ! -z "$gpfs03" ] && [ $cluster != 'hamilton' ] ; \
			} || { [ -z "$gpfs03" ] && [ $cluster == 'hamilton' ] ; }; then
		echo "The data is not visible on "$cluster "in the final"
		exit 1
	fi


else
	#echo "Running Savu in production mode"
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

	# determine the cluster from the data path
	pathtodatafile=`readlink -f $data_file`
	if [ -z $pathtodatafile ] ; then
		echo $data_file": No such file or directory"
		exit 1
	fi

	gpfs03="$(df $pathtodatafile | grep gpfs03)"
	if [ -z "$gpfs03" ] ; then
		cluster=cluster
		# determine cluster setup based on type
		case $type in
			'AUTO') gpu_arch=fermi ; nNodes=1 ;;
			'PREVIEW') gpu_arch=fermi ; nNodes=1 ;;
			'BIG') gpu_arch=pascal ; nNodes=8 ;;
			'') gpu_arch=kepler ; nNodes=4 ;;
			 *) echo -e "\nUnknown 'type' optional argument"
			    echo -e "Please choose from 'AUTO' or 'PREVIEW'"
				exit 1 ;;
		esac

	else
		cluster='hamilton'
		# determine cluster setup based on type
		gpu_arch=pascal
		case $type in
			'AUTO') nNodes=1 ;;
			'PREVIEW') nNodes=1 ;;
			'BIG') nNodes=4 ;;
			'') nNodes=2 ;;
			 *) echo -e "\nUnknown 'type' optional argument\n"
			    echo -e "Please choose from 'AUTO' or 'PREVIEW'" 
				exit 1 ;;
		esac
	fi

	# which project?
	project=`echo $pathtodatafile | grep -o -P '(?<=/dls/).*(?=/data)'`
	if [ -z "$project" ] ; then
	  project=tomography
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
			'fermi')
				cluster_queue=$cluster@@com07
				cpus_per_node=12
				gpus_per_node=2 ;;
     		'kepler')
				cluster_queue=$cluster@@com10
				cpus_per_node=20
				gpus_per_node=4 ;;
     		'pascal')
				cluster_queue=$cluster@@com14
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
		gpus_per_node=4

    	# which gpu architecture?
		if [ -z $gpu_arch ] ; then
			gpu_arch='pascal'
		elif [ $gpu_arch != 'pascal' ] && [ $gpu_arch != 'volta' ] ; then
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
savupath=$(python -c "import savu, os; print savu.__path__[0]")
savupath=${savupath%/savu}

# Set output and intermediate file paths
basename=`basename $data_file`
# set the output folder
arg_parse "-f" foldername $options
if [ ! $foldername ] ; then
  IFS=. read path ext <<<"${basename##*-}"
  foldername=$(date +%Y%m%d%H%M%S)"_$(basename $path)"
fi
outfolder=$outpath/$foldername

# create the output folder
if [ ! -d $outfolder ]; then
  #echo -e "\t Creating the output folder "$outfolder
  create_folder $outfolder
fi
# create the user log
touch $outfolder/user.log

# set the intermediate folder
arg_parse "-d" interfolder $options
delete=false
if [ ! $interfolder ] ; then
	arg_parse "--tmp" interfolder $options
fi

if [ ! $interfolder ] ; then
	interfolder=$outfolder
else
	interfolder=$interfolder/$foldername
	if [ ! -d $interfolder ]; then
		echo -e "\t Creating the output folder "$interfolder
		create_folder $interfolder
	fi
	if [ ! $type == 'AUTO' ] && [ ! $type == 'PREVIEW' ] ; then
		delete=$interfolder
	fi
fi

# copy process list to the intermediate folder
process_file=`readlink -f $process_file`
basename=`basename $process_file`
cp $process_file $interfolder
process_file=$interfolder/$basename

case $cluster in
	"test_cluster")
		qsub -N $outname -j y -o $interfolder -e $interfolder -pe openmpi $processes -l exclusive \
		-l infiniband -l gpu=$gpus_per_node -l gpu_arch=$gpu_arch -q $cluster_queue -P $project \
		$filepath $version $savupath $data_file $process_file $outpath $cpus_to_use_per_node \
		$gpus_to_use_per_node $delete $options -c -f $outfolder -s graylog2.diamond.ac.uk -p 12203 \
		--facility_email scientificsoftware@diamond.ac.uk -l $outfolder > /dls/tmp/savu/$USER.out ;;
	"cluster")
	  	qsub -jsv /dls_sw/apps/sge/common/JSVs/savu.pl \
		-N $outname -j y -o $interfolder -e $interfolder -pe openmpi $processes -l exclusive \
		-l infiniband -l gpu=$gpus_per_node -l gpu_arch=$gpu_arch -q $cluster_queue -P $project \
		$filepath $version $savupath $data_file $process_file $outpath $cpus_to_use_per_node \
		$gpus_to_use_per_node $delete $options -c -f $foldername -s graylog2.diamond.ac.uk -p 12203 \
		--facility_email scientificsoftware@diamond.ac.uk -l $outfolder > /dls/tmp/savu/$USER.out ;;
	"hamilton")
		qsub -N $outname -j y -o $interfolder -e $interfolder -pe openmpi $processes -l exclusive \
		-l gpu=$gpus_per_node -l gpu_arch=$gpu_arch -q $cluster_queue -P $project $filepath $version \
		$savupath $data_file $process_file $outpath $cpus_to_use_per_node $gpus_to_use_per_node \
		$delete $options -c -f $foldername -s graylog2.diamond.ac.uk -p 12203 \
		--facility_email scientificsoftware@diamond.ac.uk -l $outfolder > /dls/tmp/savu/$USER.out ;;
esac	

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
echo -e "\t\t   >> tail -f $outfolder/user.log"
echo -e "\t\t   >> Ctrl+C (to quit)"
tput setaf 6
echo -e "\n\t For a more detailed log file see: "
echo -e "\t   $interfolder/savu.o$jobnumber"
tput sgr0
echo -e "\n\t************************************************************************\n"

