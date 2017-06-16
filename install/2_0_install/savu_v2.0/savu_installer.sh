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

# function for parsing optional arguments
function arg_parse ()
{
  flag=$1
  return=$2
  while [[ $# -gt 3 ]] ; do
    if [ $3 == $flag ] ; then
      eval "$return"=$4
    fi
    shift
  done
}

# set the intermediate folder
arg_parse "-f" facility "$@"
if [ ! $facility ] ; then
  facility=dls # change this default?
fi

export FACILITY=$facility

# set the intermediate folder
arg_parse "-c" conda_folder "$@"
if [ ! $conda_folder ] ; then
  conda_folder=Savu_$savu_version
fi

# set the intermediate folder
arg_parse "-s" savu_recipe "$@"
if [ ! $savu_recipe ] ; then
  savu_recipe=savu
elif [ $savu_recipe = 'master' ] ; then
  savu_recipe=savu_master
else
  echo "Unknown Savu installation version."
fi

#=========================library checking==============================

echo -e "\n============================================================="
echo -e "    ......Thank you for running the Savu installer......\n"

echo -e "Performing a library check..."
echo -e "\nNB: An MPI implementation is required to build Savu."
echo -e "fftw and cuda are desirable for a full range of plugins."

echo -e "\n============================================================="

# set compiler wrapper
MPICC=$(command -v mpicc)
if ! [ "$MPICC" ]; then
    echo "ERROR: I require mpicc but I can't find it.  Check /path/to/mpi_implementation/bin is in your PATH"
    exit 1
else
    echo "Using mpicc:   " $MPICC
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
    PREFIX=$PREFIX/$conda_folder/
    break
  fi
  echo "The path" $PREFIX "is not recognised"
  read  -p ">>> Please input a different installation path: " input
  PREFIX=$input
done

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
export PATH="$PYTHONHOME:$PATH"

echo
conda info | grep 'root environment'
echo

conda env update -n root -f $DIR/environment.yml

echo "Building Savu..."
conda build $DIR/$savu_recipe
savubuild=`conda build $DIR/$savu_recipe --output`
echo "Installing Savu..."
conda install --use-local $savubuild

path=$(python -c "import savu; import os; print os.path.abspath(savu.__file__)")
savu_path=${path%/savu/__init__.pyc}

# get the savu version
install_path=$(python -c "import savu; import savu.version as sv; print sv.__install__")
recipes=$savu_path/$install_path/conda-recipes

launcher_path=`command -v savu_launcher.sh`
launcher_path=${launcher_path%/savu_launcher.sh}
if [ "$facility" ]; then
    cp $savu_path/mpi/$facility/savu_launcher.sh $launcher_path
    cp $savu_path/mpi/$facility/savu_mpijob.sh $launcher_path
fi

mpi4py_version=`cat $recipes/mpi4py/version.txt`
mpi4py_version=1.3.1

echo $mpi4py_version

echo "Installing mpi4py..."
env MPICC=$MPICC pip install mpi4py==$mpi4py_version

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

echo "Installing tomopy..."
conda install -c dgursoy tomopy
# revert back to MPI versions of HDF5 and h5py
conda install --use-local $hdf5build
conda install --use-local $h5pybuild

echo "Installing ccpi-reconstruction..."
conda install -c ccpi ccpi-reconstruction -c conda-forge

# pycuda not working add this later?
#if [ "$CUDAHOME" ] ; then
#  pip install pycuda
#fi

# update to pyqt5?

echo -e "\n\t***************************************************"
echo -e "\t*          Package installation complete          *"
echo -e "\t*    Check $error_log for errors     *"
echo -e "\t***************************************************\n"

# automatically run the tests
source test_setup.sh > /dev/null # not available yet

setup_script=$PREFIX'savu_setup.sh'
echo -e "\nCreating a Savu setup script" $setup_script
( [ -e "$setup_script" ] || touch "$setup_script" ) && [ ! -w "$setup_script" ] && echo cannot write to $setup_script && exit 1
MPIHOME="$(dirname "$(dirname $MPICC)")"
echo "#!bin/bash" > $setup_script
echo ""export PATH=$MPIHOME/bin:'$PATH'"" >> $setup_script
echo ""export LD_LIBRARY_PATH=$MPIHOME/lib:'$LD_LIBRARY_PATH'"" >> $setup_script
echo ""export PYTHONUSERSITE True"" >> $setup_script
echo ""export PATH=$PYTHONHOME:'$PATH'"" >> $setup_script
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

echo $(python -c "import savu; savu.__file__")
nGPUs=$(python -c "import savu.core.utils as cu; p, count = cu.get_available_gpus(); print count")

source $setup_script

echo -e "\n***** Testing Savu setup *****\n"
savu_quick_tests

echo -e "\n*****Running Savu single-threaded local tests *****\n"
savu_full_tests

echo -e "\n************** Single-threaded local tests complete ******************\n"

echo -e "\n***** Running Savu MPI local CPU tests *****\n"
local_mpi_cpu_test.sh

if [ $nGPUs -gt 0 ]; then
  echo -e "\n***** Running Savu MPI local GPU tests *****\n"
  local_mpi_gpu_test.sh
else
  echo -e "\n***** Skipping Savu MPI local GPU tests (no GPUs found) *****\n"
fi

echo -e "\n************** MPI local tests complete ******************\n"


#while true
#do
#  read  -n 1 -p "Are you installing Savu for cluster use? (y/n): " input
#  if [ "$input" = "y" ]; then
#    echo -e "To run Savu across a cluster you will need to update the savu laucher scripts:"
#    echo -e "savu_launcher.sh"
#    echo -e "savu_mpijob.sh"
#    break    
#  elif [ "$input" = "n" ]; then
#    echo -e "\nYour input was unknown.\n"
#    continue
#  fi
#done   


# what about an example module file?  OR source savu_setup instead (adding the paths from savu_setup).
echo -e "\nTo run Savu type 'source $savu_setup' to set relevant paths every time you open a new terminal."
echo -e "Alternatively, if you are using the Modules system, see $DIR/module_template for an example module file." 

echo -e "*************** SAVU INSTALLATION COMPLETE! ******************\n"
echo -e "    ......Thank you for running the Savu installer......\n"
echo -e "=============================================================\n"

# have a look at .... for the list of instructions above. (inside the downloaded folder).
# Create a README.txt inside Savu/install/savu_install/README.txt

