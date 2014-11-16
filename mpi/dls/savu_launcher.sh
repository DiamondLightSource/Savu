module load global/cluster

echo "SAVU_LAUNCHER:: Running Job"

cd /dls/tmp/savu/

echo "SAVU_LAUNCHER:: Changed to temporary directory - /dls/tmp/savu"

qsub -N mpi_test -sync y -j y -pe openmpi 24 -q medium.q@@com07 -l tesla64 $SAVU_HOME/mpi/dls/savu_mpijob.sh $@ > tmp.txt

echo "SAVU_LAUNCHER:: Job Complete, preparing output..."

filename=`echo mpi_test.o`
jobnumber=`awk '{print $3}' tmp.txt | head -n 1`
filename=$filename$jobnumber

while [ ! -f $filename ]
do
  sleep 2
done

echo "SAVU_LAUNCHER:: Output ready, spooling now"

cat $filename

echo "SAVU_LAUNCHER:: Output complete, preparing job statistics"

sleep 20

echo "SAVU_LAUNCHER:: Spooling job statistics"

echo qacct -j ${jobnumber}
qacct -j ${jobnumber}

echo "SAVU_LAUNCHER:: Process complete, End of Line..."
