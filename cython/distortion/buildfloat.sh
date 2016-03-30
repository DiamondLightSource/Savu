module add python/ana
#$Id: buildfloat.sh 448 2015-12-15 12:14:14Z kny48981 $

#make shared
#make static

# the setup.py done this way automatically calls the compiler
# no need for building the library explicitly
# but additional source files need to be added in the .pyx file in special comments for distutils

export CFLAGS="-I . $CFLAGS"
export LDFLAGS="-L . $LDFLAGS"
./clean.sh
python setupfloat.py build_ext -i
#python setup.py cythonize
#make debug

