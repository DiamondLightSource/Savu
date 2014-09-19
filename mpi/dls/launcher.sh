module load global/cluster

qsub -sync y -j y -pe openmpi 8 -q medium.q@@com01 /home/ssg37927/Savu/mpi/dls/mpijob.sh $@ > tmp.txt

filename=`echo mpirun.sh.o`
filename=$filename`awk '{print $3}' tmp.txt`

cat $filename