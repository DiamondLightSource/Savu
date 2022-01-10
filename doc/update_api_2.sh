#!/bin/bash

echo "***********************************************************************"
echo "                Starting the second read the docs script"
echo "***********************************************************************"
echo "        Creating plugin API files and html pages for read the docs.."

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# members will document all modules
# undoc keeps modules without docstrings
export SPHINX_APIDOC_OPTIONS='members,undoc-members,noindex'

# Remove directory for api so that there are no obsolete files
rm -rf $DIR/source/reference/plugin_api/
rm -rf $DIR/source/reference/framework_api/

# sphinx-apidoc [options] -o <outputdir> <sourcedir> [pathnames to exclude]
# -f, --force. Usually, apidoc does not overwrite files, unless this option is given.
# -e, --separate. Put each module file in its own page.
# -T, --no-toc. Do not create a table of contents file.
# -E, --no-headings. Do not create headings for the modules/packages. This is useful, for example, when docstrings already contain headings.
# add -Q to suppress warnings

# Generate plugin api rst files
sphinx-apidoc -feTE -o $DIR/source/reference/plugin_api $DIR/../savu/plugins/ $DIR/../savu/plugins/loaders/utils/** $DIR/../savu/plugins/savers/utils/** $DIR/../savu/plugins/unregistered/** $DIR/../savu/plugins/under_development/** $DIR/../savu/plugins/*tools* $DIR/../savu/plugins/**/*tools* $DIR/../savu/plugins/**/**/*tools* $DIR/../savu/plugins/**/**/**/*tools*

# Generate savu framework api
sphinx-apidoc -feT -o $DIR/source/reference/framework_api $DIR/../savu/ $DIR/../savu/plugins/ $DIR/../savu/test/ $DIR/../savu/data/*tools*

# sphinx-build [options] <sourcedir> <outputdir> [filenames]
# -a Write all output files. The default is to only write output files for new and changed source files. (This may not apply to all builders.)
# -E Don’t use a saved environment (the structure caching all cross-references), but rebuild it completely. The default is to only read and parse source files that are new or have changed since the last run.
# -b buildername, build pages of a certain file type
sphinx-build -a -E -b html $DIR/source/ $DIR/build/


echo "***********************************************************************"
echo "                          End of script"
echo "***********************************************************************"

