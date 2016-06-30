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
    
    #datafile=/dls/i13/data/2016/mt14080-1/raw/77391.nxs
    #processfile=$outpath/test.nxs

    #datafile=$outpath/../../test_data/sn65/SampleA
    #processfile=$outpath/sri_test.nxs

    datafile=$outpath/../../test_data/mark_data/
    processfile=/home/qmm55171/Documents/Git/git_repos/Savu/scripts/config_generator/test_processes/multi_nxs_test.nxs

    #datafile=/dls/i18/data/2016/sp12778-1/processing/Savu_testing_steve/XRF/RAW_DATA/67086_homer_absorption_tomo17kev_1.nxs
    #processfile=$outpath/i18_test2.nxs
    #processfile=$outpath/i18_fluo_preview.nxs

    #datafile=/dls/i12/data/2016/cm14465-1/processing/brick-data/dls/i12/data/2014/cm4963-3/rawdata/40384.nxs
    #processfile=/home/qmm55171/Documents/Git/git_repos/Savu/scripts/config_generator/test_loader.nxs

    #datafile=/dls/i13/data/2016/mt14367-1/raw/75814.nxs
    #processfile=/home/qmm55171/Documents/Git/git_repos/Savu/scripts/config_generator/test_processes/i13_process_list_preview.nxs

    #datafile=/dls/i18/data/2016/sp12601-1/processing/Savu_Test_Data/70214_Cat2_RT_1.nxs
    #processfile=/home/qmm55171/Documents/Git/git_repos/Savu/scripts/config_generator/test_processes/i18_tiff_test.nxs

    #processfile=/dls/i18/data/2016/sp12601-1/processing/Savu_Test_Data/new_test_process_list.nxs

    #datafile=$outpath/../test_data/24737.nxs
    #processfile=/home/qmm55171/Documents/Git/git_repos/Savu/scripts/config_generator/test_processes/test.nxs
    #processfile=/home/qmm55171/Documents/Git/git_repos/Savu/test_data/test_process_lists/NLReg_cgls.nxs

    #processfile=/home/qmm55171/Documents/Git/git_repos/Savu/test_data/test_process_lists/vo_centering_test.nxs
    #processfile=/home/qmm55171/Documents/Git/git_repos/Savu/scripts/config_generator/test_processes/astra_gpu_test.nxs
    #datafile=/dls/i12/data/2015/ee10500-1/processing/LD_2W50_8/LD_2W50_8_Dataset_093.nxs
    #processfile=/home/qmm55171/Documents/Git/git_repos/Savu/test_data/test_process_lists/basic_tomo_process.nxs
    #processfile=/home/qmm55171/Documents/Git/git_repos/Savu/scripts/config_generator/mpi_settings_test.nxs
    
    #datafile=$outpath/../test_data/LD_2W50_8_Dataset_038.nxs
	#processfile=$outpath/../test_data/original_process_lists/i12_tomo_pipeline_preview_55751.nxs
    
    #datafile=$outpath/../test_data/ee12581-1_test/pc2_KRA_530_ramp_00000.hdf
    #process_file=/home/qmm55171/Documents/Git/git_repos/Savu/scripts/config_generator/test_processes/test.nxs
    #processfile=/home/qmm55171/Documents/Git/git_repos/Savu/scripts/config_generator/test_processes/test_loader_i12.nxs
    #processfile=$outpath/../test_data/i12_tomo_pipeline_gpu.nxs
	#processfile=$outpath/../test_data/i12_full_test.nxs

    #datafile=$outpath/../test_data/for_nicola/54681.nxs
	#processfile=/home/qmm55171/Documents/Git/git_repos/Savu/scripts/config_generator/test_processes/sally_pipeline.nxs
    #datafile=/dls/i12/data/2015/sw12280-3/rawdata/54652.nxs
    #datafile=/dls/i12/data/2015/sw12280-3/rawdata/54653.nxs
    #datafile=/dls/i12/data/2015/sw12280-3/rawdata/54654.nxs
	#processfile=/home/qmm55171/Documents/Git/git_repos/Savu/scripts/config_generator/test_processes/sally_pipeline_full.nxs
    #processfile=/home/qmm55171/Documents/Git/git_repos/Savu/scripts/config_generator/test_processes/sally_pipeline_preview.nxs

    #datafile=/dls/science/sharpfiles/oqi73530/tubetDataTest081Jan2016.nxs
    #processfile=/home/qmm55171/Documents/Git/git_repos/Savu/test_data/process_lists/B16_pipeline_preview.nxs

    #datafile=/dls/i13/data/2015/cm12165-5/processing/AskAaron/mmbig_58905.nxs
    #processfile=/home/qmm55171/Documents/Git/git_repos/Savu/test_data/process_lists/I18_pipeline_just_xrd.nxs

    # i13 data
    #datafile=/dls/i13/data/2016/mt13302-1/raw/72588.nxs
    #processfile=$outpath/../test_data/i13_mapping_preview.nxs

    #datafile=/home/qmm55171/Documents/Git/git_repos/Savu/test_data/data/mm.nxs
    #datafile=/dls/i18/data/2016/sp12778-1/processing/converted_files_for_savu/67132.nxs
    #processfile=/home/qmm55171/Documents/Git/git_repos/Savu/test_data/process_lists/I18_pipeline_just_xrd_from_raw_filtered_adp_mod2.nxs

	outname="${fname}N${nNodes}_C${nCPUs}_mpi_test"

    echo $data_file $process_file

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

done < ../../test.txt

