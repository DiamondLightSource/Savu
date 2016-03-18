#!/bin/bash

python create_autosummary.py
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo $DIR
export SPHINX_APIDOC_OPTIONS='members,private-members,undoc-members,show-inheritance'
sphinx-apidoc -fMeTP $DIR/../ -o $DIR/source/api
sphinx-apidoc -fMeT $DIR/../ -o $DIR/source/api_plugin_dev
sphinx-build -a -E -j 2 -b html $DIR/source/ $DIR/build/ 

