#!/bin/bash

while read -r a b c d; do

	if [ ! -z "$a" ]; then

	nNodes=$a
	nCPUs=$b
	nRuns=$c
	fname=$d

	echo $nNodes $nCPUs $nRuns $fname


	DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
	x=$DIR
	echo $x
	savupath=${x%/bin}

	#runfile=/bin/savu_distArray_launcher.sh
	runfile=/bin/savu_launcher.sh
	outpath=$PWD #outputting to the current folder
	#datafile=$outpath/../test_data/24888.nxs
	datafile=$outpath/../test_data/ee12581-1_test/pc2_KRA_530_ramp_00000.hdf
	processfile=$outpath/../test_data/i12_tomo_pipeline.nxs
	outname="${fname}N${nNodes}_C${nCPUs}_mpi_test"

	for i in $(eval echo {1..$nRuns})
  		do
   		  $savupath$runfile $savupath $datafile $processfile $outpath $outname $nNodes $nCPUs
	done


    
      #************ Delete if auto-profiling is not required ******************
      #****************** This can be done offline ****************************
    
      #cd Profiling
	  #python $savupath/scripts/log_evaluation/VisualiseProfileData.py
      #cd ../

      #************************************************************************

      #echo "completed profiling"
	fi	

done < ../test.txt

