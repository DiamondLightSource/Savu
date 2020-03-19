#!/bin/bash

# the setup.py done this way automatically calls the compiler
# no need for building the library explicitly
# but additional source files need to be added in the .pyx file in special comments for distutils
CFLAGS="-I ." LDFLAGS="-L ." python setupfloat.py build_ext -i
