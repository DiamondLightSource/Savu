module add fftw
module add python/ana
#make shared
make static
export CFLAGS="-I . $CFLAGS"
export LDFLAGS="-L . $LDFLAGS"
python setup.py build_ext -i
#make debug

