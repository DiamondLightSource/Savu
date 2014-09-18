module load global/cluster

qsub -j y -pe openmpi 8 -q medium.q@@com01 /home/ssg37927/Savu/mpi/dls/mpijob.sh $@