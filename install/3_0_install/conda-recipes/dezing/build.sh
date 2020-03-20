#!/bin/bash

# activate the environment where the python build is happening
# this will give access to the packages needed by the C source build
ana_path=$(command -v savu)
ana_path=${ana_path%/bin/savu}

source $ana_path/bin/activate $ana_path
export PYTHONPATH=$PYTHONPATH:$(python -c 'import site; print(site.getsitepackages())')

dezing_path=$SRC_DIR/c_source_code/dezing
cd $dezing_path

./clean.sh

make static

CFLAGS="-I $dezing_path $CFLAGS" LDFLAGS="-L $dezing_path $LDFLAGS" $PYTHON setup.py install