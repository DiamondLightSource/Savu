#!/bin/bash

if [[ $# -lt 1 ]]; then
    echo "Please specify Savu version to install"
    exit -1
fi

VERSION=$1
ALL_VERSIONS_URL="https://raw.githubusercontent.com/DiamondLightSource/Savu/master/install/all_versions.txt"

wget "$ALL_VERSIONS_URL" || exit -1

SAVU_URL=$(awk '$1 == "'$VERSION'" { print $2 }' all_versions.txt)

if [[ "$SAVU_URL" == "" ]]; then
    echo "Savu version not found"
    exit -1
fi

wget -O savu.tar.gz "$SAVU_URL"

tar -xvzf savu.tar.gz

cd savu_v${VERSION}
chmod +x savu_installer.sh
./savu_installer.sh --no_prompts | tee savu_installation.log
