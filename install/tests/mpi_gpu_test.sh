#!/bin/bash

output=$1
if ! [ "$output" ]; then
    echo "Please pass the path to the output folder."
    exit 1
fi

# get the loaded module version of savu
IN=$LOADEDMODULES
while IFS=':' read -ra ADDR; do
    for i in "${ADDR[@]}"; do
        if [[ $i == *"savu"* ]]; then
            version=`echo "$i" | awk -F/ '{print $NF}'`
        fi
    done
done <<< "$IN"

# set the TESTDATA environment variable
. test_setup.sh

echo "Running the mpi gpu test..."
savu_launcher.sh $version $TESTDATA/data/tomo_standard.nxs $TESTDATA/test_process_lists/mpi_gpu_test.nxs $output

