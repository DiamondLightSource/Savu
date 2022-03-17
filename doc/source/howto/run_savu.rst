How to run Savu
---------------

To run Savu you require a data file and a process list (a link to process list). If Savu has been installed into the module system:

    >>> module load savu

To run Savu across the cluster (in parallel):

    >>> savu_mpi  <data_path>  <process_list_path>  <output_folder>  <optional_args>

To run Savu on your local machine (single threaded):

    >>> savu  <data_path>  <process_list_path>  <output_folder>  <optional_args>


The full list of aliases provided with `module load savu` is given below:

+-------------------+---------------------------------------+----------------------------------------------+
|    Alias          |            Description                |             Required input parameters        |
+===================+=======================================+==============================================+
|   savu            | Run single threaded Savu              | <data_path> <process_list_path> <output_path>|
+-------------------+---------------------------------------+----------------------------------------------+
|  savu_mpi         | Run mpi Savu across the cluster       | <data_path> <process_list_path> <output_path>|
+-------------------+---------------------------------------+----------------------------------------------+
| savu_mpi_preview  | Run mpi Savu across 1 node (20 cores) | <data_path> <process_list_path> <output_path>|
+-------------------+---------------------------------------+----------------------------------------------+
| savu_config       | Create or amend process lists         |                                              |
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


.. note:: Savu produces a hdf5 file for each plugin in the process list.  It is recommended, if you are running
          Savu on a full dataset, to pass the optional argument `-d <tmp_dir>` where `tmp_dir` is the temporary
          directory for a visit.

.. raw:: html

    <iframe width="560" height="315" src="https://youtu.be/5RhNBVZSBsY" title="YouTube video, Savu" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

