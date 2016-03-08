
#$Id: allclean.sh 448 2015-12-15 12:14:14Z kny48981 $
set -x
make clean
rm  -f unwarpint16.so unwarp.so unwarpint16.cpp   unwarp.cpp 
rm -rf build
set +x

