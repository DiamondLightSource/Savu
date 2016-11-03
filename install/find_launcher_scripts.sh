#!/bin/bash

facility=$1

# check anaconda distribution
ana_path=$(command -v anaconda)
if ! [ "$ana_path" ]; then
    echo "ERROR: I require anaconda but I can't find it.  Check /path/to/anaconda/bin is in your PATH."
    return
else
    ana_path=$(python -c "import sys; print sys.prefix")
    echo "Using anaconda:" $ana_path
fi

# get savu path through python import

# if facility doesn't exist
    # print a list of all the possible facilities
    # return
# else
# output the path to the launcher scripts

