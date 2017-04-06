Savu Diamond User Guide
***********************

Introduction
------------
Tomography data collected at Diamond has, in recent years, been processed using the Tomo Recon GPU 
cluster-based code available through DAWN.  A steady increase in the popularity of tomographic imaging, 
due to improvements in data acquisition and computer technology, has led to a broadening of the range of 
tomographic experiments, and their complexity, across multiple fields.   

In full-field tomography, where the whole region-of-interest is irradiated by the beam simultaneously, 
time-resolved imaging is becoming increasingly popular.  In mapping tomography, where a thin beam of 
X-rays is translated and rotated across the region of interest, multi-modal data collection is common and
incorporates a variety of measurements, such as X-ray absorption, diffraction and fluorescence. 

This wide range of experimental requirements leads to a wider range of software processing requirements.  
Savu, developed in the Data Analysis Group at Diamond Light Source Ltd., is the new tomography data 
processing tool that has been developed to allow greater flexibility in tomography data processing. Custom
process lists are passed to Savu at runtime to enable processing to be tailored to a specific experimental
setup.  The framework is capable of processing multiple, n-dimensional, very large datasets, and is written
in Python to allow easy integration of new functionality, allowing researchers and beam line staff greater
flexibility in integrating new, cutting-edge processing techniques.

A quick comparison of the old and new tomography software is given in the table below.

+-------------------+---------------------------------------+----------------------------------------------+
|                   |            Tomo Recon                 |                      Savu                    |
+===================+=======================================+==============================================+
|    Data type      |     Full-field tomography data        |   Full-field and mapping tomography data     | 
+-------------------+---------------------------------------+----------------------------------------------+
|  Data dimensions  |                 3-D                   |                     N-D                      |
+-------------------+---------------------------------------+----------------------------------------------+
|   Data format     |          Nxtomo NEXUS format          |      Multiple formats (any possible)         |
+-------------------+---------------------------------------+----------------------------------------------+
|  Output format    |                 tiff                  | Multiple formats (hdf5 - tiff coming soon)   |
+-------------------+---------------------------------------+----------------------------------------------+
|     Data size     |             Limited by RAM            |        No RAM limit (uses parallel hdf5)     |
+-------------------+---------------------------------------+----------------------------------------------+
| Datasets per run  |             One dataset               |           Multiple datasets                  |
+-------------------+---------------------------------------+----------------------------------------------+
|   Data slicing    |            Sinogram only              |       Flexible (e.g sinogram/projection)     |
+-------------------+---------------------------------------+----------------------------------------------+
|    Processing     | Fixed: correction, ring removal, FBP  |        Custom: Tailored process lists        |
+-------------------+---------------------------------------+----------------------------------------------+
| New functionality |            No integration             |                Easy integration              |
+-------------------+---------------------------------------+----------------------------------------------+


Process lists
-------------
Savu is a framework that does nothing if you run it on its own.  It requires a process list, passed to it 
at runtime along with the data, to detail the processing steps it should follow.  A Savu process list is 
created using the Savu configurator tool, which stacks together plugins chosen from a repository. Each plugin
performs a specific independent task, such as correction, filtering, reconstruction.  For a list of available
plugins see `plugin API <file:///home/qmm55171/Documents/Git/git_repos/Savu/doc/build/plugin_autosummary.html>`_.

Plugins are grouped into categories of similar functionality.  Loaders and savers are two of these categories and each
process list must begin with a loader plugin and end with a saver plugin (soon to be deprecated), with at
least one processing plugin in-between.  The loader informs the framework of the data location and format along
with important metadata such as shape, axis information, and associated patterns (e.g. sinogram, projection).
Therefore, the choice of loader is dependent upon the format of the data.

.. note:: Savu plugins can run on the CPU or the GPU.  If you are running the single-threaded version of Savu
          and you don't have a GPU you will be limited to CPU plugins.

Example: View a process list in the Savu configurator.
    
    >>> module load savu
    >>> savu_config
    >>> help                # show the available commands
    >>> list                # list the available plugins
    >>> open /dls/science/groups/das/SavuTraining/process_lists/simple_tomo_pipeline.nxs  # open a process list
    >>> exit                # exit the configurator

