Savu Diamond User Training
**************************

Running Savu
============

Load the Savu module
--------------------

Start by loading the Savu module

    >>> module load savu

This will load the correct version of python-anaconda, set relevant paths and provide 4 aliases:

+-------------+------------------------------------+----------------------------------------------+
|    Alias    |            Description             |             Required input parameters        |
+=============+====================================+==============================================+
|   savu      | Run single threaded Savu           | <data_path> <process_list_path> <output_path>|
+-------------+------------------------------------+----------------------------------------------+
|  savu_mpi   | Run mpi Savu                       | <data_path> <process_list_path> <output_path>|
+-------------+------------------------------------+----------------------------------------------+
| savu_config | Create or amend process lists      |                                              |
+-------------+------------------------------------+----------------------------------------------+
|  savu_test  | Run tests to check setup           |                                              |
+-------------+------------------------------------+----------------------------------------------+


Check the setup
---------------

To test the current setup is correct run:

    >> savu_test

Create a Savu test directory
----------------------------

Savu requires a data file and a process list as input.
A training folder of test data and process lists is available at /dls/science/groups/das/SavuTraining

Create an environment variable for the test folder

    >>> export DATAPATH=/dls/science/groups/das/SavuTraining

Create an output test directory in /dls/tmp/<your_fed_id> and cd to this directory.

View a process list
-------------------

1. In DAWN
^^^^^^^^^^

A process list is simply a list of processes (e.g. corrections, filters, reconstructions) that
should be applied to the data in the specified order. 

To view the example process list $DATAPATH/process_lists/simple_tomo_process.nxs do:

    >>> module load dawn
    >>> dawn &

In the DAWN GUI click on File -> open, navigate to the test folder and click on relevant process list.
In the Data Browsing perspective navigate through the tree entry->plugin and browse the plugin entries.

2. In the configurator
^^^^^^^^^^^^^^^^^^^

An alternative way to view the process list is using the configurator:

    >>> savu_config
    >>> open /dls/science/groups/das/SavuTraining/process_lists/simple_tomo_process.nxs


Run examples
------------

1. single process
^^^^^^^^^^^^^^^^^

Run the single-threaded verion of Savu with the data file $DATAPATH/data/LD_2W50_8_Dataset_038.nxs and the process list
$DATAPATH/process_lists/simple_tomo_process.nxs and output to the current directory.

    >>> savu <data_file> <process_list> .

View the output data in Dawn (see below) and look at the log files (user.log and log.txt) in the output directory.


2. multiple process
^^^^^^^^^^^^^^^^^^^

The MPI version of Savu will run on the cluster.

    >>> savu_mpi <data_file> <process_list> .

To view the job in the queue:

    >>> module load global/cluster
    >>> qstat

To view the user log file during the run 

    >>> less user.log

Or to view the full log file

    >>> less /dls/tmp/savu/savu.o<job_id>

(job_id is in qstat). Shift-f to dynamically watch the file.


View the output data in DAWN
----------------------------

Once the run is complete, the current directory will contain all the output hdf5 (.h5?) files and the .nxs file
that links the files together.  Do not change the names of the files as this will break the link to the data.
You can view the data in Dawn by opening the .nxs file.  


-----------------------------------------------------------------------------------------------------------


Creating and amending process lists
===================================

Process lists
-------------

Each process list requires a loader as the first entry, a saver as the final entry and any combination of corrections/filters/reconstructions in-between.


The Configurator
----------------

Open the configurator:

    >>> savu_config

whilst inside the configurator type --help for a list of available commands.

e.g to view available loaders:

    >>> list loaders names


Special features
----------------

Previewing
^^^^^^^^^^

Previewing enables the process list to be applied to a subset of the data.

Copy the tomo_process.nxs file to /dls/tmp/<fed_id>

Open the configurator and open the process list:

    >>> open tomo_process.nxs

Each loader has a preview parameter that is empty by default (apply processing to all the data).  
The preview requires a list as input with entries for each data dimension.  Each entry in the 
preview list requires a string of 4 values, ‘start:stop:step:chunk’, where each of the strings 
should be replaced with an integer or the key words ‘end’ or ‘mid’.

For example, the test data is 3D, in the order (rotation_angle, detector_y, detector_x).  
To apply the data only to the middle 5 sinograms:

    >>> mod 1.1 [‘0:end:1:1’, ‘mid-2:mid+2:1:1’, ‘0:end:1:1’]

Or alternatively,

    >>> mod 1.1 [‘0:end:1:1’, ‘mid:mid+1:1:5’, ‘0:end:1:1’]

Amend the process list to preview only the middle 5 sinograms.


Turning process on/off
^^^^^^^^^^^^^^^^^^^^^^

Any process can be turned off by typing

    >>> mod <processNo>.off

Or

    >>> mod <processNo>.on


Sinogram centering
^^^^^^^^^^^^^^^^^^

There is an optional auto-centering filter (vo_centering).  However, it is computationally expensive 
and should only be applied to a preview.  There are two ways to do this. 

1. Amend the preview parameter in the loader
2. Create a process list that incorporates vo_centering (choose relevant degree of polynomial) and reconstructs the data.
3. There are two additional .h5 files that end in *cor_raw.h5 and *cor_fit.h5: View these in DAWN
   and get the fit value (if satisfied with the reconstruction).
4. Manually amend the centering parameter to the required value for the full data reconstruction.

OR

1. Ensure the preview parameter is empty.
2. Amend the preview parameter in the vo_centering plugin entry. 


Parameter_tuning
^^^^^^^^^^^^^^^^

If you wish to test a preview reconstruction with a range of values for a parameter, for instance, if the centering is not quite optimal, then you can add different values separated by semi-colons.  Each ‘tuned’ parameter will add an extra dimension to the data. 

For example, add 3 centering values to the process list:

    >>> mod 6.2 85;86;87

(values for example only).

Or to try FBP and CGLS reconstructions

    >>> mod 6.8 FBP;CGLS

Add parameter tuning and save the process list.  Apply the new pipeline to the data and view the output in DAWN. 

-----------------------------------------------------------------------------------------------------------

AVIZO
=====


