How to open a process list in the Savu configurator
----------------------------------------------------

    >>> module load savu
    >>> savu_config
    >>> help                # show the available commands
    >>> list                # list the available plugins
    >>> open /dls/science/groups/das/SavuTraining/process_lists/simple_tomo_pipeline.nxs  # open a process list
    >>> disp -v             # view parameter descriptions
    >>> disp -v -a          # view hidden parameters
    >>> exit                # exit the configurator

.. note:: The process lists created by the configurator are in NeXus (.nxs) format (http://www.nexusformat.org/).

For examples of how to create and amend process lists see :ref:`create_process_list` and :ref:`amend_process_list`.
