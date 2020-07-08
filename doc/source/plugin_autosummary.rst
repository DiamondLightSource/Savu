.. _api_plugin:

**********************
Api Plugin 
**********************

.. toctree::


Absorption Corrections
########################################################

.. toctree::
   Base Absorption Correction <api_plugin/plugins.absorption_corrections.base_absorption_correction>
   Mc Near Absorption Correction <api_plugin/plugins.absorption_corrections.mc_near_absorption_correction>


Alignment
########################################################

.. toctree::
   Projection Shift <api_plugin/plugins.alignment.projection_shift>
   Projection Vertical Alignment <api_plugin/plugins.alignment.projection_vertical_alignment>
   Sinogram Alignment <api_plugin/plugins.alignment.sinogram_alignment>
   Sinogram Clean <api_plugin/plugins.alignment.sinogram_clean>


Analysis
########################################################

.. toctree::
   Base Analysis <api_plugin/plugins.analysis.base_analysis>
   Histogram <api_plugin/plugins.analysis.histogram>
   Stats <api_plugin/plugins.analysis.stats>
   Stxm Analysis <api_plugin/plugins.analysis.stxm_analysis>


Azimuthal Integrators
########################################################

.. toctree::
   Base Azimuthal Integrator <api_plugin/plugins.azimuthal_integrators.base_azimuthal_integrator>
   Pyfai Azimuthal Integrator <api_plugin/plugins.azimuthal_integrators.pyfai_azimuthal_integrator>
   Pyfai Azimuthal Integrator Separate <api_plugin/plugins.azimuthal_integrators.pyfai_azimuthal_integrator_separate>
   Pyfai Azimuthal Integrator With Bragg Filter <api_plugin/plugins.azimuthal_integrators.pyfai_azimuthal_integrator_with_bragg_filter>


Basic Operations
########################################################

.. toctree::
   Arithmetic Operations <api_plugin/plugins.basic_operations.arithmetic_operations>
   Basic Operations <api_plugin/plugins.basic_operations.basic_operations>
   Data Rescale <api_plugin/plugins.basic_operations.data_rescale>
   Get Data Statistics <api_plugin/plugins.basic_operations.get_data_statistics>
   No Process Plugin <api_plugin/plugins.basic_operations.no_process_plugin>
   Data Threshold <api_plugin/plugins.basic_operations.data_threshold>
   Value Mask Replacement <api_plugin/plugins.basic_operations.value_mask_replacement>
   Elementwise Arrays Arithmetics <api_plugin/plugins.basic_operations.elementwise_arrays_arithmetics>
   No Process <api_plugin/plugins.basic_operations.no_process>


Centering
########################################################

.. toctree::
   Vo Centering <api_plugin/plugins.centering.vo_centering>
   Vo Centering Iterative <api_plugin/plugins.centering.vo_centering_iterative>


Component Analysis
########################################################

.. toctree::
   Base Component Analysis <api_plugin/plugins.component_analysis.base_component_analysis>
   Ica <api_plugin/plugins.component_analysis.ica>
   Pca <api_plugin/plugins.component_analysis.pca>


Corrections
########################################################

.. toctree::
   Base Correction <api_plugin/plugins.corrections.base_correction>
   Camera Rot Correction <api_plugin/plugins.corrections.camera_rot_correction>
   Convert 360 180 Sinogram <api_plugin/plugins.corrections.convert_360_180_sinogram>
   Dark Flat Field Correction <api_plugin/plugins.corrections.dark_flat_field_correction>
   Distortion Correction <api_plugin/plugins.corrections.distortion_correction>
   Monitor Correction <api_plugin/plugins.corrections.monitor_correction>
   Monitor Correction Nd <api_plugin/plugins.corrections.monitor_correction_nd>
   Subpixel Shift <api_plugin/plugins.corrections.subpixel_shift>
   Time Based Correction <api_plugin/plugins.corrections.time_based_correction>
   Time Based Plus Drift Correction <api_plugin/plugins.corrections.time_based_plus_drift_correction>
   Timeseries Field Corrections <api_plugin/plugins.corrections.timeseries_field_corrections>
   Xrd Absorption Approximation <api_plugin/plugins.corrections.xrd_absorption_approximation>
   Mtf Deconvolution <api_plugin/plugins.corrections.mtf_deconvolution>
   Distortion Correction Deprecated <api_plugin/plugins.corrections.distortion_correction_deprecated>


