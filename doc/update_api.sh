#!/bin/bash

python create_plugin_doc.py api_plugin plugin_autosummary.rst plugin
python create_plugin_doc.py plugin_documentation plugin_documentation.rst plugin
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo $DIR
export SPHINX_APIDOC_OPTIONS='members,undoc-members,noindex'
# members will document all modules
# undoc keeps modules without docstrings
sphinx-apidoc -feT -o $DIR/source/api_plugin $DIR/../savu/plugins/ $DIR/../savu/plugins/*tools* $DIR/../savu/plugins/**/*tools* $DIR/../savu/plugins/**/**/*tools* $DIR/../savu/plugins/**/**/**/*tools*
# add -Q to suppress warnings
sphinx-build -a -E -j 2 -b html $DIR/source/ $DIR/build/
