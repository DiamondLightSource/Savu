#!/bin/bash

# build the dezing and unwarp libraries
(cd c_source_code; make)

$PYTHON setup.py install --facility $FACILITY   # Python command to install the script.