Developing
########################################################

.. toctree::
   Testing Sino Align <api_plugin/plugins.developing.testing_sino_align>


Driver
########################################################

.. toctree::
   All Cpus Plugin <api_plugin/plugins.driver.all_cpus_plugin>
   Base Driver <api_plugin/plugins.driver.base_driver>
   Basic Driver <api_plugin/plugins.driver.basic_driver>
   Cpu Plugin <api_plugin/plugins.driver.cpu_plugin>
   Gpu Plugin <api_plugin/plugins.driver.gpu_plugin>
   Iterative Plugin <api_plugin/plugins.driver.iterative_plugin>
   Multi Threaded Plugin <api_plugin/plugins.driver.multi_threaded_plugin>
   Plugin Driver <api_plugin/plugins.driver.plugin_driver>


Filters
########################################################

.. toctree::
   Band Pass <api_plugin/plugins.filters.band_pass>
   Base Filter <api_plugin/plugins.filters.base_filter>
   Pymca <api_plugin/plugins.filters.pymca>
   Dezinger <api_plugin/plugins.filters.dezinger>
   Dezinger Simple <api_plugin/plugins.filters.dezinger_simple>
   Dezinger Sinogram <api_plugin/plugins.filters.dezinger_sinogram>
   Dials Find Spots <api_plugin/plugins.filters.dials_find_spots>
   Find Peaks <api_plugin/plugins.filters.find_peaks>
   Fresnel Filter <api_plugin/plugins.filters.fresnel_filter>
   Hilbert Filter <api_plugin/plugins.filters.hilbert_filter>
   Image Interpolation <api_plugin/plugins.filters.image_interpolation>
   List To Projections <api_plugin/plugins.filters.list_to_projections>
   Paganin Filter <api_plugin/plugins.filters.paganin_filter>
   Poly Background Estimator <api_plugin/plugins.filters.poly_background_estimator>
   Umpa <api_plugin/plugins.filters.umpa>
   Quantisation Filter <api_plugin/plugins.filters.quantisation_filter>
   Spectrum Crop <api_plugin/plugins.filters.spectrum_crop>
   Strip Background <api_plugin/plugins.filters.strip_background>
   Threshold Filter <api_plugin/plugins.filters.threshold_filter>


Denoising
********************************************************

.. toctree::
   Ccpi Denoising Cpu <api_plugin/plugins.filters.denoising.ccpi_denoising_cpu>
   Ccpi Denoising Cpu 3D <api_plugin/plugins.filters.denoising.ccpi_denoising_cpu_3D>
   Ccpi Denoising Gpu <api_plugin/plugins.filters.denoising.ccpi_denoising_gpu>
   Ccpi Denoising Gpu 3D <api_plugin/plugins.filters.denoising.ccpi_denoising_gpu_3D>
   Denoise Bregman Filter <api_plugin/plugins.filters.denoising.denoise_bregman_filter>
   Median Filter <api_plugin/plugins.filters.denoising.median_filter>


Fitters
########################################################

.. toctree::
   Base Fitter <api_plugin/plugins.fitters.base_fitter>
   Ral Fit <api_plugin/plugins.fitters.ral_fit>
   Reproduce Fit <api_plugin/plugins.fitters.reproduce_fit>
   Simple Fit <api_plugin/plugins.fitters.simple_fit>


Fluo Fitters
########################################################

.. toctree::
   Base Fluo Fitter <api_plugin/plugins.fluo_fitters.base_fluo_fitter>
   Fastxrf Fitting <api_plugin/plugins.fluo_fitters.fastxrf_fitting>
   Simple Fit Xrf <api_plugin/plugins.fluo_fitters.simple_fit_xrf>


