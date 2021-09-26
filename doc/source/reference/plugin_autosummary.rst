.. _plugin_api:

**********************
Plugin Api
**********************

Absorption Corrections
########################################################

.. toctree::
   :maxdepth: 1 

   Mc Near Absorption Correction <plugin_api/plugins.absorption_corrections.mc_near_absorption_correction>


Alignment
########################################################

.. toctree::
   :maxdepth: 1 

   Projection Shift <plugin_api/plugins.alignment.projection_shift>
   Projection Vertical Alignment <plugin_api/plugins.alignment.projection_vertical_alignment>
   Sinogram Alignment <plugin_api/plugins.alignment.sinogram_alignment>
   Sinogram Clean <plugin_api/plugins.alignment.sinogram_clean>


Azimuthal Integrators
########################################################

.. toctree::
   :maxdepth: 1 

   Pyfai Azimuthal Integrator <plugin_api/plugins.azimuthal_integrators.pyfai_azimuthal_integrator>
   Pyfai Azimuthal Integrator Separate <plugin_api/plugins.azimuthal_integrators.pyfai_azimuthal_integrator_separate>
   Pyfai Azimuthal Integrator With Bragg Filter <plugin_api/plugins.azimuthal_integrators.pyfai_azimuthal_integrator_with_bragg_filter>


Basic Operations
########################################################

.. toctree::
   :maxdepth: 1 

   Arithmetic Operations <plugin_api/plugins.basic_operations.arithmetic_operations>
   Basic Operations <plugin_api/plugins.basic_operations.basic_operations>
   Get Data Statistics <plugin_api/plugins.basic_operations.get_data_statistics>
   No Process Plugin <plugin_api/plugins.basic_operations.no_process_plugin>
   Data Threshold <plugin_api/plugins.basic_operations.data_threshold>
   Rescale Intensity <plugin_api/plugins.basic_operations.rescale_intensity>
   Value Substitution <plugin_api/plugins.basic_operations.value_substitution>
   Elementwise Arrays Arithmetics <plugin_api/plugins.basic_operations.elementwise_arrays_arithmetics>


Centering
########################################################

.. toctree::
   :maxdepth: 1 

   Vo Centering <plugin_api/plugins.centering.vo_centering>


Component Analysis
########################################################

.. toctree::
   :maxdepth: 1 

   Ica <plugin_api/plugins.component_analysis.ica>
   Pca <plugin_api/plugins.component_analysis.pca>


Corrections
########################################################

.. toctree::
   :maxdepth: 1 

   Camera Rot Correction <plugin_api/plugins.corrections.camera_rot_correction>
   Convert 360 180 Sinogram <plugin_api/plugins.corrections.convert_360_180_sinogram>
   Dark Flat Field Correction <plugin_api/plugins.corrections.dark_flat_field_correction>
   Distortion Correction <plugin_api/plugins.corrections.distortion_correction>
   Monitor Correction <plugin_api/plugins.corrections.monitor_correction>
   Mtf Deconvolution <plugin_api/plugins.corrections.mtf_deconvolution>
   Subpixel Shift <plugin_api/plugins.corrections.subpixel_shift>
   Time Based Correction <plugin_api/plugins.corrections.time_based_correction>
   Time Based Plus Drift Correction <plugin_api/plugins.corrections.time_based_plus_drift_correction>


Filters
########################################################

.. toctree::
   :maxdepth: 1 

   Band Pass <plugin_api/plugins.filters.band_pass>
   Pymca <plugin_api/plugins.filters.pymca>
   Find Peaks <plugin_api/plugins.filters.find_peaks>
   Fresnel Filter <plugin_api/plugins.filters.fresnel_filter>
   Hilbert Filter <plugin_api/plugins.filters.hilbert_filter>
   Image Interpolation <plugin_api/plugins.filters.image_interpolation>
   List To Projections <plugin_api/plugins.filters.list_to_projections>
   Paganin Filter <plugin_api/plugins.filters.paganin_filter>
   Poly Background Estimator <plugin_api/plugins.filters.poly_background_estimator>
   Quantisation Filter <plugin_api/plugins.filters.quantisation_filter>
   Spectrum Crop <plugin_api/plugins.filters.spectrum_crop>
   Strip Background <plugin_api/plugins.filters.strip_background>
   Threshold Filter <plugin_api/plugins.filters.threshold_filter>


Dezingers
********************************************************

.. toctree::
   :maxdepth: 1 

   Dezinger <plugin_api/plugins.filters.dezingers.dezinger>
   Dezinger Gpu <plugin_api/plugins.filters.dezingers.dezinger_gpu>
   Dezinger Sinogram <plugin_api/plugins.filters.dezingers.dezinger_sinogram>
   Dezinger Sinogram Gpu <plugin_api/plugins.filters.dezingers.dezinger_sinogram_gpu>


