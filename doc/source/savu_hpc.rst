Installing Savu for a HPC cluster
=================================

Savu is designed to run on a High Performance Computing cluster.  For optimum 
performance, we recommend a fast network interconnect, such as infiniBand, and 
a high performance parallel filesystem, such as GPFS or Lustre.


Requirements: 
    - An MPI implementation (tested with openmpi 3.1.4)
    

Installation:

1. Ensure that your MPI libraries are can be found in the PATH?

1. Download the latest version of :download:`savu <../../install/savu_hpc/savu_installer/savu_installer.tar.gz>` and extract.

2. Run the following command and follow the installation instructions:

    >>> bash savu_installer/savu_installer.sh


# what does Savu install?


bash and module files.

# if [ ! $test_flag ]; then
# 
#   launcher_path=$(command -v savu_launcher.sh)
#   mpijob_path=$(command -v savu_mpijob.sh)
#   echo -e "\n\n===============================IMPORTANT NOTICES================================"
#   echo -e "If you are installing Savu for cluster use, you will need to update the savu "
#   echo -e "launcher scripts:"
#   echo -e "\n$launcher_path"
#   echo -e "$mpijob_path\n"
#   echo -e "\n\nTo run Savu type 'source $savu_setup' to set relevant paths every time you"
#   echo -e "open a new terminal.  Alternatively, if you are using the Modules system, see"
#   echo -e "$DIR/module_template for an example module file."
#   echo -e "================================================================================\n"


Test the installation:

1. Test Savu on a single core of your local PC:  This tests that Savu and all plugin package dependencies have been installed correctly.

    >> source savu_setup.sh


1. Single-threaded tests: There is an option to run the tests at the end of the
installation process.  To run the tests again type:

    >>> bash savu_installer/savu_installer.sh # how does this know which conda environment to use?  Should I add 'source savu_setup'

2. MPI single node tests:?

3. MPI 


Using Savu:

