# Stop on first error
set -ex

# Test C compiler
h5cc=h5pcc
echo "Testing $h5cc"
$h5cc -show
$h5cc h5_cmprss.c -o h5_cmprss
./h5_cmprss

