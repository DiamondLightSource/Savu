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
    #datafile=$outpath/../test_data/24737.nxs
    datafile=$outpath/../test_data/ee12581-1_test/pc2_KRA_530_ramp_00000.hdf
    #datafile=$outpath/../test_data/LD_2W50_8_Dataset_038.nxs
	#processfile=$outpath/../test_data/original_process_lists/i12_tomo_pipeline_preview_55751.nxs
	processfile=/home/qmm55171/Documents/Git/git_repos/Savu/scripts/config_generator/i12_test2.nxs
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

