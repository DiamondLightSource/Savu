new_env=$1
new_version=1.2

# create module file for new Savu version with old Savu env
# update Savu version in setup.py
# update Savu version in conda recipe
# update other conda recipe versions

module load savu/$new_version
source deactivate
conda create -n $new_env
source activate $new_env
conda install python=2.7 anaconda

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
recipes=$DIR/conda-recipes

conda build $recipes/savu_test
savu_build=`conda build $recipes/savu_test --output`

anaconda login
anaconda upload $savu_build --label test

conda install -c savu/label/test savu
savu_installer.sh dls

# Update tomopy source code to not use multiprocessing

savu_quick_tests
savu_full_tests
source savu_setup.sh
mpi_cpu_test.sh /dls/tmp/qmm55171
mpi_gpu_test.sh /dls/tmp/qmm55171

# Push changes to Git
# Create new release on Github
# Create conda build of Savu and upload to anaconda cloud
# Remove savu test install and install new version of Savu into new conda env
# Re-run tests
# Download zip
# update module file to source new environment
# copy savu_launcher_preview.sh to conda_env/bin?
# update Savu default module load
# create a branch for the new release

