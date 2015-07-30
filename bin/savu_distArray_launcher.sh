echo "running the mpi job" 

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
x=$DIR
echo $x
savupath=${x%/bin}


module load global/cluster
#module load global/testcluster

outpath=$PWD #outputting to the current folder
datafile=$outpath/../test_data/24888.nxs	
processfile=$outpath/../test_data/process01.nxs
outname="testing_dist_array"
nNodes=2
nCPUs=12

filepath=$savupath/bin/savu_distArray.sh
M=$((nNodes*12))

#qsub -N $outname -sync y -j y -pe openmpi $M -q test-medium.q -l infiniband $filepath $savupath $datafile $processfile $outpath $nCPUs > tmp.txt
qsub -N $outname -sync y -j y -pe openmpi $M -l exclusive -q medium.q@@com06 $filepath $savupath $datafile $processfile $outpath $nCPUs > tmp.txt

if [ ! -d $outpath/Profiling ]; then
    mkdir -p $outpath/Profiling;
fi

filename=`echo $outname.o`
jobnumber=`awk '{print $3}' tmp.txt | head -n 1`
filename=$filename$jobnumber

while [ ! -f $filename ]
do
  sleep 2
done

cat $filename

grep "L " $filename > Profiling/log_$filename

#sleep 20
#echo qacct -j ${jobnumber}
#qacct -j ${jobnumber}

