Installing Savu for a HPC cluster
=================================

Savu is designed to run on a High Performance Computing cluster.  For optimum 
performance, we recommend a fast network interconnect, such as infiniBand, and 
a high performance parallel filesystem, such as GPFS or Lustre.


Requirements: 
    - An MPI implementation (tested with openmpi 3.1.4)

Installation:

1. Download the latest version of :download:`savu <../../install/savu_hpc/savu_installer.tar.gz>` and extract.

2. Run the following command and follow the installation instructions:

    >>> bash savu_installer/savu_installer.sh

3. Check the log file /tmp/<tmpfolder>/savu_error_log.txt for installation errors (correct log file path printed to screen during installation process).

