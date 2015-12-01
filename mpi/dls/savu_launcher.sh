#!/bin/bash
module load global/cluster

echo "SAVU_LAUNCHER:: Running Job"

cd /dls/tmp/savu/

echo "SAVU_LAUNCHER:: Changed to temporary directory - /dls/tmp/savu"

savupath=/dls_sw/apps/savu/master/Savu
datafile=$1
processfile=$2
outpath=$3
outname=savu
nNodes=1
nCPUs=20

filepath=$savupath/bin/savu_mpijob.sh
M=$((nNodes*20))

echo "SAVU_LAUNCHER:: Running Job, please wait"

qsub -N $outname -sync y -j y -pe openmpi $M -l infiniband -q medium.q@@com10 $filepath $savupath $datafile $processfile $outpath $nCPUs > $USER.out

echo "SAVU_LAUNCHER:: Job Complete, preparing output..."

filename=`echo $outname.o`
jobnumber=`awk '{print $3}' $USER.out | head -n 1`
filename=$filename$jobnumber

while [ ! -f $filename ]
do
  sleep 2
done

echo "SAVU_LAUNCHER:: Output ready, spooling now"

cat $filename

echo "SAVU_LAUNCHER:: Process complete"