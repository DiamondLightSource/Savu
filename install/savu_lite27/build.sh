#!/bin/bash

python -m pip install . --no-deps --ignore-installed -vv
#python -m pip install . --no-deps --ignore-installed --no-cache-dir -vvv
#$PYTHON setup.py install

pip install https://files.pythonhosted.org/packages/e3/bf/06ba84df6ed76903d7ba25440337c9c41ca4147fc9bc310474cd4d1d8fef/gnureadline-8.0.0-cp27-cp27mu-manylinux1_x86_64.whl

# pip install nvidia-ml-py==7.352.0
pip install https://files.pythonhosted.org/packages/72/31/378ca145e919ca415641a0f17f2669fa98c482a81f1f8fdfb72b1f9dbb37/nvidia-ml-py-7.352.0.tar.gz


