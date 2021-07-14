#!/bin/bash

package=$1
installed_version=$2

echo "Building $package..."
conda build $recipes/$package
build=$(conda build $recipes/$package --output)

echo "Installing $package..."
conda install -y -q --use-local $build

echo "Checking that $package is installed into conda environment"
conda list

conda list $package > check_conda_package.txt
if grep -q $installed_version check_conda_package.txt; then
    echo -e "\nPackage $package of version $installed_version is found in Savu's environment, continue with the installation..."
    rm -f check_conda_package.txt
else
    echo -e "\nPackage $package of version $installed_version is NOT found in Savu's environment! \nInstallation process terminated!"
    rm -f check_conda_package.txt
    exit 0
fi
