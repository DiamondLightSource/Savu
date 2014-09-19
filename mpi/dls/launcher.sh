module load global/cluster

qsub -sync y -j y -pe openmpi 16 -q medium.q@@com01 /home/ssg37927/Savu/mpi/dls/mpijob.sh $@ > tmp.txt

filename=`echo mpijob.sh.o`
filename=$filename`awk '{print $3}' tmp.txt`

while [ ! -f $filename ]
do
  sleep 2
done

cat $filename