#!/bin/bash

python create_autosummary.py api autosummary.rst
#python create_autosummary.py api_plugin_dev dev_autosummary.rst
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo $DIR
export SPHINX_APIDOC_OPTIONS='members,private-members,undoc-members,show-inheritance'
sphinx-apidoc -fMeTP $DIR/../ -o $DIR/source/api
export SPHINX_APIDOC_OPTIONS='members,undoc-members,noindex'
sphinx-apidoc -fe $DIR/../ -o $DIR/source/api_plugin_dev
python create_dev_autosummary.py
sphinx-build -a -E -j 2 -b html $DIR/source/ $DIR/build/


