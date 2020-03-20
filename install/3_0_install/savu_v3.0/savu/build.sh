#!/bin/bash

# activate the environment where the python build is happening
# this will give access to the packages needed by the C source build
source ${PREFIX%/conda-bld*}/bin/activate
# build the dezing and unwarp libraries
cd c_source_code; make; cd ..

$PYTHON setup.py install --facility $FACILITY   # Python command to install the script.
