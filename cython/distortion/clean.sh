
#$Id: clean.sh 448 2015-12-15 12:14:14Z kny48981 $
set -x
make clean
rm  -f unwarp.cpp  unwarp.cpp 
rm -rf build
set +x

