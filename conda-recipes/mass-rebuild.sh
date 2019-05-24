#!/bin/sh

set -e -x

# FFTW -> https://jira.diamond.ac.uk/browse/SCI-8695
conda build --user savu-dep fftw