Inpainting
********************************************************

.. toctree::
   :maxdepth: 1 

   Inpainting <plugin_api/plugins.filters.inpainting.inpainting>


Denoising
********************************************************

.. toctree::
   :maxdepth: 1 

   Ccpi Denoising Cpu <plugin_api/plugins.filters.denoising.ccpi_denoising_cpu>
   Ccpi Denoising Cpu 3D <plugin_api/plugins.filters.denoising.ccpi_denoising_cpu_3D>
   Ccpi Denoising Gpu <plugin_api/plugins.filters.denoising.ccpi_denoising_gpu>
   Ccpi Denoising Gpu 3D <plugin_api/plugins.filters.denoising.ccpi_denoising_gpu_3D>
   Denoise Bregman Filter <plugin_api/plugins.filters.denoising.denoise_bregman_filter>
   Median Filter <plugin_api/plugins.filters.denoising.median_filter>
   Median Filter Gpu <plugin_api/plugins.filters.denoising.median_filter_gpu>


Fitters
########################################################

.. toctree::
   :maxdepth: 1 

   Simple Fit <plugin_api/plugins.fitters.simple_fit>


Kinematics
########################################################

.. toctree::
   :maxdepth: 1 

   Stage Motion <plugin_api/plugins.kinematics.stage_motion>


Loaders
########################################################

.. toctree::
   :maxdepth: 1 

   Multi Savu Loader <plugin_api/plugins.loaders.multi_savu_loader>
   Random Hdf5 Loader <plugin_api/plugins.loaders.random_hdf5_loader>
   Savu Nexus Loader <plugin_api/plugins.loaders.savu_nexus_loader>
   Yaml Converter <plugin_api/plugins.loaders.yaml_converter>


Full Field Loaders
********************************************************

.. toctree::
   :maxdepth: 1 

   Dxchange Loader <plugin_api/plugins.loaders.full_field_loaders.dxchange_loader>
   Image Loader <plugin_api/plugins.loaders.full_field_loaders.image_loader>
   Mrc Loader <plugin_api/plugins.loaders.full_field_loaders.mrc_loader>
   Multi Nxtomo Loader <plugin_api/plugins.loaders.full_field_loaders.multi_nxtomo_loader>
   Nxtomo Loader <plugin_api/plugins.loaders.full_field_loaders.nxtomo_loader>
   Random 3D Tomo Loader <plugin_api/plugins.loaders.full_field_loaders.random_3d_tomo_loader>
   Lfov Loader <plugin_api/plugins.loaders.full_field_loaders.lfov_loader>


Mapping Loaders
********************************************************

.. toctree::
   :maxdepth: 1 

   Mm Loader <plugin_api/plugins.loaders.mapping_loaders.mm_loader>
   Nxfluo Loader <plugin_api/plugins.loaders.mapping_loaders.nxfluo_loader>
   Nxmonitor Loader <plugin_api/plugins.loaders.mapping_loaders.nxmonitor_loader>
   Nxstxm Loader <plugin_api/plugins.loaders.mapping_loaders.nxstxm_loader>
   Nxxrd Loader <plugin_api/plugins.loaders.mapping_loaders.nxxrd_loader>


Reconstructions
########################################################

.. toctree::
   :maxdepth: 1 

   Scikitimage Sart <plugin_api/plugins.reconstructions.scikitimage_sart>
   Scikitimage Filter Back Projection <plugin_api/plugins.reconstructions.scikitimage_filter_back_projection>
   Simple Recon <plugin_api/plugins.reconstructions.simple_recon>
   Tomopy Recon <plugin_api/plugins.reconstructions.tomopy_recon>
   Visual Hulls Recon <plugin_api/plugins.reconstructions.visual_hulls_recon>
   Ccpi Cgls Recon <plugin_api/plugins.reconstructions.ccpi_cgls_recon>


Astra Recons
********************************************************

.. toctree::
   :maxdepth: 1 

   Astra Recon Cpu <plugin_api/plugins.reconstructions.astra_recons.astra_recon_cpu>
   Astra Recon Gpu <plugin_api/plugins.reconstructions.astra_recons.astra_recon_gpu>


Projectors
********************************************************

.. toctree::
   :maxdepth: 1 

   Forward Projector Cpu <plugin_api/plugins.reconstructions.projectors.forward_projector_cpu>
   Forward Projector Gpu <plugin_api/plugins.reconstructions.projectors.forward_projector_gpu>


Tomobar
********************************************************

