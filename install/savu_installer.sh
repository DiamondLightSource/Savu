facility=$1
savu_env=$2

#hdf5_version=1.8.18
#h5py_version=2.6.0
mpi4py_version=2.0.0

path=$(python -c "import savu; import os; print os.path.abspath(savu.__file__)")
DIR=${path%/savu/__init__.pyc}
recipes=$DIR'/install/conda-recipes'

launcher_path=`command -v savu_launcher.sh`
launcher_path=${launcher_path%/savu_launcher.sh}
if [ "$facility" ]; then
    cp $DIR/mpi/$facility/savu_launcher.sh $launcher_path
    cp $DIR/mpi/$facility/savu_mpijob.sh $launcher_path
fi

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
conda remove mpi4py
conda remove h5py
conda remove hdf5
pip uninstall mpi4py astra-toolbox xraylib
pip uninstall -r $package_list

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

astra_init_path=$(python -c "import site; print site.getsitepackages()[0]")/astra/__init__.py
mv $recipes/astra/start_up_script.py $astra_init_path

echo "Building xraylib..."
conda build $recipes/xraylib
xraylibbuild=`conda build $recipes/xraylib --output`

echo "Installing xraylib..."
conda install --use-local $xraylibbuild

echo "Installing tomopy..."
conda install -c dgursoy tomopy
# revert back to MPI version of HDF5
conda install --use-local $hdf5build

package_list=$recipes'/../pip_install_package_list.txt'
echo "Installing extra packages through pip..."
pip install -r $package_list

echo
echo "*********************************"
echo "* package installation complete *"
echo "*********************************"

