#!/bin/bash

echo "***********************************************************************"
echo "                Starting the second read the docs script"
echo "***********************************************************************"
echo "        Creating plugin API files and html pages for read the docs.."

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# members will document all modules
# undoc keeps modules without docstrings
export SPHINX_APIDOC_OPTIONS='members,undoc-members,noindex'

# Remove directory for plugin api so that there are no obsolete files
rm -rf $DIR/source/reference/api_plugin/

# Generate plugin api rst files
sphinx-apidoc -feT -o $DIR/source/reference/api_plugin $DIR/../savu/plugins/ $DIR/../savu/plugins/loaders/utils/** $DIR/../savu/plugins/savers/utils/** $DIR/../savu/plugins/unregistered/** $DIR/../savu/plugins/under_development/** $DIR/../savu/plugins/*tools* $DIR/../savu/plugins/**/*tools* $DIR/../savu/plugins/**/**/*tools* $DIR/../savu/plugins/**/**/**/*tools*
# add -Q to suppress warnings

sphinx-build -a -E -b html $DIR/source/ $DIR/build/


echo "***********************************************************************"
echo "                          End of script"
echo "***********************************************************************"

