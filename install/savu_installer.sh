build_no=100
hdf5_version=1.15.1
h5py_version=2.5.0
mpi4py_version=1.3.1

path=$(python -c "import savu; import os; print os.path.abspath(savu.__file__)")
DIR=${path%/savu/__init__.pyc}
recipes=$DIR'/install/conda-recipes'

#=========================library checking==============================

echo -e "\n============================================================="

# set compiler wrapper
mpicc=$(command -v mpicc)
if ! [ "$mpicc" ]; then
    echo "ERROR: I require mpicc but I can't find it.  Check /path/to/mpi_implementation/bin is in your PATH"
    exit 1
else
    echo "Using mpicc:   " $mpicc
fi

# check anaconda distribution
ana_path=$(command -v anaconda)
if ! [ "$ana_path" ]; then
    echo "ERROR: I require anaconda but I can't find it.  Check /path/to/anaconda/bin is in your PATH."
    exit 1
else
    ana_path=$(python -c "import sys; print sys.prefix")
    echo "Using anaconda:" $ana_path
fi

# check for fftw
CFLAGS=""
LDFLAGS=""
IFS=:
file_base=libfftw?.so
for p in ${LD_LIBRARY_PATH}; do
    file_path=${p}/$file_base
    if [ "x$p" != "x" -a -e $file_path ]; then
        fftwdir=${file_path%/lib/libfftw?.so}
        CFLAGS="$fftwdir/include"
        LDFLAGS="$fftwdir/lib"
        break
    fi
done

if [ "$CFLAGS" ]; then
    echo "Using fftw:    " $fftwdir 
else
    echo "fftw has not been found."
fi

# check for cuda
nvcc=`command -v nvcc`
cuda=${nvcc%/bin/nvcc}
if [ "$cuda" ]; then
    echo "Using cuda:    " $cuda
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

echo "Uninstalling packages..."
conda remove mpi4py h5py hdf5

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


CUDA_ROOT=/path/to/cuda pip install astra-toolbox

echo "Building astra toolbox..."
conda build $recipes/astra
astrabuild=`conda build $recipes/astra --output`

echo "Installing astra toolbox..."
conda install --use-local $astrabuild

echo "Installing xraylib..."
conda install -c tacaswell xraylib

package_list='install/pip_install_package_list.txt'
echo "Installing extra packages through pip..."
pip install -r $package_list

echo
echo "*********************************"
echo "* package installation complete *"
echo "*********************************"


