#!/bin/bash

output=$1
if ! [ "$output" ]; then
    echo "Please pass the path to the output folder."
    exit 1
fi

# set the TESTDATA environment variable
savu_setup.sh

echo "Running the mpi gpu test..."
savu_launcher.sh $TESTDATA/data/24737.nxs $TESTDATA/test_process_lists/mpi_gpu_test.nxs $output

