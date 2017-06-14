Installing Savu at Diamond
==========================

(Savu requires openmpi...)

1. :download:`Download savu version 2.0 <../../install/2_0_install/savu_v2.0.tar.gz>` and unzip.

2. >>> bash /path/to/savu_v2/savu_installer.sh
   and follow the instructions for installation.

3. To run savu... (updating installer scripts etc.)

1. Install Python Anaconda for Python 2.7 version (https://www.continuum.io/downloads) and add to the PATH.

    >>> export PATH=/path/to/anaconda/bin:$PATH
    
2. Install conda-build.

    >>> conda install conda-build

3.  Load other libraries required for the build.

    >>> module load openmpi/2.1.0
    >>> module load cuda/7.0
    >>> module load fftw

.. note:: The above libraries are the latest tested versions.


4. Install Savu.

    a. Install a stable version of Savu:

    >>> conda install -c savu savu=2.0

    b. Install from the master repository using the savu_test recipe (

Install from the savu_test recipe (which installs from the master repository):

    >>> conda build savu_test
    >>> savubuild=`conda build savu_test --output`
    >>> conda install --use-local $savubuild


.. note:: NB: Case of 4.b: If changes are required to conda recipes and they have not
    been pushed to the master repository then, before running step 5, do

    >>> export RECIPES=/path/to/folder/containing/recipes


5. Install and build other libraries

    >>> savu_installer.sh dls

Savu should now be installed!


Test the installation
=====================

1. Copy the Savu module template at /dls/science/groups/das/savu/savu_module_template
to your local module folder (/home/username/privatemodules), changing the name if
you prefer, and update the relevant paths inside the file. Then

    >>> module load your_savu_module


2. Update launcher scripts, to module load your_savu_module (type `which savu_launcher.sh` to find the location).

    a. Update savu_launcher.sh and savu_mpijob.sh if you will run across the cluster

    b. Update savu_mpijob_local.sh if you will run locally in mpi mode.


3. Run the Savu tests.

    a. Set test data environment variable (use a fresh terminal).

    >>> source savu_setup.sh

    b. Run single-threaded tests

    >>> savu_quick_tests
    >>> savu_full_tests
    
    c. Run local mpi tests

    >>> mpi_cpu_local_test.sh
    >>> mpi_gpu_local_test.sh

    d. Run cluster mpi tests

    >>> mpi_cpu_cluster_test.sh /path/to/output/folder
    >>> mpi_gpu_cluster_test.sh /path/to/output/folder

