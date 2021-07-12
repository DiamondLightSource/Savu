#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo $DIR
export SPHINX_APIDOC_OPTIONS='members,undoc-members,noindex'

python -m doc.create_plugin_doc api_plugin plugin_autosummary.rst plugin
python -m doc.create_plugin_doc plugin_documentation plugin_documentation.rst plugin

# members will document all modules
# undoc keeps modules without docstrings

sphinx-apidoc -feT -o $DIR/source/reference/api_plugin $DIR/../savu/plugins/ $DIR/../savu/plugins/loaders/utils/** $DIR/../savu/plugins/savers/utils/** $DIR/../savu/plugins/unregistered/** $DIR/../savu/plugins/under_development/** $DIR/../savu/plugins/*tools* $DIR/../savu/plugins/**/*tools* $DIR/../savu/plugins/**/**/*tools* $DIR/../savu/plugins/**/**/**/*tools*
# add -Q to suppress warnings

# Pick up command prompt lines from plugin documentation and create tests
# python -m doc.create_individual_doc_test
# python -m unittest savu.test.travis.framework_tests.plugin_doc_test_runner

sphinx-build -a -E -b html $DIR/source/ $DIR/build/