.. toctree::
   :maxdepth: 1 

   Tomobar Recon <plugin_api/plugins.reconstructions.tomobar.tomobar_recon>
   Tomobar Recon 3D <plugin_api/plugins.reconstructions.tomobar.tomobar_recon_3D>
   Tomobar Recon Cpu <plugin_api/plugins.reconstructions.tomobar.tomobar_recon_cpu>


Reshape
########################################################

.. toctree::
   :maxdepth: 1 

   Data Removal <plugin_api/plugins.reshape.data_removal>
   Downsample Filter <plugin_api/plugins.reshape.downsample_filter>
   Mipmap <plugin_api/plugins.reshape.mipmap>
   Image Stitching <plugin_api/plugins.reshape.image_stitching>
   Sum Dimension <plugin_api/plugins.reshape.sum_dimension>


Ring Removal
########################################################

.. toctree::
   :maxdepth: 1 

   Ccpi Ring Artefact Filter <plugin_api/plugins.ring_removal.ccpi_ring_artefact_filter>
   Raven Filter <plugin_api/plugins.ring_removal.raven_filter>
   Remove All Rings <plugin_api/plugins.ring_removal.remove_all_rings>
   Remove Large Rings <plugin_api/plugins.ring_removal.remove_large_rings>
   Remove Unresponsive And Fluctuating Rings <plugin_api/plugins.ring_removal.remove_unresponsive_and_fluctuating_rings>
   Ring Removal Filtering <plugin_api/plugins.ring_removal.ring_removal_filtering>
   Ring Removal Fitting <plugin_api/plugins.ring_removal.ring_removal_fitting>
   Ring Removal Normalization <plugin_api/plugins.ring_removal.ring_removal_normalization>
   Ring Removal Regularization <plugin_api/plugins.ring_removal.ring_removal_regularization>
   Ring Removal Sorting <plugin_api/plugins.ring_removal.ring_removal_sorting>
   Ring Removal Waveletfft <plugin_api/plugins.ring_removal.ring_removal_waveletfft>
   Ring Removal Interpolation <plugin_api/plugins.ring_removal.ring_removal_interpolation>


Savers
########################################################

.. toctree::
   :maxdepth: 1 

   Hdf5 Saver <plugin_api/plugins.savers.hdf5_saver>
   Image Saver <plugin_api/plugins.savers.image_saver>
   Tiff Saver <plugin_api/plugins.savers.tiff_saver>
   Xrf Saver <plugin_api/plugins.savers.xrf_saver>


Morphological Operations
********************************************************

.. toctree::
   :maxdepth: 1 

   Morph Proc <plugin_api/plugins.segmentation.morphological_operations.morph_proc>
   Morph Remove Objects <plugin_api/plugins.segmentation.morphological_operations.morph_remove_objects>
   Morph Proc Line <plugin_api/plugins.segmentation.morphological_operations.morph_proc_line>
   Morph Proc Line3D <plugin_api/plugins.segmentation.morphological_operations.morph_proc_line3D>


Evolving Contours
********************************************************

.. toctree::
   :maxdepth: 1 

   Morph Snakes <plugin_api/plugins.segmentation.evolving_contours.morph_snakes>
   Morph Snakes3D <plugin_api/plugins.segmentation.evolving_contours.morph_snakes3D>
   Region Grow <plugin_api/plugins.segmentation.evolving_contours.region_grow>
   Region Grow3D <plugin_api/plugins.segmentation.evolving_contours.region_grow3D>


Gaussian Mixtures
********************************************************

.. toctree::
   :maxdepth: 1 

   Gmm Segment3D <plugin_api/plugins.segmentation.gaussian_mixtures.gmm_segment3D>


Geo Distance
********************************************************

.. toctree::
   :maxdepth: 1 

   Geo Distance <plugin_api/plugins.segmentation.geo_distance.geo_distance>
   Geo Distance3D <plugin_api/plugins.segmentation.geo_distance.geo_distance3D>


Masks Initialise
********************************************************

.. toctree::
   :maxdepth: 1 

   Mask Initialiser <plugin_api/plugins.segmentation.masks_initialise.mask_initialiser>


Thresholding
********************************************************

.. toctree::
   :maxdepth: 1 

   Thresh Segm <plugin_api/plugins.segmentation.thresholding.thresh_segm>


Stats
########################################################

.. toctree::
   :maxdepth: 1 

   Min And Max <plugin_api/plugins.stats.min_and_max>


Visualisation
########################################################

.. toctree::
   :maxdepth: 1 

   Ortho Slice <plugin_api/plugins.visualisation.ortho_slice>


Simulation
########################################################

.. toctree::
   :maxdepth: 1 

   Tomo Phantom <plugin_api/plugins.simulation.tomo_phantom>
   Tomo Phantom Quantification <plugin_api/plugins.simulation.tomo_phantom_quantification>


