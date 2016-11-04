module load global/cluster

echo "running the mpi job"

savupath=$1
datafile=$2
processfile=$3
outpath=$4
outname=$5
nNodes=$6
nCPUs=$7
shift 7

echo "nNodes" $nNodes
echo $outname
nCoresPerNode=20

DIR="$(cd "$(dirname "$0")" && pwd)"
filepath=$DIR'/savu_mpijob.sh'
savupath=${DIR%/bin}

M=$((nNodes*nCoresPerNode))

qsub -N $outname -sync y -j y -pe openmpi $M -l exclusive -l infiniband -l gpu=1 -q medium.q@@com10 $filepath $savupath $datafile $processfile $outpath $nCoresPerNode $@ > tmp.txt

filename=`echo $outname.o`
jobnumber=`awk '{print $3}' tmp.txt | head -n 1`
filename=$filename$jobnumber

while [ ! -f $filename ]
do
  sleep 2
done

cat $filename
echo $filename