Kinematics
########################################################

.. toctree::
   Stage Motion <api_plugin/plugins.kinematics.stage_motion>


Loaders
########################################################

.. toctree::
   Base Loader <api_plugin/plugins.loaders.base_loader>
   Hdf5 Template Loader <api_plugin/plugins.loaders.hdf5_template_loader>
   Image Template Loader <api_plugin/plugins.loaders.image_template_loader>
   Multi Savu Loader <api_plugin/plugins.loaders.multi_savu_loader>
   Random Hdf5 Loader <api_plugin/plugins.loaders.random_hdf5_loader>
   Savu Nexus Loader <api_plugin/plugins.loaders.savu_nexus_loader>
   Yaml Converter <api_plugin/plugins.loaders.yaml_converter>


Full Field Loaders
********************************************************

.. toctree::
   Dxchange Loader <api_plugin/plugins.loaders.full_field_loaders.dxchange_loader>
   Image Loader <api_plugin/plugins.loaders.full_field_loaders.image_loader>
   Mrc Loader <api_plugin/plugins.loaders.full_field_loaders.mrc_loader>
   Multi Nxtomo Loader <api_plugin/plugins.loaders.full_field_loaders.multi_nxtomo_loader>
   Nxtomo Loader <api_plugin/plugins.loaders.full_field_loaders.nxtomo_loader>
   Random 3D Tomo Loader <api_plugin/plugins.loaders.full_field_loaders.random_3d_tomo_loader>


Mapping Loaders
********************************************************

.. toctree::
   Base Multi Modal Loader <api_plugin/plugins.loaders.mapping_loaders.base_multi_modal_loader>
   Mm Loader <api_plugin/plugins.loaders.mapping_loaders.mm_loader>
   Nxfluo Loader <api_plugin/plugins.loaders.mapping_loaders.nxfluo_loader>
   Nxmonitor Loader <api_plugin/plugins.loaders.mapping_loaders.nxmonitor_loader>
   Nxptycho Loader <api_plugin/plugins.loaders.mapping_loaders.nxptycho_loader>
   Nxstxm Loader <api_plugin/plugins.loaders.mapping_loaders.nxstxm_loader>
   Nxxrd Loader <api_plugin/plugins.loaders.mapping_loaders.nxxrd_loader>
   P2R Fly Scan Detector Loader <api_plugin/plugins.loaders.mapping_loaders.p2r_fly_scan_detector_loader>
   Txm Loader <api_plugin/plugins.loaders.mapping_loaders.txm_loader>


I08 Loaders
--------------------------------------------------------

.. toctree::
   I08 Fluo Loader <api_plugin/plugins.loaders.mapping_loaders.i08_loaders.i08_fluo_loader>


I13 Loaders
--------------------------------------------------------

.. toctree::
   I13 Fluo Loader <api_plugin/plugins.loaders.mapping_loaders.i13_loaders.i13_fluo_loader>
   I13 Ptycho Loader <api_plugin/plugins.loaders.mapping_loaders.i13_loaders.i13_ptycho_loader>
   I13 Speckle Loader <api_plugin/plugins.loaders.mapping_loaders.i13_loaders.i13_speckle_loader>
   I13 Stxm Loader <api_plugin/plugins.loaders.mapping_loaders.i13_loaders.i13_stxm_loader>
   I13 Stxm Monitor Loader <api_plugin/plugins.loaders.mapping_loaders.i13_loaders.i13_stxm_monitor_loader>
   I13 Stxm Xrf Loader <api_plugin/plugins.loaders.mapping_loaders.i13_loaders.i13_stxm_xrf_loader>


I14 Loaders
--------------------------------------------------------

.. toctree::
   I14 Fluo Loader <api_plugin/plugins.loaders.mapping_loaders.i14_loaders.i14_fluo_loader>


I18 Loaders
--------------------------------------------------------

