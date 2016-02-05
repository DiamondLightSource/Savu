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
    datafile=$outpath/../test_data/24737.nxs
    #datafile=/dls/i12/data/2015/ee10500-1/processing/LD_2W50_8/LD_2W50_8_Dataset_093.nxs
    processfile=/home/qmm55171/Documents/Git/git_repos/Savu/test_data/test_process_lists/timeseries_field_corrections_test_process.nxs
    #processfile=/home/qmm55171/Documents/Git/git_repos/Savu/scripts/config_generator/test_processes/astra_gpu_test.nxs
    
    #datafile=$outpath/../test_data/LD_2W50_8_Dataset_038.nxs
	#processfile=$outpath/../test_data/original_process_lists/i12_tomo_pipeline_preview_55751.nxs
    
    #datafile=$outpath/../test_data/ee12581-1_test/pc2_KRA_530_ramp_00000.hdf
	#processfile=$outpath/../test_data/i12_tomo_pipeline.nxs

    #datafile=$outpath/../test_data/for_nicola/54681.nxs
	#processfile=/home/qmm55171/Documents/Git/git_repos/Savu/scripts/config_generator/test_processes/sally_pipeline.nxs
    #datafile=/dls/i12/data/2015/sw12280-3/rawdata/54652.nxs
    #datafile=/dls/i12/data/2015/sw12280-3/rawdata/54653.nxs
    #datafile=/dls/i12/data/2015/sw12280-3/rawdata/54654.nxs
	#processfile=/home/qmm55171/Documents/Git/git_repos/Savu/scripts/config_generator/test_processes/sally_pipeline_full.nxs
#	processfile=/home/qmm55171/Documents/Git/git_repos/Savu/scripts/config_generator/test_processes/sally_pipeline_preview.nxs

    #datafile=/dls/science/sharpfiles/oqi73530/tubetDataTest081Jan2016.nxs
    #processfile=/home/qmm55171/Documents/Git/git_repos/Savu/test_data/process_lists/B16_pipeline_preview.nxs

    #datafile=/dls/i13/data/2015/cm12165-5/processing/AskAaron/mmbig_58905.nxs
    #processfile=/home/qmm55171/Documents/Git/git_repos/Savu/test_data/process_lists/I18_pipeline_just_xrd.nxs

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

