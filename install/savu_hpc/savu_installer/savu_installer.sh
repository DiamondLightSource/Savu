#!/bin/bash -ex

set -e
# change to 'latest' for the latest version
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
versions_file=$DIR/versions_file.txt

# error log to screen and file
log_temp=$(mktemp -d)
error_log=$log_temp/savu_error_log.txt
exec 2> >(tee -ia $error_log)

oldprompt=$PS1
newprompt=">>> "
export PS1=$newprompt

for sig in INT TERM EXIT; do
  trap "export PS1=$oldprompt; [[ $sig == EXIT ]] || kill -$sig $$" $sig
done

PREFIX="${PREFIX:-$HOME}"

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# get version from the version file in base of savu
export savu_version=$(cat $DIR/version.txt)
# dealing with a case when a branch name passed as savu_version
if [ "$savu_version" != "master" ]; then
  export savu_version="v$savu_version"
fi
echo "--> Savu version has passed as $savu_version" | xargs

# function for parsing optional arguments
function arg_parse() {
  flag=$1
  return=$2
  while [[ $# -gt 2 ]]; do
    if [ $3 == $flag ]; then
      eval "$return"=$4
    fi
    shift
  done
}

# function for parsing flags without arguments
function flag_parse() {
  flag=$1
  return=$2
  while [[ $# -gt 2 ]]; do
    if [ $3 == $flag ]; then
      eval "$return"=true
    fi
    shift
  done
}


# Set the test flag to true if test only
flag_parse "--tests_only" test_flag "$@"
if [ $test_flag ]; then
  test_flag=true
fi


# Set the prompts flag to false if no prompts are required
flag_parse "--no_prompts" prompts "$@"
if [ $prompts ]; then
  prompts=false
else
  prompts=true
fi

# set the facility
arg_parse "-f" facility "$@"
if [ ! $facility ]; then
  facility=dls # change this default?
fi

export FACILITY=$facility

# set the explicit file
arg_parse "-f" explicit_file "$@"
if [ ! $explicit_file ]; then
  explicit_file=false
fi
export EXPLICIT_FILE=$explicit_file

# set the conda folder
arg_parse "-c" conda_folder "$@"
if [ ! $conda_folder ]; then
  conda_folder=Savu_$savu_version
fi

# set the branch from which install savu
arg_parse "-s" savu_branch "$@"
# by default the savu branch is "master", if the version branch is required then
# do: export savu_branch="savu_version"
if [ ! $savu_branch ]; then
  savu_branch="master"
fi
if [ "$savu_branch" == "savu_version" ]; then
  savu_branch=$savu_version
fi

# override the conda recipes folder
arg_parse "-r" recipes "$@"
#=========================library checking==============================


if [ $test_flag ]; then
  echo -e "\n============================================================="
  echo -e "    ......Thank you for running the Savu tests......\n"
  echo -e "Performing a library check..."
else
  echo -e "\n============================================================="
  echo -e "    ......Thank you for running the Savu installer......\n"
  echo -e "Performing a library check..."
  echo -e "\nNB: An MPI implementation is required to build Savu."
  #echo -e "Cuda is desirable for a full range of plugins."
  echo -e "\n============================================================="
fi

if [ $facility = dls ]; then
  echo "Proceed with the DLS-specific installation and will use locally installed openmpi..." | xargs
else
  echo -e "Proceed with $facility installation and will attempt to use the pre-installed openmpi."
  echo -e "If a PC (non-MPI) installation is required, then install Savu-lite in a new Python 3.7 conda environment using the command:"
  echo -e "conda install savu-lite -c conda-forge -c savu-dep -c ccpi -c astra-toolbox/label/dev"
fi

# set compiler wrapper
MPICC=$(command -v mpicc)
MPI_HOME=${MPICC%/mpicc}
if ! [ "$MPICC" ]; then
  echo "ERROR: I require mpicc but I can't find it.  Check /path/to/mpi_implementation/bin is in your PATH"
  exit 1
else
  echo "Using mpicc:   " $MPICC
  export PATH=$MPI_HOME:$PATH
  openmpi_ver_string=$(mpicxx --showme:version)
  export openmpi_version=$(echo $openmpi_ver_string | sed -ne 's/[^0-9]*\(\([0-9]\.\)\{0,4\}[0-9][^.]\).*/\1/p')
  echo "Proceed with $openmpi_version version" | xargs
fi

# # check for cuda
# nvcc=`command -v nvcc`
# CUDAHOME=${nvcc%/bin/nvcc}
# if [ "$CUDAHOME" ]; then
#     echo "Using cuda:    " $CUDAHOME
# 	export PATH=$CUDAHOME/bin:$PATH
# 	export LD_LIBRARY_PATH=$CUDAHOME/lib64:$LD_LIBRARY_PATH
# else
#     echo "No cuda libraries found."
# fi

if [ $test_flag ] && [ $prompts = true ]; then

  PYTHONHOME=$(command -v conda)
  PYTHONHOME=${PYTHONHOME%conda}
  if [ ! $PYTHONHOME ]; then
    echo -e "No conda environment found in PATH. Try:"
    echo -e "   >>> source <path_to_savu_installation>/savu_setup.sh"
    echo -e "Aborting the tests."
    exit 1
  fi

  echo -e "=============================================================\n"
  while true; do
    read -n 1 -p "Are you happy to proceed with the tests? (y/n): " input
    if [ "$input" = "y" ]; then
      echo -e "\nProceeding with the tests."
      break
    elif [ "$input" = "n" ]; then
      echo -e "\nAborting the tests."
      exit 0
    else
      echo -e "\nYour input was unknown.\n"
    fi
  done
elif [ $prompts = true ]; then
  echo -e "=============================================================\n"
  while true; do
    read -n 1 -p "Are you happy to proceed with the installation? (y/n): " input
    if [ "$input" = "y" ]; then
      echo -e "\nYour input was yes"
      break
    elif [ "$input" = "n" ]; then
      echo -e "\nInstallation process terminated."
      exit 0
    else
      echo -e "\nYour input was unknown.\n"
    fi
  done

  #=====================installing other packages==========================

  echo -e "\nInstalling Savu in" $PREFIX
  read -p ">>> Press ENTER to continue or input a different path: " input

  if [ "$input" != "" ]; then
    PREFIX=$input
  fi

  while true; do
    if [ -d "$PREFIX" ]; then
      PREFIX=$PREFIX/$conda_folder/
      break
    fi
    echo "The path" $PREFIX "is not recognised"
    read -p ">>> Please input a different installation path: " input
    PREFIX=$input
  done

  if [ -d "$PREFIX" ]; then
    echo
    while true; do
      read -n 1 -p "The folder $PREFIX already exists. Continue? [y/n]" input
      if [ "$input" = "y" ]; then
        echo -e "\nStarting the installation........"
        break
      elif [ "$input" = "n" ]; then
        echo -e "\nInstallation process terminated."
        exit 0
      else
        echo -e "\nYour input was unknown.\n\n"
      fi
    done
  else
    # create the folder
    mkdir -p $PREFIX
  fi
else
  if [ ! -d "$PREFIX" ]; then
    mkdir -p $PREFIX
  fi
fi


if [ ! $test_flag ]; then

  echo -e "\nThank you!  Installing Savu into" $PREFIX"\n"

  unset IFS
  string=$(awk '/^miniconda/' $versions_file)
  miniconda_version=$(echo $string | cut -d " " -f 2)

  wget https://repo.continuum.io/miniconda/Miniconda3-$miniconda_version-Linux-x86_64.sh -O $PREFIX/miniconda.sh

  bash $PREFIX/miniconda.sh -b -p $PREFIX/miniconda
  PYTHONHOME=$PREFIX/miniconda/bin
  export PATH="$PYTHONHOME:$PATH"

  conda install -y -q conda-build

  echo -e "=============================================================\n"
  echo "Building Savu..."
  conda build $DIR/savu-recipe
  savubuild=`conda build $DIR/savu-recipe --output`
  echo -e "=============================================================\n"
  echo "Installing Savu..."
  conda install -y -q --use-local $savubuild

  path=$(python -c "import savu; import os; print(os.path.abspath(savu.__file__))")
  savu_path=${path%/savu/__init__.py*}

  # get the savu version
  if [ -z $recipes ]; then
    install_path=$(python -c "import savu; import savu.version as sv; print(sv.__install__)")
    recipes=$savu_path/$install_path/../conda-recipes
  fi

  # getting versions of mpi4py/hdf5/h5py from the versions file
  string=$(awk '/^mpi4py/' $versions_file)
  mpi4py_version=$(echo $string | cut -d " " -f 2)
  string=$(awk '/^hdf5/' $versions_file)
  hdf5_version=$(echo $string | cut -d " " -f 2)
  string=$(awk '/^h5py/' $versions_file)
  h5py_version=$(echo $string | cut -d " " -f 2)

  if [ $facility = dls ]; then

    if [ $EXPLICIT_FILE = false ]; then
    echo "Installing mpi4py from savu-dep conda channel"
    export VERSION_BUILD_MPI4PI=$mpi4py_version"_openmpi_"$openmpi_version
    conda install --yes -c savu-dep mpi4py=$VERSION_BUILD_MPI4PI --no-deps

    echo "Installing hdf5 from savu-dep conda channel"
    export VERSION_BUILD_HDF5=$hdf5_version"_openmpi_"$openmpi_version
    conda install -y -c savu-dep hdf5=$VERSION_BUILD_HDF5 --no-deps

    echo "Installing h5py from savu-dep conda channel"
    export VERSION_BUILD_H5PY=$h5py_version"_mpi4pi_"$mpi4py_version"_hdf5_"$VERSION_BUILD_HDF5
    conda install -y -c savu-dep h5py=$VERSION_BUILD_H5PY --no-deps

    echo "Installing cudatoolkit and pytorch..."
    string=$(awk '/^cudatoolkit/' $versions_file)
    cudatoolkit_version=$(echo $string | cut -d " " -f 2)
    conda install -y -q pytorch torchvision cudatoolkit=$cudatoolkit_version -c pytorch

    export PACKAGE=cudatoolkit
    string=$(awk '/^cudatoolkit/' $versions_file)
    cudatoolkit_version=$(echo $string | cut -d " " -f 2)
    export VER_PACKAGE=$cudatoolkit_version
    conda list $PACKAGE > check_conda_package.txt
      if grep -q $VER_PACKAGE check_conda_package.txt; then
          echo -e "\nPackage $PACKAGE of v.$VER_PACKAGE is found in Savu's environment, continue with installation..."
          rm -f check_conda_package.txt
      else
          echo -e "\nPackage $PACKAGE of v.$VER_PACKAGE is NOT found in Savu's environment! \nInstallation process terminated!"
          rm -f check_conda_package.txt
          exit 0
      fi
    conda env update -n root -f $DIR/environment.yml
    else
      echo "Installing all required packages from the explicit file $EXPLICIT_FILE" | xargs
      conda update -n root --file $DIR/explicit_lists/$EXPLICIT_FILE
    fi
  else
    echo "Installation for $facility has been chosen, installing packages from the explicit list first" | xargs
    conda update -n root --file $DIR/explicit_lists/savu_explicit_packages.txt

    echo "Installing mpi4py from the recipe"
    export VERSION_MPI4PY=$mpi4py_version
    export VERSION_BUILD_MPI4PY=$mpi4py_version"_openmpi_"$openmpi_version
    . $recipes/installer.sh "mpi4py" $VERSION_BUILD_MPI4PY

    echo "Installing hdf5 from the recipe"
    export hdf5_XYZ_version=$hdf5_version
    export PATCH_HDF="hdf5-"$hdf5_version
    export RELEASE_HDF=${PATCH_HDF%.*}
    export VERSION_BUILD_HDF5=$hdf5_version"_openmpi_"$openmpi_version
    . $recipes/installer.sh "hdf5" $VERSION_BUILD_HDF5

    echo "Installing h5py from the recipe"
    export VERSION_H5PY=$h5py_version
    export VERSION_BUILD_H5PY=$h5py_version
    . $recipes/installer.sh "h5py" $VERSION_BUILD_H5PY
  fi

  # cleanup build artifacts
  rm $PREFIX/miniconda.sh

  conda build purge
  conda clean -y --all

  echo -e "\n\t***************************************************"
  echo -e "\t          Package installation complete"
  echo -e "\t  Check $error_log for errors"
  echo -e "\t***************************************************\n"

fi

if [ ! $test_flag ]; then
  if [ $prompts = true ]; then
    while true; do
      read -n 1 -p "Would you like to run the tests? (y/n): " input
      if [ "$input" = "y" ]; then
        echo -e "\nYour input was yes"
        test_flag=true
        break
      elif [ "$input" = "n" ]; then
        echo -e "Aborting test run..."
        echo -e "To run the tests later type: "
        echo -e "   >>> bash savu_installer/savu_installer.sh --tests_only"
        exit 0
      else
        echo -e "\nYour input was unknown.\n"
      fi
    done
  fi

  setup_script=$PREFIX/'savu_setup.sh'
  echo -e "\nCreating a Savu setup script" $setup_script
  ([ -e "$setup_script" ] || touch "$setup_script") && [ ! -w "$setup_script" ] && echo cannot write to $setup_script && exit 1
  MPIHOME="$(dirname "$(dirname $MPICC)")"
  echo '#!bin/bash' >$setup_script
  echo ""export PATH=$MPIHOME/bin:'$PATH'"" >>$setup_script
  echo ""export LD_LIBRARY_PATH=$MPIHOME/lib:'$LD_LIBRARY_PATH'"" >>$setup_script
  echo ""export PYTHONUSERSITE True"" >>$setup_script
  echo ""export PATH=$PYTHONHOME:'$PATH'"" >>$setup_script
  echo ""export LD_LIBRARY_PATH=$PYTHONHOME/lib:'$LD_LIBRARY_PATH'"" >>$setup_script
  echo ""export LD_LIBRARY_PATH=$astra_lib_path:'$LD_LIBRARY_PATH'"" >>$setup_script
  if [ "$CUDAHOME" ]; then
    echo ""export PATH=$CUDAHOME/bin:'$PATH'"" >>$setup_script
    echo ""export LD_LIBRARY_PATH=$CUDAHOME/lib64:'$LD_LIBRARY_PATH'"" >>$setup_script
  fi
  if [ "$FFTWHOME" ]; then
    echo ""export FFTWDIR=$FFTWHOME"" >>$setup_script
    echo ""export LD_LIBRARY_PATH=$FFTWHOME/lib:'$LD_LIBRARY_PATH'"" >>$setup_script
  fi

  source $setup_script
fi

if [ $test_flag ]; then

  nGPUs=$(nvidia-smi -L | wc -l)

  echo -e "\n***** Testing Savu setup *****\n"
  savu_quick_tests

  echo -e "\n*****Running Savu single-threaded local tests *****\n"
  savu_full_tests

  echo -e "\n************** Single-threaded local tests complete ******************\n"

fi

if [ ! $test_flag ]; then

  echo -e "*************** SAVU INSTALLATION COMPLETE! ******************\n"
  echo -e "    ......Thank you for running the Savu installer......\n"
  echo -e "=============================================================\n"
else
  echo -e "\n\n*************** SAVU TESTS COMPLETE! ******************\n"
  echo -e "    ......Thank you for running the Savu tests......\n"
  echo -e " Please check $tmpfile for errors\n"
  echo -e "=======================================================\n"
fi

echo -e "\n\t***************************************************"
echo -e "\t          Package installation complete"
echo -e "\t  Check $error_log for errors"
echo -e "\t***************************************************\n"

exit 0