.. toctree::
   Base I18 Multi Modal Loader <api_plugin/plugins.loaders.mapping_loaders.i18_loaders.base_i18_multi_modal_loader>
   I18 Fluo Loader <api_plugin/plugins.loaders.mapping_loaders.i18_loaders.i18_fluo_loader>
   I18 Mm Loader <api_plugin/plugins.loaders.mapping_loaders.i18_loaders.i18_mm_loader>
   I18 Monitor Loader <api_plugin/plugins.loaders.mapping_loaders.i18_loaders.i18_monitor_loader>
   I18 Stxm Loader <api_plugin/plugins.loaders.mapping_loaders.i18_loaders.i18_stxm_loader>
   I18 Xrd Loader <api_plugin/plugins.loaders.mapping_loaders.i18_loaders.i18_xrd_loader>


I22 Loaders
--------------------------------------------------------

.. toctree::
   I22 Tomo Loader <api_plugin/plugins.loaders.mapping_loaders.i22_loaders.i22_tomo_loader>


Templates
********************************************************

.. toctree::


I18 Templates
--------------------------------------------------------

.. toctree::


Malcolm Templates
--------------------------------------------------------

.. toctree::


Nexus Templates
--------------------------------------------------------

.. toctree::


Utils
********************************************************

.. toctree::
   Yaml Utils <api_plugin/plugins.loaders.utils.yaml_utils>


Missing Data
########################################################

.. toctree::


Ptychography
########################################################

.. toctree::
   Base Ptycho <api_plugin/plugins.ptychography.base_ptycho>
   Dummy Ptycho <api_plugin/plugins.ptychography.dummy_ptycho>
   Ptypy Batch <api_plugin/plugins.ptychography.ptypy_batch>
   Ptypy Compact <api_plugin/plugins.ptychography.ptypy_compact>


Reconstructions
########################################################

.. toctree::
   Base Recon <api_plugin/plugins.reconstructions.base_recon>
   Ccpi Cgls Recon <api_plugin/plugins.reconstructions.ccpi_cgls_recon>
   Scikitimage Filter Back Projection <api_plugin/plugins.reconstructions.scikitimage_filter_back_projection>
   Scikitimage Sart <api_plugin/plugins.reconstructions.scikitimage_sart>
   Simple Recon <api_plugin/plugins.reconstructions.simple_recon>
   Tomopy Recon <api_plugin/plugins.reconstructions.tomopy_recon>
   Visual Hulls Recon <api_plugin/plugins.reconstructions.visual_hulls_recon>


Astra Recons
********************************************************

.. toctree::
   Astra Recon Cpu <api_plugin/plugins.reconstructions.astra_recons.astra_recon_cpu>
   Astra Recon Gpu <api_plugin/plugins.reconstructions.astra_recons.astra_recon_gpu>
   Base Astra Recon <api_plugin/plugins.reconstructions.astra_recons.base_astra_recon>


Tomobar
********************************************************

.. toctree::
   Tomobar Recon <api_plugin/plugins.reconstructions.tomobar.tomobar_recon>
   Tomobar Recon 3D <api_plugin/plugins.reconstructions.tomobar.tomobar_recon_3D>
   Tomobar Recon Cpu <api_plugin/plugins.reconstructions.tomobar.tomobar_recon_cpu>
   Tomobar Recon Fully 3D <api_plugin/plugins.reconstructions.tomobar.tomobar_recon_fully_3D>


Reshape
########################################################

.. toctree::
   Data Removal <api_plugin/plugins.reshape.data_removal>
   Downsample Filter <api_plugin/plugins.reshape.downsample_filter>
   Mipmap <api_plugin/plugins.reshape.mipmap>


Ring Removal
########################################################

