module add python/ana
#$Id: buildint16.sh 446 2015-12-15 12:08:48Z kny48981 $

#make shared
#make static

# the setup.py done this way automatically calls the compiler
# no need for building the library explicitly
# but additional source files need to be added in the .pyx file in special comments for distutils

export CFLAGS="-I . $CFLAGS"
export LDFLAGS="-L . $LDFLAGS"
python setupint16.py build_ext -i
#python setup.py cythonize
#make debug

