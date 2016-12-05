new_env=$1
new_version=1.2

# create module file for new Savu version with old Savu env
# change Savu version in setup.py

module load savu/$new_version
source deactivate
conda create -n $new_env
source activate $new_env
conda install python=2.7 anaconda

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
recipes=$DIR/conda-recipes

conda build $recipes/savu_test
$savu_build =`conda build $recipes/savu_test --output`

anaconda login
anaconda upload $savu_build --label test

conda install -c savu/label/test savu
savu_installer.sh dls

# update module file to source new environment
# update Savu default module load