.. toctree::
   Ccpi Ring Artefact Filter <api_plugin/plugins.ring_removal.ccpi_ring_artefact_filter>
   Raven Filter <api_plugin/plugins.ring_removal.raven_filter>
   Remove All Rings <api_plugin/plugins.ring_removal.remove_all_rings>
   Remove Large Rings <api_plugin/plugins.ring_removal.remove_large_rings>
   Remove Unresponsive And Fluctuating Rings <api_plugin/plugins.ring_removal.remove_unresponsive_and_fluctuating_rings>
   Ring Removal Filtering <api_plugin/plugins.ring_removal.ring_removal_filtering>
   Ring Removal Fitting <api_plugin/plugins.ring_removal.ring_removal_fitting>
   Ring Removal Normalization <api_plugin/plugins.ring_removal.ring_removal_normalization>
   Ring Removal Regularization <api_plugin/plugins.ring_removal.ring_removal_regularization>
   Ring Removal Sorting <api_plugin/plugins.ring_removal.ring_removal_sorting>
   Ring Removal Waveletfft <api_plugin/plugins.ring_removal.ring_removal_waveletfft>


Savers
########################################################

.. toctree::
   Base Image Saver <api_plugin/plugins.savers.base_image_saver>
   Base Saver <api_plugin/plugins.savers.base_saver>
   Edf Saver <api_plugin/plugins.savers.edf_saver>
   Hdf5 Saver <api_plugin/plugins.savers.hdf5_saver>
   Image Saver <api_plugin/plugins.savers.image_saver>
   Tiff Saver <api_plugin/plugins.savers.tiff_saver>
   Xrf Saver <api_plugin/plugins.savers.xrf_saver>


Utils
********************************************************

.. toctree::
   Hdf5 Utils <api_plugin/plugins.savers.utils.hdf5_utils>


Segmentation
########################################################

.. toctree::


I23Segmentation
********************************************************

.. toctree::
   Final Segment I23 <api_plugin/plugins.segmentation.i23segmentation.final_segment_i23>
   I23 Segment <api_plugin/plugins.segmentation.i23segmentation.i23_segment>
   I23 Segment3D <api_plugin/plugins.segmentation.i23segmentation.i23_segment3D>


Morphological Operations
********************************************************

.. toctree::
   Morph Proc <api_plugin/plugins.segmentation.morphological_operations.morph_proc>
   Merge Binary Mask <api_plugin/plugins.segmentation.morphological_operations.merge_binary_mask>
   Merge Binary Mask 3D <api_plugin/plugins.segmentation.morphological_operations.merge_binary_mask_3D>
   Morph Remove Objects <api_plugin/plugins.segmentation.morphological_operations.morph_remove_objects>


Evolving Contours
********************************************************

.. toctree::
   Mask Evolve <api_plugin/plugins.segmentation.evolving_contours.mask_evolve>
   Mask Evolve3D <api_plugin/plugins.segmentation.evolving_contours.mask_evolve3D>
   Morph Snakes <api_plugin/plugins.segmentation.evolving_contours.morph_snakes>
   Morph Snakes3D <api_plugin/plugins.segmentation.evolving_contours.morph_snakes3D>
   Mask Conditional Evolve3D <api_plugin/plugins.segmentation.evolving_contours.mask_conditional_evolve3D>


Gaussian Mixtures
********************************************************

.. toctree::
   Gmm Segment3D <api_plugin/plugins.segmentation.gaussian_mixtures.gmm_segment3D>


Geo Distance
********************************************************

.. toctree::
   Geo Distance <api_plugin/plugins.segmentation.geo_distance.geo_distance>
   Geo Distance3D <api_plugin/plugins.segmentation.geo_distance.geo_distance3D>


Masks Initialise
********************************************************

.. toctree::
   Mask Initialiser <api_plugin/plugins.segmentation.masks_initialise.mask_initialiser>


Thresholding
********************************************************

.. toctree::
   Thresh Segm <api_plugin/plugins.segmentation.thresholding.thresh_segm>


Stats
########################################################

.. toctree::
   Min And Max <api_plugin/plugins.stats.min_and_max>


Visualisation
########################################################

.. toctree::
   Ortho Slice <api_plugin/plugins.visualisation.ortho_slice>


