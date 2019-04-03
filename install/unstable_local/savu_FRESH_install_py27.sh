###################################################################
# This is not a bash script but the list of commands to intiate
# a _local_ installation of packages in conda environment for Savu
# testing. 
###################################################################
# get conda installer 
# wget https://repo.anaconda.com/archive/Anaconda3-2018.12-Linux-x86_64.sh
# chmod +x Anaconda3-2018.12-Linux-x86_64.sh
## install it
# bash Anaconda3-2018.12-Linux-x86_64.sh

#source ~/.bashrc_local2
#create conda env
conda create -n SAVU_py27 python==2.7.15

module load cuda/9.2
module load fftw/3.3.7
module load openmpi/3.0.0   # 2.1.2 # 3.1.3  - do not work
module load cmake

# path to conda recipies for packages
recipes=/scratch/SOFTWARE_TEMP/SAVU/savu_py27_fresh/conda-recipes/
###############################
# some warnings regarding no openmpil libraries in RPATH ? 
echo "Building hdf5..."
#conda uninstall -y -q hdf5 || true
conda build $recipes/hdf5
hdf5build=`conda build $recipes/hdf5 --output`
echo "Installing hdf5..."
conda install -y -q --use-local $hdf5build

pip install mpi4py==3.0.1   
###############################
echo "Building h5py..."
conda uninstall -y -q h5py || true
conda build $recipes/h5py --no-test
h5pybuild=`conda build $recipes/h5py --output`
echo "Installing h5py..."
conda install -y -q --use-local $h5pybuild

###############################
echo "Building xraylib..."
conda build $recipes/xraylib
xraylibbuild=`conda build $recipes/xraylib --output`
echo "Installing xraylib..."
conda install -y -q --use-local $xraylibbuild --no-deps

# install TomoPy
conda install -c conda-forge tomopy --no-deps # 1.4.1
# install ASTRA
conda install -c astra-toolbox/label/dev astra-toolbox # 1.9.0 dev

pip install pyyaml # 5.1 
pip install gnureadline # 6.3.8
pip install pyfftw # 0.11.1
conda install -c conda-forge tifffile # 0.15.1
conda install colorama

# conda install -c david_baddeley nvidia-ml-py  - doesn't work for 3.7, hence
pip install nvidia-ml-py # nvidia-ml-py-375.53.1

conda install -c conda-forge fabio # 0.8.0
conda install -c conda-forge pyfai # 0.17.0
# conda install -y -q -c conda-forge pyfai==0.15.0 --no-deps
conda install -c conda-forge peakutils # 1.3.2
# this wants to install python 2.7
# conda install -c praxes pymca # tifffile dependency which also drags TomoPy with it
# did insead
pip install pymca # 5.4.3





