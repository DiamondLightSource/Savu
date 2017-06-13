#!/bin/bash -ex

# error log to screen and file
error_log=/tmp/savu_error_log.txt
exec 2> >(tee -ia $error_log)

oldprompt=$PS1
newprompt=">>> "
export PS1=$newprompt

for sig in INT TERM EXIT; do
    trap "export PS1=$oldprompt; [[ $sig == EXIT ]] || kill -$sig $$" $sig
done

PREFIX=$HOME
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
savu_version=`cat $DIR/version.txt`

# might want to change this
if [ $# -gt 0 ]; then
  facility=$1
else
  facility=dls
fi

#=========================library checking==============================

echo -e "\n============================================================="
echo -e "    ......Thank you for running the Savu installer......\n"

echo -e "Performing a library check..."
echo -e "\nNB: An MPI implementation is required to build Savu."
echo -e "fftw and cuda are desirable for a full range of plugins."

echo -e "\n============================================================="

# set compiler wrapper
mpicc=$(command -v mpicc)
if ! [ "$mpicc" ]; then
    echo "ERROR: I require mpicc but I can't find it.  Check /path/to/mpi_implementation/bin is in your PATH"
    exit 1
else
    echo "Using mpicc:   " $mpicc
fi

# check for fftw
CFLAGS=""
LDFLAGS=""
IFS=:
file_base=libfftw?.so
for p in ${LD_LIBRARY_PATH}; do
    file_path=${p}/$file_base
    if [ "x$p" != "x" -a -e $file_path ]; then
        FFTWHOME=${file_path%/lib/libfftw?.so}
        CFLAGS="$FFTWHOME/include"
        LDFLAGS="$FFTWHOME/lib"
        break
    fi
done

if [ "$CFLAGS" ]; then
    echo "Using fftw:    " $FFTWHOME
else
    echo "fftw has not been found."
fi

# check for cuda
nvcc=`command -v nvcc`
CUDAHOME=${nvcc%/bin/nvcc}
if [ "$CUDAHOME" ]; then
    echo "Using cuda:    " $CUDAHOME
    CUDAHOME="$(dirname $CUDAHOME)"
else
    echo "cuda has not been found."
fi

echo -e "=============================================================\n"

read  -n 1 -p "Are you happy to proceed with the installation? (y/n): " input
if [ "$input" = "y" ]; then
    echo -e "\nYour input was yes"
elif [ "$input" = "n" ]; then
    echo -e "\nInstallation process terminated."
    exit 1
else
    echo -e "\nYour input was unknown.\n"
    read  -n 1 -p "Are you happy to proceed with the installation? (y/n): " input
fi   
#=====================installing other packages==========================


echo -e "\nInstalling Savu in" $PREFIX
read  -p ">>> Press ENTER to continue or input a different path: " input

if [ "$input" != "" ]; then
    PREFIX=$input
fi

while true; do
  if [ -d "$PREFIX" ]; then
    PREFIX=$PREFIX/Savu_$savu_version/
    break
  fi
  echo "The path" $PREFIX "is not recognised"
  read  -p ">>> Please input a different installation path: " input
  PREFIX=$input
done

# what if this folder already exists.
if [ -d "$PREFIX" ]; then
  echo
  read -n 1 -p "The folder $PREFIX already exists. Continue? [y/n]" input
  if [ "$input" = "y" ]; then
    echo -e "\nStarting the installation........"
  elif [ "$input" = "n" ]; then
    echo -e "\nInstallation process terminated."
    exit 1
  else
    echo -e "\nYour input was unknown.\n\n"
    read -n 1 -p -e "The folder" $PREFIX "already exists. Continue? [y/n]" input
  fi
else
  # create the folder
  mkdir -p $PREFIX
fi

echo -e "\nThank you!  Installing Savu into" $PREFIX"\n"

echo $PREFIX

wget https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh -O $PREFIX/miniconda.sh;
bash $PREFIX/miniconda.sh -b -p $PREFIX/miniconda
PYTHONHOME=$PREFIX/miniconda/bin
export PATH=$PYTHONHOME:$PATH

echo
conda info | grep 'root environment'
echo

conda env update -n root -f $DIR/environment.yml

# check anaconda distribution
ana_path=$(command -v anaconda)
if ! [ "$ana_path" ]; then
    echo "ERROR: I require anaconda but I can't find it.  Check /path/to/anaconda/bin is in your PATH."
    exit 1
else
    ana_path=$(python -c "import sys; print sys.prefix")
    echo "Using anaconda:" $ana_path
fi

# conda install savu
conda install -c savu savu=$version

facility=$1

path=$(python -c "import savu; import os; print os.path.abspath(savu.__file__)")
DIR=${path%/savu/__init__.pyc}

if [[ ! -z "${RECIPES}" ]]; then
    recipes=`echo $RECIPES`
else
    recipes=$DIR'/install/conda-recipes'
fi

launcher_path=`command -v savu_launcher.sh`
launcher_path=${launcher_path%/savu_launcher.sh}
if [ "$facility" ]; then
    cp $DIR/mpi/$facility/savu_launcher.sh $launcher_path
    cp $DIR/mpi/$facility/savu_mpijob.sh $launcher_path
fi

mpi4py_version=`cat $recipes/mpi4py/version.txt`

echo "Installing mpi4py..."
env MPICC=$mpicc pip install mpi4py==$mpi4py_version

echo "Building hdf5..."
conda build $recipes/hdf5
hdf5build=`conda build $recipes/hdf5 --output`

echo "Installing hdf5..."
conda install --use-local $hdf5build

echo "Building h5py..."
conda build $recipes/h5py --no-test
h5pybuild=`conda build $recipes/h5py --output`

echo "Installing h5py..."
conda install --use-local $h5pybuild

echo "Building astra toolbox..."
conda build $recipes/astra
astrabuild=`conda build $recipes/astra --output`

echo "Installing astra toolbox..."
conda install --use-local $astrabuild

site_path=$(python -c "import site; print site.getsitepackages()[0]")
cp $recipes/astra/astra.pth $site_path
astra_lib_path=$site_path/astra/lib

echo "Building xraylib..."
conda build $recipes/xraylib
xraylibbuild=`conda build $recipes/xraylib --output`

echo "Installing xraylib..."
conda install --use-local $xraylibbuild

echo "Installing ccpi-reconstruction"
conda install –c ccpi ccpi-reconstruction –c conda-forge

if [ "$CUDAHOME" ]; then
  pip install pycuda
fi

echo
echo "*********************************"
echo "* package installation complete *"
echo "*********************************"
echo 
echo "Check the log file $error_log for any installation errors\n".


echo -e "Adding "$astra_lib_path" to LD_LIBRARY_PATH"
export LD_LIBRARY_PATH=$astra_lib_path:$LD_LIBRARY_PATH

# automatically run the tests
source test_setup.sh

setup_script=$DIR/savu_setup.sh
echo -e "\nCreating a Savu setup script" $setup_script
( [ -e "$setup_script" ] || touch "$setup_script" ) && [ ! -w "$setup_script" ] && echo cannot write to $setup_script && exit 1
MPIHOME="$(dirname "$(dirname $MPICC)")"
echo ""export PATH=$MPIHOME/bin:'$PATH'"" > $setup_script
echo ""export LD_LIBRARY_PATH=$MPIHOME/lib:'$LD_LIBRARY_PATH'"" >> $setup_script
echo ""export PYTHONUSERSITE True"" >> $setup_script
echo ""export PATH=$PYTHONHOME/bin:'$PATH'"" >> $setup_script
echo ""export LD_LIBRARY_PATH=$PYTHONHOME/lib:'$LD_LIBRARY_PATH'"" >> $setup_script
echo ""export LD_LIBRARY_PATH=$astra_lib_path:'$LD_LIBRARY_PATH'"" >> $setup_script
if [ "$CUDAHOME" ]; then
  echo ""export PATH=$CUDAHOME/bin:'$PATH'"" >> $setup_script
  echo ""export LD_LIBRARY_PATH=$CUDAHOME/lib:'$LD_LIBRARY_PATH'"" >> $setup_script
fi
if [ "$FFTWHOME" ]; then
  echo ""export FFTWDIR=$FFTWHOME"" >> $setup_script
  echo ""export LD_LIBRARY_PATH=$FFTWHOME/lib:'$LD_LIBRARY_PATH'"" >> $setup_script
fi

nGPUs=$(python -c "import savu.core.utils as cu; p, count = cu.get_available_gpus(); print count")

source $setup_script

echo -e "\nTesting Savu setup....."
savu_quick_tests

echo -e "\nRunning Savu single-threaded local tests (this may take a while)....."
savu_full_tests

echo "************** Single-threaded local tests complete ******************"

# can the savu_mpi_local tests be auto-mated?
echo -e "\nRunning Savu MPI local cpu tests....."
local_mpi_cpu_test.sh

if [ $nGPUs -gt 0 ]; then
  echo -e "\nRunning Savu MPI local gpu tests....."
  # if gpus are found then run the gpu tests else print a message saying they are skipped
  local_mpi_gpu_test.sh
fi

echo "************** MPI local tests complete ******************"


read  -n 1 -p "Are you installing Savu for cluster use? (y/n): " input
if [ "$input" = "y" ]; then
    echo -e "To run Savu across a cluster you will need to update the savu laucher scripts:"
    echo -e "savu_launcher.sh"
    echo -e "savu_mpijob.sh"
    
elif [ "$input" = "n" ]; then
    continue
else
    echo -e "\nYour input was unknown.\n"
    read  -n 1 -p "Are you happy to proceed with the installation? (y/n): " input
fi   


echo -e "\nTo run Savu type 'source $savu_setup' to set relevant paths every time you open a new terminal."
echo -e "Alternatively, if you are using the Modules system, see $DIR/module_template for an example module file." 


echo -e "*************** SAVU INSTALLATION COMPLETE! ******************\n"
echo -e "    ......Thank you for running the Savu installer......\n"
echo -e "=============================================================\n"

# have a look at .... for the list of instructions above. (inside the downloaded folder).
# Create a README.txt inside Savu/install/savu_install/README.txt

#path_remove ()  { export PATH=`echo -n $PATH | awk -v RS=: -v ORS=: '$0 != "'$1'"' | sed 's/:$//'`; }

