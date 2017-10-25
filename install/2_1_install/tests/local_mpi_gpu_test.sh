#!/bin/bash

# function for parsing optional arguments
function arg_parse ()
{
  flag=$1
  return=$2
  while [[ $# -gt 1 ]] ; do
    if [ $1 == $flag ] ; then
      eval "$return"=$2
    fi
    shift
  done
}

output=$1
if ! [ "$output" ]; then
    echo "Please pass the path to the output folder."
    exit 1
fi

# set the TESTDATA environment variable
. test_setup.sh

echo "Running the mpi gpu test..."


arg_parse "-r" redirect "$@"
if [ $redirect ] ; then
  exec 4<&2
  exec 5<&1
  exec &> $redirect
fi

savu_mpijob_local.sh $TESTDATA/data/24737.nxs $TESTDATA/test_process_lists/mpi_gpu_test.nxs $output

if [ $redirect ] ; then
 exec 2<&4
 exec 1<&5
fi

