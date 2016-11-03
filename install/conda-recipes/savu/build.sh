#!/bin/bash

$PYTHON setup.py install --facility $FACILITY   # Python command to install the script.

# run the savu installer to install additional packages
savu_installer.sh

