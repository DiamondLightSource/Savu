#!/bin/bash

savu_path=$(python -c "import savu; import os; print os.path.abspath(os.path.dirname(savu.__file__))")
test_path=$savu_path'/../test_data'
export TESTDATA=$test_path
echo '$TESTDATA points to the Savu test data folder at' $TESTDATA

