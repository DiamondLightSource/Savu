#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo $DIR

# Add the relevant savu libraries into your path
module load savu/4.0

# Create pages for savu_config commands and plugin template documentation
python -m doc.create_arg_parser_doc
python -m doc.create_plugin_template_doc

# Remove directory for plugin doc so that there are no obsolete files
rm -rf $DIR/source/reference/plugin_documentation/

# Create contents for plugin api and plugin tools documentation
python -m doc.create_plugin_doc api_plugin plugin_autosummary.rst
python -m doc.create_plugin_doc plugin_documentation plugin_documentation.rst

# Pick up command prompt lines from plugin documentation and create tests
python -m doc.create_individual_doc_test

# Run documentation tests for process list refresh and process list command execution
# Errors should be raised here if there is a problem with a plugin reference
# Log files containing the resulting output from each command will be created
# python -m unittest savu.test.travis.framework_tests.plugin_doc_test_runner

module unload savu/4.0