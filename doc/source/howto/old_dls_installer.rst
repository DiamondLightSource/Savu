:orphan:

=====================================
Notes for installing Savu at Diamond
=====================================

(1) Install Python Anaconda for Python 2.7 version (https://www.continuum.io/downloads). Then::

    >> export PATH=/path/to/anaconda/bin:$PATH
    
(2) >> conda install conda-build

(3) # These library versions have been tested but any versions can be tried.
    >> module load openmpi/1.6.5   # potentially any MPI library
    >> module load cuda/7.0
    >> module load fftw

(4)(a) To install a stable version of Savu::

        # replace 1.2 with newest version
        >> conda install -c savu savu=1.2

   (b) To install from the savu_test recipe (which installs from the master repository)::

        >> conda build savu_test
        >> savubuild=`conda build savu_test --output`
        >> conda install --use-local $savubuild

.. note::
    NB: Case of (4)(b): If changes are required to conda recipes and they have not
    been pushed to the master repository then, before running step (5), do
    >> export RECIPES=/path/to/folder/containing/recipes


(5) >> savu_installer.sh dls

    # Savu should now be installed!
    # Test the installation.

(6) Copy the Savu module template at /dls/science/groups/das/savu/savu_module_template
    to your local module folder (/home/username/privatemodules), changing the name if
    you prefer, and update the relevant paths inside the file. Then
    >> module load your_savu_module

(7) Update launcher scripts, to module load your_savu_module.
    (just type 'which savu_launcher.sh' to find the location).
    (a) savu_launcher.sh and savu_mpijob.sh if you will run across the cluster
    (b) savu_mpijob_local.sh if you will run locally in mpi mode.

(8) From a fresh terminal::

    >> source savu_setup.sh

    # single-threaded tests
    >> savu_quick_tests
    >> savu_full_tests
    
    # local mpi tests
    >> mpi_cpu_local_test.sh
    >> mpi_gpu_local_test.sh

    # cluster mpi tests
    >> mpi_cpu_cluster_test.sh /path/to/output/folder
    >> mpi_gpu_cluster_test.sh /path/to/output/folder
