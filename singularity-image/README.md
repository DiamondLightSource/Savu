# Savu Singularity Recipe

## Motivation

Singularity-containerised applications enjoy the same HPC performance as native runs.  Overheads are negligible, with some runs in fact reportedly performing better run inside the container.  Typically, while disk I/O and network bandwidth are unaffected by containerisation, network latency may suffer from a small overhead.

In the case of Savu, the Singularity HPC benefits result from
 * optimal messaging over high-speed networks, such as Infiniband (IB) or Omni-Path Architecture (OPA);
 * access to an underlying high-performance parallel file system;
 * access to GPU processing.

The preservation of HPC perfomance combined with a relatively easy image manipulation (compared with Docker) makes Singularity uniquely suitable for HPC applications such as Savu.  Up-to-date documentation for Singularity is at [sylabs.io](https://www.sylabs.io/docs/).

Another attraction for using Singularity is that no elevated privileges are needed to run the container, and this makes Singularity particularly suitable for usage in shared data centres.  *sudo* access is needed to create a Singularity image but not to run it.


## Requirements

The Singularity recipe requires the following present on the host linux:
  * an OpenMPI installation;
  * up-to-date Nvidia drivers.

OpenMPI works well with Singularity (recommended) and it is assumed the host-side installation provides support for IB/OPA.  While present outside the container, OpenMPI must also be installed inside the container, also with support for IB/OPA.  A container image is started from the host linux via *mpirun*, thus launching the process management daemon (ORTED) on the host OS.  ORTED launches the Singularity container and then the MPI application within the container, which loads the OpenMPI libraries.  The OpenMPI libraries connect back to ORTED via the Process Management Interface (PMI), allowing the containerised processes to run as they would normally directly on the host.  The entire process takes places behind the scenes, and from the user’s perspective running the container is as simple as running a normal MPI application on the host.

Nvidia GPU processing makes use the Singularity flag *--nv*, which ensures the Nvidia driver libraries on the host system are bind mounted into the container at runtime.  Thus, the container only has to have CUDA installed and not the drivers, which makes the Singularity image portable.


## Recipe

### Nvidia Dockerhub images
Installing CUDA inside the container is possible using the CUDA installer directly but past experience has revealed problems, although Nvidia's installation instructions were followed.  For this reason, and not only, it is easier to start building the Singularity image from an existing Docker image with CUDA already installed from [github](https://github.com/NVIDIA/nvidia-docker/wiki/CUDA).  Because CUDA programs are later compiled as part of installing Savu, *devel* version of the images are used.

The recipe is based on Centos 7 because the subsequent installation of Infiniband software stack is easy.

### Message passing over high-speed network
A basic requirement for message passing over high-speed network is the installation of a number of libraries, of which the most important is the the *ibverbs*.  These libraries are later used to build OpenMPI inside the container, so that the application message passing is optimised for high-speed networks.  In Centos 7, these libraries are *yum*-installable as group "Infiniband", making the installation task very easy.  Naturally, optimal IB/OPA transport must supported by OpenMPI on the host linux too in order for the recipe to work well.

The bulk of the testing around Singularity has confirmed this approach supports Mellanox network adaptors well and containerised message passing is for all practical purposes as well performing as native runs.  Preliminary testing has also indicated running a container generated in this way over Omni-Path Architecture works equally well.

Another possible way to support Mellanox architectures is to install the Mellanox OFED software stack (possibly adding the HPC-X software toolkit); there are several Mellanox "community" web pages showing how to do this.  While this approach has the advantage of obtaining the ultimate application performance over IB, this benefit is only reaped at a large scale, _i.e._ with runs on a large enough number of cluster nodes, in other words with runs that are atypical for DLS.  The approach on the other hand is less simple than it sounds (the Mellanox OFED installation is more complicated than a *yum install*) and is certainly not portable to OPA clusters without modifications.


### OpenMPI
The recipe uses OpenMPI 3.0.0, installed with minimal configuration but including *ibverbs* support.  The OpenMPI software stack used to start the container on the host side must be at least this version or newer.

### Generating an image
*sudo* privileges are needed to generate an image.  A command such as the one below would work

```
sudo $(which singularity) build centos-7__savu-2.3__openmpi-3.0.0__cuda-9.0.simg centos-7__savu-2.3__openmpi-3.0.0__cuda-9.0.def
```
The build process takes up to 1:30 hours.  The resulting image size is 2.4GB.


### Running the image
Singularity images are launched by normal users, without elevated privileges.

The basics ingredients for running the Savu Singularity image are
 * Singularity is started via the OpenMPI launcher *mpirun* and
 * processing details (_i.e._ input files) are passed on to the Singularity *runscript* as command line options.

Thus, the launch as part of a cluster job script can look something like this
```
mpirun -np ${NSLOTS} singularity run \
       --bind /mnt/gpfs03/wzp22541/savu/testcases/360-degree:/savu-input,/mnt/gpfs03/wzp22541/savu/runs/360-degree:/savu-output \
       --nv \
       /mnt/gpfs03/wzp22541/savu/singularity/centos-7__savu-2.3__openmpi-3.0.0__cuda-9.0.simg \
       --data-file /savu-input/data/83652.nxs \
       --process-file /savu-input/typical-processing.nxs \
       --output-dir /savu-output/output \
       --folder-name ${JOB_ID} \
       --log-name /savu-output/output/${JOB_ID} \
       --cpus 40 --gpus 4
```

Drilling down into details, the elements of the above command are
 * The OpenMPI *mpirun* is configured on the DLS clusters to integrate with the UGE scheduler, and the only scheduling option passed on to *mpirun* is the overall number of MPI processes (given by the UGE *NSLOTS*), with no host details.
 * Singularity is started with the *run* command option, which runs the shell script in the section *%runsection* in the definition file.  This script takes in a number of command-line arguments, supplied in the command above following the name of the Singularity *.simg* file.  From the shell command line, the script can be inspected with the command *singularity inspect --runscript centos-7__savu-2.3__openmpi-3.0.0__cuda-9.0.simg*.  Running the script without arguments prints help information and aborts.  There are some checks applied to the command line arguments too.
 * Singularity bind mounts the input and output directories into the bind points */savu-input* and */savu-output*, which are created by the recipe.  This provides a mechanism to manage relative complex input/output scenarios, at the same time enjoying the performance of the underlying file system.
 * Singularity is started with the option *--nv*, which bind mounts the Nvidia driver libraries present on the host system into the container at runtime.
 * The command line arguments that follow after the Singularity image file name are familiar to Savu users: data HDF5 file, process list file, etc.  The *--cpus* options is used to indicate the number of MPI processes started on a single host (attention, this is *not* the total number of processes in the case of a multi-node run).  Similarly, *--gpus* sets the number of GPUs scheduled for use on a single host.  Symmetry is assumed, in the sense that all hosts will run the same number of MPI processes and use the same number of GPU cards.  In a UGE job script, these values to pass via the *--cpus* and *--gpus* options can respectively be inferred from
```
savu_num_cpus=${SGE_HGR_exclusive}
savu_num_gpus=$(echo ${SGE_HGR_gpu} | wc -w)
```
