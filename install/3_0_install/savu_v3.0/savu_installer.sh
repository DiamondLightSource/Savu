#!/bin/bash -ex

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
savu_version=$(cat $DIR/version.txt)

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

# Set the install PREFIX
arg_parse "--PREFIX" PREFIX "$@"

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

# set the conda folder
arg_parse "-c" conda_folder "$@"
if [ ! $conda_folder ]; then
  conda_folder=Savu_$savu_version
fi

# set the savu recipe
arg_parse "-s" savu_recipe "$@"
if [ ! $savu_recipe ]; then
  savu_recipe=savu
elif [ $savu_recipe = 'master' ]; then
  savu_recipe=savu_master
else
  echo "Unknown Savu installation version."
fi

# override the conda recipes folder
arg_parse "-r" recipes "$@"

# Specify whether this is running on CI
arg_parse "--local" local_installation "$@"
if [ ! $local_installation ]; then
  local_installation=false
else
  local_installation=true
fi
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
  echo -e "fftw is required to build Savu."
  echo -e "Cuda is desirable for a full range of plugins."
  echo -e "\n============================================================="
fi

if [ $local_installation = false ]; then
  # set compiler wrapper
  MPICC=$(command -v mpicc)
  MPI_HOME=${MPICC%/mpicc}
  if ! [ "$MPICC" ]; then
    echo "ERROR: I require mpicc but I can't find it.  Check /path/to/mpi_implementation/bin is in your PATH"
    exit 1
  else
    echo "Using mpicc:   " $MPICC
    export PATH=$MPI_HOME:$PATH
  fi
else
  echo "Going to use the openmpi installation from conda"
fi

# check for fftw
# CFLAGS=""
# LDFLAGS=""
# IFS=:
# file_base=libfftw?.so
# for p in ${LD_LIBRARY_PATH}; do
#     file_path=${p}/$file_base
#     if [ "x$p" != "x" -a -e $file_path ]; then
#         FFTWHOME=${file_path%/lib/libfftw?.so}
#         CFLAGS="$FFTWHOME/include"
#         LDFLAGS="$FFTWHOME/lib"
#         break
#     fi
# done

# if [ "$CFLAGS" ]; then
#     echo "Using fftw:    " $FFTWHOME
# else
#     echo "fftw has not been found."
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
  # TODO replace with module load python/ana if conda is not on PATH - for non-local builds!
  wget https://repo.continuum.io/miniconda/Miniconda3-$miniconda_version-Linux-x86_64.sh -O $PREFIX/miniconda.sh

  miniconda_dir=$PREFIX/miniconda
  env_dir=$PREFIX/savu

  bash $PREFIX/miniconda.sh -b -p $miniconda_dir
  PYTHONHOME=$env_dir/bin

  "$miniconda_dir"/bin/conda create -y -p $env_dir
  source $miniconda_dir/bin/activate $env_dir

  # conda-build needed to build the savu/hdf5/h5py packages
  # cython needed to compile dezing and unwarp savu plugins
  conda install -y -q conda-build conda-verify cython

  echo "Building Savu..."
  conda build $DIR/$savu_recipe
  savubuild=$(conda build $DIR/$savu_recipe --output)
  echo "Installing Savu..."
  conda install -y -q --use-local $savubuild

  path=$(python -c "import savu; import os; print(os.path.abspath(savu.__file__))")
  savu_path=${path%/savu/__init__.py*}

  # get the savu version
  if [ -z $recipes ]; then
    install_path=$(python -c "import savu; import savu.version as sv; print(sv.__install__)")
    recipes=$savu_path/$install_path/conda-recipes
  fi

  launcher_path=`command -v savu_launcher.sh`
  launcher_path=${launcher_path%/savu_launcher.sh}
  if [ "$facility" ]; then
    cp $savu_path/system_files/$facility/mpi/savu_launcher.sh $launcher_path
    cp $savu_path/system_files/$facility/mpi/savu_mpijob.sh $launcher_path
  fi

  if [ $local_installation = false ]; then
    echo "Installing mpi4py..."
    pip uninstall -y -q mpi4py || true
    string=$(awk '/^mpi4py/' $versions_file)
    mpi4py_version=$(echo $string | cut -d " " -f 2)
    pip install mpi4py==$mpi4py_version

    echo "Building hdf5..."
    conda uninstall -y -q hdf5 || true
    conda build $recipes/hdf5
    hdf5build=$(conda build $recipes/hdf5 --output)

    echo "Installing hdf5..."
    conda install -y -q --use-local $hdf5build

    echo "Building h5py..."
    conda uninstall -y -q h5py || true
    conda build $recipes/h5py --no-test
    h5pybuild=$(conda build $recipes/h5py --output)

    echo "Installing h5py..."
    conda install -y -q --use-local $h5pybuild
  else
    echo "Installing mpi4py/hdf5/h5py from conda for CI run"
    conda env update -f $DIR/environment_ci.yml
  fi
  conda env update -f $DIR/environment.yml

  # cleanup base miniconda and build artifacts
  rm $PREFIX/miniconda.sh
  rm -rf $PREFIX/miniconda

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
        echo -e "   >>> bash savu_v3/savu_installer.sh --tests_only"
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

  test_dir=$(mktemp -d)
  tmp_dir=$(mktemp -d)
  tmpfile=$tmp_dir/temp_output.txt
  touch $tmpfile

fi

if [ ! $test_flag ]; then

  launcher_path=$(command -v savu_launcher.sh)
  mpijob_path=$(command -v savu_mpijob.sh)
  echo -e "\n\n===============================IMPORTANT NOTICES================================"
  echo -e "If you are installing Savu for cluster use, you will need to update the savu "
  echo -e "launcher scripts:"
  echo -e "\n$launcher_path"
  echo -e "$mpijob_path\n"
  echo -e "\n\nTo run Savu type 'source $savu_setup' to set relevant paths every time you"
  echo -e "open a new terminal.  Alternatively, if you are using the Modules system, see"
  echo -e "$DIR/module_template for an example module file."
  echo -e "================================================================================\n"

  echo -e "*************** SAVU INSTALLATION COMPLETE! ******************\n"
  echo -e "    ......Thank you for running the Savu installer......\n"
  echo -e "=============================================================\n"
else
  echo -e "\n\n*************** SAVU TESTS COMPLETE! ******************\n"
  echo -e "    ......Thank you for running the Savu tests......\n"
  echo -e " Please check $tmpfile for errors\n"
  echo -e "=======================================================\n"
fi

exit 0
