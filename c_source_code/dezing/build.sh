#!/bin/bash
make static

CFLAGS="-I ." LDFLAGS="-L ." python setup.py build_ext -i
