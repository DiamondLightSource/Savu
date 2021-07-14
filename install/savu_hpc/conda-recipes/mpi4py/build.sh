#!/bin/bash

# set compiler wrapper
MPICC=$(command -v mpicc)

$PYTHON setup.py build --mpicc=$MPICC
$PYTHON setup.py install
