.. |savu_installer| replace:: :download:`savu installer <../../../install/savu_hpc/savu_installer.tar.gz>`

How to install Savu for a HPC cluster
======================================

.. start_of_main_text

Savu is designed to run on a High Performance Computing cluster.  For optimum
performance, we recommend a fast network interconnect, such as infiniBand, and
a high performance parallel filesystem, such as GPFS or Lustre.

Requirements:
    - A Unix system with MPI libraries installed: Savu has been test with `openMPI <https://www.open-mpi.org/>`_ (latest version 4.1.1)


**Installation of Savu HPC outside Diamond Light Source (DLS) systems**

1. Check that you do **NOT** have conda in your path with "which conda". Note that the installer will install its own version of conda so it is essential that conda is not in the path.
2. Download |savu_installer| and extract
3. Set the desired Github branch of Savu to install. E.g. if you need to install the latests changes in Savu, you can select the "master" branch as >>> export savu_branch="master" or if you need the latest Savu `release <https://github.com/DiamondLightSource/Savu/releases>`_ to be installed do >>> export savu_branch="savu_version"
4. Set the name of the facility, e.g. *export facility='facility_name'*
5. >>> bash savu_installer/savu_installer.sh
6. Check the log file /tmp/<tmpfolder>/savu_error_log.txt for installation errors (correct log file path printed to screen during installation process).

**Installation of *Savu* HPC at Diamond Light Source (DLS) systems (fastest)**

*This is the fastest installation which uses pre-built against openmpi packages _mpi4py, hdf5, h5py_ from the savu-dep conda channel.*

1. Do 1-3 steps as above.
2. >>> export explicit_file='savu_list_openmpi4_1_1.txt'
3. >>>`bash savu_installer/savu_installer.sh

**Installation of *Savu* HPC at Diamond Light Source (DLS) systems**

*When the explicit file is not provided then the installer will use *environment.yml* to install additional to pre-built packages. This will be slower than the previous option.*

**Installation for Diamond Light Source (DLS) systems:**

1. Get |savu_installer|
2. >>> bash savu_installer/savu_installer.sh
