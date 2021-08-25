## Installation of *Savu*
If you need a PC installation, see *Savu-lite* installation guide bellow and for High Performance Computing (HPC) installation, see *Savu* HPC.

### Requirements:
Unix operating system is required for *Savu* installation. For *Savu* HPC one needs an [openMPI](https://www.open-mpi.org/) library installed.

### *Savu-lite* installation
*Savu-lite* is designed to run on a local PC workstation. The main functionality of *Savu* is preserved with *Savu-lite* except the MPI part.
Currently *Savu-lite* is built for Python 3.7 with Numpy 1.15. To install it you'll need a clean conda environment.

#### 1a: Installation of *Savu-lite* from the savu-dep conda channel
Probably the easiest method since you'll be installing the pre-built version from the conda channel.
1. Install miniconda (preferably 4.6.14 which comes with Python 3.7) and activate it
2. `conda create -n savu`
3. `conda activate savu`
4. `conda install savu-lite -c conda-forge -c savu-dep -c ccpi -c astra-toolbox/label/dev`
This will install *Savu-lite* into your Savu environment with all dependencies.

#### 1b: Installation of *Savu-lite* using the explicit list of packages
This method requires cloning the repository and then installing all the dependencies from the explicit list. Then *Savu-lite* is installed into the environment.
1. Get the explicit list file from [HERE](https://github.com/DiamondLightSource/Savu/blob/master/install/savu_lite37/spec-savu_lite_latest.txt)
2. `conda install --yes --name savu --file spec-savu_lite_latest.txt`
3. From the main Savu folder run `python setup.py install`

### *Savu* HPC installation
To install this version of Savu you will need an HPC cluster with a fast network interconnect, such as infiniBand, and
a high performance parallel filesystem, such as GPFS or Lustre. Additionally you'll need an [openMPI](https://www.open-mpi.org/) library installed.

#### 2a: Installation of *Savu* HPC _outside_ Diamond Light Source (DLS) systems
1. Check that you do *NOT* have conda in your path with `which conda`. Note that the installer will install its own version of conda so it is essential that conda is not in the path.
2. Download the [INSTALLER](https://github.com/DiamondLightSource/Savu/blob/master/install/savu_hpc/savu_installer.tar.gz)
3. Set the desired Github branch of Savu to install. E.g. if you need to install the latests changes in Savu, you can select the "master" branch as  `export savu_branch="master"` or if you need the _latest_ Savu [release](https://github.com/DiamondLightSource/Savu/releases) to be installed do `export savu_branch="savu_version"`
4. Set the name of the facility, as: `export facility="facility_name"`
5. `bash savu_installer/savu_installer.sh` and follow installation instructions

#### 2b: Installation of *Savu* HPC at Diamond Light Source (DLS) systems (fastest)
This is the fastest installation which uses pre-built against openmpi packages _mpi4py, hdf5, h5py_ from the [savu-dep](https://anaconda.org/savu-dep) conda channel.
1. Do 1-3 steps as in *2a*.
2. `export explicit_file="savu_list_openmpi4_1_1.txt"`
3. `bash savu_installer/savu_installer.sh` and follow installation instructions

#### 2c: Installation of *Savu* HPC at Diamond Light Source (DLS) systems
When the `explicit_file` is not provided then the installer will use _environment.yml_ to install additional to pre-built packages. This will be slower than the *2b* option.

##### Contact:
Please send your questions to scientificsoftware@diamond.ac.uk
