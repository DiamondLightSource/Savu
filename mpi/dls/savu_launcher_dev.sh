#!/bin/bash

count=0
while read -r entry; do

	if [ ! -z "$entry" ]; then

        var[count]=${entry#*=}
        echo ${var[count]}
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

DIR="$(cd "$(dirname "$0")" && pwd)"
file_path=$DIR'/savu_mpijob.sh'
savu_path=$(python -c "import savu, os; print os.path.dirname(os.path.abspath(savu.__file__))")

savu_path=${savu_path%/savu}

M=$((nNodes*nCoresPerNode))

log_path=/dls/tmp/savu
while [[ $options -gt 1 ]]
do
if [ $1 == "-l" ]
  then
  log_path=$2
fi
shift
done

echo "The log path is"$log_path