.. note:: The process lists created by the configurator are in NeXus (.nxs) format (http://www.nexusformat.org/).

For examples of how to create and amend process lists see :ref:`create_process_list` and :ref:`amend_process_list`.


Running Savu
------------

To run Savu you require a data file and a process list (link to process list).

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



Training Examples
-----------------

Test data and process lists can be found in the directory `/dls/science/groups/das/SavuTraining` inside the data and
process_lists directories respectively.  Create a SavuTraining directory in your home directory and copy the 
data and process lists into this folder.  First, open a terminal and follow the commands below: 

    >>> mkdir SavuTraining
    >>> cd SavuTraining
    >>> cp -r /dls/science/groups/das/SavuTraining/process_lists .
    >>> cp -r /dls/science/groups/das/SavuTraining/data .
    >>> module load savu


1. Run a single-threaded Savu job on your local machine
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

View the simple_tomo_pipeline_cpu.nxs process list inside the configurator

    >>> savu_config
    >>> open process_lists/simple_tomo_pipeline_cpu.nxs
    >>> disp -v
    >>> exit

Run the single-threaded version of Savu with the data file `data/24737.nxs`.
and the process list `process_lists/simple_tomo_pipeline_cpu.nxs` and output to the current directory.

    >>> savu <data_file> <process_list> .


2. Run a parallel Savu job on the cluster
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

View the simple_tomo_pipeline.nxs file in the configurator.  Use the same data file as above, but this time use 
the `simple_tomo_pipeline.nxs` process list, which contains GPU processes.

The MPI version of Savu will run on the cluster.

    >>> savu_mpi <data_file> <process_list> .

Re-run the mpi job but send the intermediate files to a temporary directory:

    >>> savu_mpi <data_file> <process_list> .  -d  /dls/tmp

.. note:: `/dls/tmp` is for training purposes only and should not be used during a visit.


3. View the output data in DAWN
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Once the run is complete, the current directory will contain all the output hdf5 files and the .nxs file
that links the files together.  Do not change the names of the files as this will break the link to the data.
You can view the data in Dawn by opening the .nxs file (see :ref:`dawn`).


.. _amend_process_list:

4. Amend a process list
^^^^^^^^^^^^^^^^^^^^^^^

The process list tomo_pipeline.nxs is a typical full-field tomography reconstruction pipeline.  However, 
the experimental setup will determine which plugins should remain 'on' and what values the plugin 
parameters should take.  Follow the list of commands below for some examples of what you can do.


Example 1
=========
1. Open the process list.
    >>> savu_config
    >>> open process_lists/tomo_pipeline.nxs
2. View all available commands.
    >>> help
3. Switch Raven filter and Paganin filter.
    >>> move 4 3
4. Turn the Paganin filter off (and turn the reconstruction log parameter back on).
    >>> mod 3.off
5. Display only the astra recon plugin with parameter descriptions.
    >>> disp 6 -v
6. Turn the astra recon log parameter to True.
    >>> mod 6.6 True
7. Apply previewing to reconstruct the middle 10 sinograms only (:ref:`previewing`).
    >>> mod 1.6 [:, mid-5:mid+6, :]
8. Manually entering centre of rotation (:ref:`centering`).
    >>> mod 5.off
    >>> mod 6.5 86
9. Save the process list and exit.
    >>> save process_lists/test.nxs
    >>> exit

Now run `savu_mpi_preview` with `data/24737.nxs' and the new process list 'process_lists/test.nxs` and 
view the output in DAWN.

.. _eg2:

Example 2
=========
1. Open the process list.
    >>> savu_config
    >>> open process_lists/test.nxs
2. Apply parameter tuning to centre value (:ref:`parameter`).
    >>> mod 6.5 84:87:0.5;
3. Modify the reconstruction algorithm to CGLS_CUDA and increase iterations.
    >>> disp 6 -v
    >>> mod 6.6 CGLS_CUDA
    >>> mod 6.8 10
4. Apply parameter tuning to Paganin Ratio parameter.
    >>> mod 3.on
    >>> mod 6.6 False
    >>> mod 3.3 50;100;200
5. Save the process list and exit.
    >>> save process_lists/test2.nxs
    >>> exit

Now run `savu_mpi_preview` with `data/24737.nxs` and the new process list `process_lists/test2.nxs` and 
view the output in DAWN.


.. _create_process_list:

5. Create a process list
^^^^^^^^^^^^^^^^^^^^^^^^

Here is the list of commands used to create the process list `tomo_pipeline.nxs` used in the 
previous example.


.. _autocentering:

Full pipeline with auto-centering
=================================

    >>> savu_config                 # open the configurator
    >>> list nxtomo                 # filter plugin list with nxtomo
    >>> add NxtomoLoader            # add the loader plugin
    >>> list dark                   # filter plugin list with dark
    >>> add DarkFlatFieldCorrection # add the correction plugin
    >>> list raven                  # filter plugin list with raven
    >>> add RavenFilter             # add the ring artefact removal plugin 
    >>> list pag                    # filter plugin list with pag
    >>> add PaganinFilter           # add contrast enhancement plugin
    >>> list vo                     # filter plugin list with vo
    >>> add VoCentering             # add auto-centering plugin
    >>> list astra                  # filter plugin list with astra
    >>> add AstraReconGpu           # add reconstruction plugin
    >>> mod 6.6 False               # don't take the log of the data in recon (required by paganin)
    >>> list saver                  # filter plugin list with saver
    >>> add Hdf5TomoSaver           # add the saver plugin
    >>> mod 5.13 [:, mid-5:mid+6, :] # apply centering to mid 10 sinograms only
    >>> save tomo_pipeline.nxs      # save the process list
    >>> exit                        # exit the configurator

.. _previewing_eg1:

Apply previewing
================

    >>> savu_config                 # open the configurator
    >>> open tomo_pipeline.nxs      # open the full data process list
    >>> mod 1.6 [:, mid-2:mid+3, :] # process the middle 5 sinograms only
    >>> ref 5                       # refresh auto-centering to remove previewing
    >>> save tomo_pipeline_preview.nxs # save the process list
    >>> exit                        # exit the configurator


.. _manualcentering:

Apply manual centering
======================

    >>> savu_config                 # open the configurator
    >>> open tomo_pipeline_preview.nxs  # open the preview process list
    >>> mod 5.off                   # turn the auto-centering plugin off
    >>> mod 6.5 86                  # manually enter the centre value to the recon
    >>> save tomo_pipeline_preview2.nxs # save the process list
    >>> exit                        # exit the configurator

.. _cor_parameter_tuning:

Apply parameter tuning to the centre of rotation
================================================
    
    >>> savu_config                 # open the configurator
    >>> open tomo_pipeline_preview2.nxs # open the preview process list
    >>> mod 6.5 85;85.5;86;86.5     # apply 4 different values to the centre of rotation param in the reconstruction
    >>> save tomo_pipeline_preview3.nxs # save the process list
    >>> exit



Special features
----------------

.. _previewing:

Previewing
^^^^^^^^^^

Previewing enables the process list to be applied to a subset of the data.  Each loader plugin
has a preview parameter that is empty by default (apply processing to all the data).  
The preview requires a list as input with entries for each data dimension.  Each entry in the preview 
list should be of the form start:stop:step:chunk, where stop, step and chunk are optional 
(defaults: stop = start + 1, step = 1, chunk = 1) but must be given in that order.  For more information
see :meth:`~savu.data.data_structures.preview.Preview.set_preview`


Previewing Examples
===================

The 3-D NxtomoLoader plugin maps the data dimensions (0, 1, 2) to the axis labels 
(rotation_angle, detector_y, detector_x) respectively.  


    >>> savu_config
    >>> add NxtomoLoader
    >>> mod 1.6 [:, mid-5:mid+6, :]     # process the middle 10 sinograms only
    >>> mod 1.6 [0:end:2, mid-5:mid+6, :]      # process every other projection
    >>> mod 1.6 [0:end:2, mid-5:mid+6, 300:end-300] # crop 300 pixels from the sides of the detector


.. _centering:

Sinogram centering
^^^^^^^^^^^^^^^^^^

Automatic calculation OR manual input of the centre of rotation are possible in Savu. 


Auto-centering
==============

The auto-centering plugin (VoCentering) can be added to a process list before the reconstruction
plugin.  The value calculated in the centering routine is automatically passed to the reconstruction
and will override the centre_of_rotation parameter in the reconstruction plugin. The auto-centering 
plugin is computationally expensive and should only be applied to previewed data.  There are two ways
to achieve this:

1. Apply previewing in the loader plugin to reduce the size of the processed data.

and/or

2. Apply previewing in VoCentering plugin (this will not reduce the size of the data). 

.. note:: If you have applied previewing in the loader and again in the centering plugin you will be 
          applying previewing to the previewed (reduced size) data.

See :ref:`autocentering`


Manual-centering
================

Ensure the VoCentering algorithm is not in the process list (remove it or turn it off if it is already 
inside your list).  Modify the centre_of_rotation value in the reconstruction plugin, see 
:ref:`manualcentering`.  If the manual centering value is approximate you can apply parameter
tuning, see :ref:`cor_parameter_tuning`


.. _parameter_tuning:

Parameter_tuning
^^^^^^^^^^^^^^^^

If you wish to test a preview reconstruction with a range of values for a parameter, for instance, 
if the centering is not quite optimal, then you can add different values separated by semi-colons.  
Each ‘tuned’ parameter will add an extra dimension to the data. 


Parameter tuning examples
=========================

    >>> mod 6.2 85;86;87        # three distinct values
    >>> mod 6.2 84:86:0.5;      # a range of values (start:stop:step) with semi-colon at the end
    >>> mod 6.8 FBP;CGLS        # values can be strings

See :ref:`eg2` and :ref:`cor_parameter_tuning`.

View the Savu output
--------------------


.. _dawn:

In DAWN
^^^^^^^
Open a new terminal window and type:

    >>> module load dawn
    >>> dawn &

Choose the Data Browsing perspective and click on File -> open, navigate to an output folder and click on 
the .nxs file.

.. warning:: The DAWN module must be loaded in a separate terminal as it will reset relevant paths.


In Avizo
^^^^^^^^

Start avizo

    >>> module load avizo
    >>> avizo

In Avizo GUI, Click on Open Data /(File->Open Data). This should show a dialog box with list of output data 
entries. To view final output select entry/final_result_tomo/data and press OK button. This will load the data. 

1. 2D view

To view 2D slices, Select the data, right click and a pop up will be shown as below. Select Ortho Slice and Click ok button to show a 2D slice.
    .. image:: ../files_and_images/2dview.jpg	
    
2. 3D view

To view 3D volume, Select the data, right click on it and a pop up will be shown as below. Select Volume Rendering and Click OK button to show a 3D volume.
    .. image:: ../files_and_images/3dview.jpg


