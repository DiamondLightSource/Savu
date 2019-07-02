#!/bin/bash

mpi_arg="--mpi"

"${PYTHON}" setup.py configure $mpi_arg --hdf5="${PREFIX}"
"${PYTHON}" -m pip install . --no-deps --ignore-installed --no-cache-dir -vvv
