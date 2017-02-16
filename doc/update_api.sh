#!/bin/bash

python create_autosummary.py api framework_autosummary.rst framework
python create_autosummary.py api_plugin plugin_autosummary.rst plugin
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo $DIR
export SPHINX_APIDOC_OPTIONS='members,private-members,undoc-members,show-inheritance'
sphinx-apidoc -fMeTP $DIR/../ -o $DIR/source/api
export SPHINX_APIDOC_OPTIONS='members,undoc-members,noindex'
sphinx-apidoc -feT $DIR/../ -o $DIR/source/api_plugin
#python create_dev_autosummary.py
sphinx-build -a -E -j 2 -b html $DIR/source/ $DIR/build/
