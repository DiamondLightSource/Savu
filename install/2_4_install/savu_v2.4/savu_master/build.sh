#!/bin/bash

if [ -z $INSTALL_VERSION ] ; then
	$PYTHON setup.py install --facility $FACILITY
else
	$PYTHON setup.py install --facility $FACILITY --install_version $INSTALL_VERSION
fi

