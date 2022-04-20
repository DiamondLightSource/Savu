How to run Savu
---------------

To run Savu you require a data file (e.g. an hdf5 file) and a process list (a link to process list).
After Savu is successfully installed into your conda environment you will have an access to the following commands bellow from your UNIX shell:

+-------------------+---------------------------------------+----------------------------------------------+
|    Alias          |            Description                |             Required input parameters        |
+===================+=======================================+==============================================+
| savu_config       | Create or amend process lists         |                                              |
+-------------------+---------------------------------------+----------------------------------------------+
|   savu            | Run single threaded Savu              | <data_path> <process_list_path> <output_path>|
+-------------------+---------------------------------------+----------------------------------------------+
| savu_mpijob_local | Run multi-threaded Savu on your PC    | <data_path> <process_list_path> <output_path>|
+-------------------+---------------------------------------+----------------------------------------------+
|  savu_mpi         | Run mpi Savu across the cluster       | <data_path> <process_list_path> <output_path>|
+-------------------+---------------------------------------+----------------------------------------------+
| savu_mpi_preview  | Run mpi Savu across 1 node            | <data_path> <process_list_path> <output_path>|
+-------------------+---------------------------------------+----------------------------------------------+

Optional arguments:

+--------+----------------------------+-----------------------+--------------------------------------------------+
|  short |         long               |       argument        |                   Description                    |
+========+============================+=======================+==================================================+
|  -f    |    **--folder**            |      folder_name      | Override the output folder name                  |
+--------+----------------------------+-----------------------+--------------------------------------------------+
|  -d    |    **--tmp**               |      path_to_folder   | Store intermediate files in this (temp) directory|
+--------+----------------------------+-----------------------+--------------------------------------------------+
|  -l    |     **--log**              |      path_to_folder   | Store log files in this directory                |
+--------+----------------------------+-----------------------+--------------------------------------------------+
| -v, -q | **--verbose**, **--quiet** |                       | Verbosity of output log messages                 |
+--------+----------------------------+-----------------------+--------------------------------------------------+

If Savu has been installed into the `module <https://modules.readthedocs.io/en/latest/module.html>`_  system as at Diamond Light source, then you can enable it with:

    >>> module load savu

To run Savu on your local machine (single threaded):

    >>> savu  <data_path>  <process_list_path>  <output_folder>  <optional_args>

or multi-threaded:

    >>> savu_mpijob_local  <data_path>  <process_list_path>  <output_folder>  <optional_args>

and to run Savu across the cluster (in parallel):

    >>> savu_mpi  <data_path>  <process_list_path>  <output_folder>  <optional_args>

..  youtube:: 5RhNBVZSBsY

.. note:: Savu produces a hdf5 file for each plugin in the process list.  It is recommended, if you are running
          Savu on a full dataset, to pass the optional argument `-d <tmp_dir>` where `tmp_dir` is the temporary
          directory for a visit.
