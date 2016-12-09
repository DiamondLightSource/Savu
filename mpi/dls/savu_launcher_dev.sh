#!/bin/bash
module load savu/1.2

count=0
while read -r entry; do
	if [ ! -z "$entry" ]; then
        var[count]=${entry#*=}
        count=$(( $count + 1 ))
    fi
done < $1
   
cluster=medium.q@@${var[0]}
nodes=${var[1]}
cpus_per_node=${var[2]}
gpus_per_node=${var[3]}
input_file=${var[4]}
process_file=${var[5]}
output_folder=${var[6]}
options=${var[7]}
outname=savu
processes=$((nodes*cpus_per_node))

echo -e "\n*******************************************************************************"
echo "Running job on $cluster with $nodes nodes, $cpus_per_node cpus per node, $gpus_per_node gpus per node".
echo "Input file: $input_file"
echo "Process list: $process_file"
echo -e "*******************************************************************************\n"

DIR="$(cd "$(dirname "$0")" && pwd)"
file_path=$DIR'/savu_mpijob.sh'
savu_path=$(python -c "import savu, os; print os.path.dirname(os.path.abspath(savu.__file__))")
savu_path=${savu_path%/savu}

# set the log path
log_path=/dls/tmp/savu
a=( $options )
for (( i=0; i<${#a[@]} ; i+=2 )) ; do
    if [ ${a[i]} == "-l" ]; then
        log_path=${a[i+1]}
    fi
done

qsub -N $outname -sync y -j y -o $log_path -e $log_path -pe openmpi $processes \
     -l exclusive -l infiniband -l gpu=1 -q $cluster $file_path $savu_path \
     $input_file $process_file $output_folder $cpus_per_node $gpus_per_node $options -s cs04r-sc-serv-14 > /dls/tmp/savu/$USER.out

echo "SAVU_LAUNCHER:: Job Complete, preparing output..."

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

