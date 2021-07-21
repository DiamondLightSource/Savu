=============================================
How to build the read the docs pages locally
=============================================


Update the restructured text files
===================================

First, run the update_rst_1.sh script from inside your Savu directory.

    >>> cd /path/to/Savu/
    >>> source doc/update_rst_1.sh

This script will remove obsolete documentation files and repopulate these pages.

1. Documentation for the savu_config commands will be generated
2. Download pages for plugin templates will be created
3. The plugin api contents page and plugin documentation contents page will be populated
4. The plugin documentation pages will be generated. This includes information with parameter details, citations and a link to further documentation.

Create a virtual environment
============================

.. note::
    If you are installing the packages from the doc-requirements file for the first time, then you
    need to open this file and uncomment all packages preceeded by a # symbol.
    To do this you could use the line "gedit /path/to/Savu/doc/source/doc-requirements.txt"

Setup a new virtual environment using the requirements file Savu/doc/source/doc-requirements.txt.
If you are using a diamond computer you can load python into your path to do this.

    >>> module load python/3.7
    >>> python -m venv /path/to/venv/doc-env

Next, activate this virtual environment and install the requirements.

    >>> source /path/to/venv/doc-env/bin/activate
    >>> pip install -r /path/to/Savu/doc/source/doc-requirements.txt

To view installed packages, you can run:

    >>> pip list


Update API documentation and build
===================================

While inside your virtual environment, run the update_api_2.sh script.

    >>> source /path/to/venv/doc-env/bin/activate
    >>> source /path/to/Savu/doc/update_api_2.sh

The script to update the API will first clear the directory Savu/doc/source/reference/api_plugin.
This is to remove any obsolete files. Then it will repopulate the files, covering any new plugins added.

Sphinx will then build the rest of the html pages and place these inside Savu/doc/build.

You can view the completed pages by opening the Savu/doc/build/index.html page inside a browser.

To conclude
============

When you have finished, you can deactivate the virtual environment and remove python from your path.

    >>> deactivate
    >>> module unload python/3.7