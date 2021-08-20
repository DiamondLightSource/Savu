
.. raw:: html

    <style> .blue {color:#2c7aa3} </style>

.. role:: blue

Frequently Asked Questions
---------------------------

.. dropdown:: Can I create my own plugin?

        Yes. You can read more about how to do that on the :ref:`Plugin Guide <plugin_guide>` page.
        There are some examples of plugin files on the :ref:`plugin_templates` page.

.. dropdown:: When I create a plugin file, how many files are needed?

        Two files are required.

        1. A file containing your plugin, named :blue:`plugin_name`.py containing a
        class :blue:`PluginName`

            This file contains your plugin definitions and statements.

        2. A file containing plugin tools, named :blue:`plugin_name_tools`.py,
        containing a class :blue:`PluginNameTools`

            This file contains the parameter details and citations in a yaml format. You can \
            assign each parameter a data type, a description, a visibility level and a \
            default value.

        You can read more about how to create these files on the :ref:`Plugin Guide <plugin_guide>`
        page.

.. dropdown:: Where do I save my plugin files?

        If you are working on your local Savu directory, then you should save
        the plugin file and plugin tools file to /Savu/savu/plugins/.
        Within the plugins directory, you can also create a folder or choose
        an existing folder within which to put these files.

        :blue:`If you are on a diamond workstation and you are developing a plugin
        which you want to be accessible straight away, you can save it to
        /dls_sw/apps/savu/4.0/savu_plugins_new. Plugins from this directory
        are automatically accessible from any Diamond workstation after
        module loading Savu.`

        :blue:`If you don't want to load plugins from this directory, then you should
        clear the` ``SAVU_PLUGINS_PATH`` :blue:`prior to using` ``module load``.

        >>> export SAVU_PLUGINS_PATH=''

        :blue:`Alternatively, you could point this variable to another directory,
        holding your plugin and plugin tools files. This would mean that
        these plugins are accessible when you run savu commands.`

        >>> export SAVU_PLUGINS_PATH=/dir/to/plugins

.. dropdown:: How do I update my process list?

    If your process list was created using a previous version of Savu, it may
    be useful to update it. Additional parameter information and
    citation information may have been added to it.

    There are two ways to update or refresh your process list.

    1. You can open it inside the current version of Savu and save it again.

    2. You can use the command ``savu_refresh`` with a file or a directory
    and update that process list or update all process list files within
    that directory.

    .. toctree::
       :glob:
       :maxdepth: 2

       ../reference/savu_commands/savu_refresh

    .. code-block:: none

        usage: savu_refresh [-h] [-f FILE] [-d DIRECTORY]

Working from a workstation at Diamond Light Source
**************************************************

.. _`terminal`:

.. dropdown:: What is a terminal?

    A terminal could also be referred to as a console, shell, command
    prompt or command line.

    It is a program on your computer which can take in text based
    instructions and complete them. For example, navigating to a particular file
    or directory. It can also perform more complex tasks relating to
    software installation.

    It doesn't have a graphical interface, and it allows access to a wide
    range of commands quickly.

.. dropdown:: How do I run my own Savu repository inside the terminal?

    1. Open a `terminal`_ and set the ``SAVUHOME`` variable to be your directory
    where the Savu folder which you want to run is.

    >>> export SAVUHOME=/dir/to/savu/repo

    This must be completed before the ``module load savu`` command is used.

    2. Using the `module`_ system, ``module load`` the version of Savu you are using

    >>> module load savu/4.0

    This will add all of the related packages and files into your path, meaning
    that your program will be able to access these packages when it is run.

    These packages are required for the various plugins to run correctly.

    3. Run the savu command which you wish to use. For example,

    >>> savu_config

    The command should be executing using your specified directory files.

    .. note:: If you are having trouble here, you can double check your
        ``SAVUHOME`` directory. It will be blank if you have not set it.
        You can display this to your terminal by typing

        >>> echo $SAVUHOME

        You can also check the Savu path being used. This should display the
        path to your specified directory.

        >>> which savu

    .. .. note:: If you are still having a problem, once you have loaded the
        correct packages, you can enter your Savu repository directory and type
        'python -m scripts.config_generator.savu_config'

.. _`module`:

.. dropdown:: What is ``module load`` doing?

    It is modifying the users environment, by including the path to certain
    environment modules.

    It allows Savu to access all of it's relevant packages and to run correctly.

    You can read more about how module works at `modules.readthedocs.io <https://modules.readthedocs.io>`_

.. dropdown:: What do I do if I have module loaded the wrong version of Savu?

    You can use repeat the `module`_ command, replacing ``load`` with ``unload``

    >>> module unload savu/<version_number>

    Then proceed with the version which you originally wanted to load.

    >>> module load savu/4.0
