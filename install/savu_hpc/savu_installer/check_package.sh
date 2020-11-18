#!/bin/bash
if grep -q $VER_PACKAGE check_conda_package.txt; then
    echo -e "\nPackage $PACKAGE of v.$VER_PACKAGE is found in Savu's environment, continue with installation..."
    rm -f check_conda_package.txt
else
    echo -e "\nPackage $PACKAGE of v.$VER_PACKAGE is NOT found in Savu's environment! \nInstallation process terminated!"
    rm -f check_conda_package.txt
    exit 0
fi
