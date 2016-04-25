module add fftw
module add python/ana
#make shared
make static
export CFLAGS="-I . $CFLAGS"
export LDFLAGS="-L . $LDFLAGS"
python setup.py build_ext -i
#make debug
# $Id: build.sh 465 2016-02-16 11:02:36Z kny48981 $

