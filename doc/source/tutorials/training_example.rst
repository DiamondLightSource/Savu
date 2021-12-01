

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
    >>> python process_lists/refresh.py  # ensure the process lists are up-to-date with the current version of Savu.


1. Run a single-threaded Savu job on your local machine
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

View the simple_tomo_pipeline_cpu.nxs process list inside the configurator

    >>> savu_config
    >>> open process_lists/simple_tomo_pipeline_cpu.nxs
    >>> disp -v
    >>> exit

Run the single-threaded version of Savu with the data file `data/tomo_standard.nxs`.
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
    >>> set 3 off
5. Display only the astra recon plugin with parameter descriptions.
    >>> disp 6 -v
6. Turn the astra recon log parameter to True.
    >>> mod 6.3 True
7. Apply previewing to reconstruct the middle 10 sinograms only (:ref:`previewing`).
    >>> mod 1.1 [:, mid-5:mid+6, :]
8. Manually entering centre of rotation (:ref:`centering`).
    >>> set 5 off
    >>> mod 6.7 86
9. Save the process list and exit.
    >>> save process_lists/test.nxs
    >>> exit

Now run `savu_mpi_preview` with `data/tomo_standard.nxs' and the new process list 'process_lists/test.nxs` and
view the output in DAWN.

.. _eg2:

Example 2
=========
1. Open the process list.
    >>> savu_config
    >>> open process_lists/test.nxs
2. Apply parameter tuning to centre value (:ref:`parameter_tuning`).
    >>> mod 6.7 84:87:0.5;
3. Modify the reconstruction algorithm to CGLS_CUDA and increase iterations.
    >>> disp 6 -v
    >>> mod 6.6 CGLS_CUDA
    >>> mod 6.4 10
4. Apply parameter tuning to Paganin Ratio parameter.
    >>> set 3 on
    >>> mod 6.3 False
    >>> mod 3.1 50;100;200
5. Save the process list and exit.
    >>> save process_lists/test2.nxs
    >>> exit

Now run `savu_mpi_preview` with `data/tomo_standard.nxs` and the new process list `process_lists/test2.nxs` and
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
    >>> add NxtomoLoader            # add the loader plugin (use tab completion)
    >>> add DarkFlatFieldCorrection # add the correction plugin
    >>> add RemoveAllRings          # add the ring artefact removal plugin
    >>> add VoCentering             # add auto-centering plugin
    >>> add PaganinFilter           # add contrast enhancement plugin
    >>> add AstraReconGpu           # add reconstruction plugin
    >>> mod 6.3 False               # don't take the log of the data in recon (required by paganin)
    >>> mod 5.1 [:, mid-5:mid+6, :] # apply centering to mid 10 sinograms only
    >>> save tomo_pipeline.nxs      # save the process list
    >>> exit                        # exit the configurator

.. _previewing_eg1:

Apply previewing
================

    >>> savu_config                 # open the configurator
    >>> open tomo_pipeline.nxs      # open the full data process list
    >>> mod 1.1 [:, mid-2:mid+3, :] # process the middle 5 sinograms only
    >>> ref 5 -d                    # refresh auto-centering to default parameters (remove previewing)
    >>> save tomo_pipeline_preview.nxs # save the process list
    >>> exit                        # exit the configurator


.. _manualcentering:

Apply manual centering
======================

    >>> savu_config                 # open the configurator
    >>> open tomo_pipeline_preview.nxs  # open the preview process list
    >>> set 5 off                   # turn the auto-centering plugin off
    >>> mod 6.7 86                  # manually enter the centre value to the recon
    >>> save tomo_pipeline_preview2.nxs # save the process list
    >>> exit                        # exit the configurator

.. _cor_parameter_tuning:

Apply parameter tuning to the centre of rotation
================================================

    >>> savu_config                 # open the configurator
    >>> open tomo_pipeline_preview2.nxs # open the preview process list
    >>> mod 6.7 85;85.5;86;86.5     # apply 4 different values to the centre of rotation param in the reconstruction
    >>> save tomo_pipeline_preview3.nxs # save the process list
    >>> exit


