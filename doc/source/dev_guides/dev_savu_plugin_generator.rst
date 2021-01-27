.. _plugin_generator_guide:

Generating a Savu Plugin
**************************

Use the command: ``savu_plugin_generator`` to create a plugin and it's required files.

.. toctree::
   :glob:
   :maxdepth: 2

   ../reference/savu_commands/savu_plugin_generator

.. code-block:: none

    usage: savu_plugin_generator [-h] [-q] [-d] plugin_name

There are three steps:

1. If a plugin exists with this name, then the file location will be found. If it does exist, then this file path will be
displayed on the command line. If it doesn't exist, then a file will be created inside the savu/plugins directory.

2. If a plugin tools files exists, then the file location will be found. If it does exist, then this file path will be
displayed on the command line. If it doesn't exist, then a file will be created inside the savu/plugins directory.

3. If a plugin documentation file exists, then the file location will be found. If it does exist, then this file path will be
displayed on the command line. If it doesn't exist, then a file will be created inside the savu/plugins directory.

The detailed template for the plugin class is here and can be downloaded here.

.. literalinclude:: ../files_and_images/plugin_guides/plugin_name_example.py
    :language: python

You can download it
:download:`here <../files_and_images/plugin_guides/plugin_name_example.py>`.
An extended version is available :download:`here <../../../plugin_examples/plugin_templates/general/plugin_template1_with_detailed_notes.py>`.

For a list of templates visit the :ref:`plugin template<plugin_templates>` page.


Plugin Documentation
--------------------

Below is a list of the current plugins grouped by type. You may also use the
search bar on the left to find a specific one.

.. toctree::
   :maxdepth: 2

   ../reference/plugin_documentation