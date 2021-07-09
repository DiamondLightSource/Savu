.. _api_plugin:

**********************
Api Plugin 
**********************

Absorption Corrections
########################################################

.. toctree::
   :maxdepth: 1 

   Mc Near Absorption Correction <api_plugin/plugins.absorption_corrections.mc_near_absorption_correction>


Alignment
########################################################

.. toctree::
   :maxdepth: 1 

   Projection Shift <api_plugin/plugins.alignment.projection_shift>
   Projection Vertical Alignment <api_plugin/plugins.alignment.projection_vertical_alignment>
   Sinogram Alignment <api_plugin/plugins.alignment.sinogram_alignment>
   Sinogram Clean <api_plugin/plugins.alignment.sinogram_clean>


Azimuthal Integrators
########################################################

.. toctree::
   :maxdepth: 1 

   Pyfai Azimuthal Integrator <api_plugin/plugins.azimuthal_integrators.pyfai_azimuthal_integrator>
   Pyfai Azimuthal Integrator Separate <api_plugin/plugins.azimuthal_integrators.pyfai_azimuthal_integrator_separate>
   Pyfai Azimuthal Integrator With Bragg Filter <api_plugin/plugins.azimuthal_integrators.pyfai_azimuthal_integrator_with_bragg_filter>


Basic Operations
########################################################

.. toctree::
   :maxdepth: 1 

   Arithmetic Operations <api_plugin/plugins.basic_operations.arithmetic_operations>
   Basic Operations <api_plugin/plugins.basic_operations.basic_operations>
   Get Data Statistics <api_plugin/plugins.basic_operations.get_data_statistics>
   No Process Plugin <api_plugin/plugins.basic_operations.no_process_plugin>
   Data Threshold <api_plugin/plugins.basic_operations.data_threshold>
   Rescale Intensity <api_plugin/plugins.basic_operations.rescale_intensity>
   Value Substitution <api_plugin/plugins.basic_operations.value_substitution>
   Elementwise Arrays Arithmetics <api_plugin/plugins.basic_operations.elementwise_arrays_arithmetics>


Centering
########################################################

.. toctree::
   :maxdepth: 1 

   Vo Centering <api_plugin/plugins.centering.vo_centering>


Component Analysis
########################################################

.. toctree::
   :maxdepth: 1 

   Ica <api_plugin/plugins.component_analysis.ica>
   Pca <api_plugin/plugins.component_analysis.pca>


Corrections
########################################################

.. toctree::
   :maxdepth: 1 

   Camera Rot Correction <api_plugin/plugins.corrections.camera_rot_correction>
   Convert 360 180 Sinogram <api_plugin/plugins.corrections.convert_360_180_sinogram>
   Dark Flat Field Correction <api_plugin/plugins.corrections.dark_flat_field_correction>
   Distortion Correction <api_plugin/plugins.corrections.distortion_correction>
   Monitor Correction <api_plugin/plugins.corrections.monitor_correction>
   Mtf Deconvolution <api_plugin/plugins.corrections.mtf_deconvolution>
   Subpixel Shift <api_plugin/plugins.corrections.subpixel_shift>
   Time Based Correction <api_plugin/plugins.corrections.time_based_correction>
   Time Based Plus Drift Correction <api_plugin/plugins.corrections.time_based_plus_drift_correction>


Filters
########################################################

.. toctree::
   :maxdepth: 1 

   Band Pass <api_plugin/plugins.filters.band_pass>
   Pymca <api_plugin/plugins.filters.pymca>
   Find Peaks <api_plugin/plugins.filters.find_peaks>
   Fresnel Filter <api_plugin/plugins.filters.fresnel_filter>
   Hilbert Filter <api_plugin/plugins.filters.hilbert_filter>
   Image Interpolation <api_plugin/plugins.filters.image_interpolation>
   List To Projections <api_plugin/plugins.filters.list_to_projections>
   Paganin Filter <api_plugin/plugins.filters.paganin_filter>
   Poly Background Estimator <api_plugin/plugins.filters.poly_background_estimator>
   Quantisation Filter <api_plugin/plugins.filters.quantisation_filter>
   Spectrum Crop <api_plugin/plugins.filters.spectrum_crop>
   Strip Background <api_plugin/plugins.filters.strip_background>
   Threshold Filter <api_plugin/plugins.filters.threshold_filter>


Dezingers
********************************************************

.. toctree::
   :maxdepth: 1 

   Dezinger <api_plugin/plugins.filters.dezingers.dezinger>
   Dezinger Gpu <api_plugin/plugins.filters.dezingers.dezinger_gpu>
   Dezinger Simple Deprecated <api_plugin/plugins.filters.dezingers.dezinger_simple_deprecated>
   Dezinger Sinogram Deprecated <api_plugin/plugins.filters.dezingers.dezinger_sinogram_deprecated>


Inpainting
********************************************************

.. toctree::
   :maxdepth: 1 

   Inpainting <api_plugin/plugins.filters.inpainting.inpainting>


Denoising
********************************************************

.. toctree::
   :maxdepth: 1 

   Ccpi Denoising Cpu <api_plugin/plugins.filters.denoising.ccpi_denoising_cpu>
   Ccpi Denoising Cpu 3D <api_plugin/plugins.filters.denoising.ccpi_denoising_cpu_3D>
   Ccpi Denoising Gpu <api_plugin/plugins.filters.denoising.ccpi_denoising_gpu>
   Ccpi Denoising Gpu 3D <api_plugin/plugins.filters.denoising.ccpi_denoising_gpu_3D>
   Denoise Bregman Filter <api_plugin/plugins.filters.denoising.denoise_bregman_filter>
   Median Filter <api_plugin/plugins.filters.denoising.median_filter>
   Median Filter Deprecated <api_plugin/plugins.filters.denoising.median_filter_deprecated>
   Median Filter Gpu <api_plugin/plugins.filters.denoising.median_filter_gpu>


Fitters
########################################################

.. toctree::
   :maxdepth: 1 

   Simple Fit <api_plugin/plugins.fitters.simple_fit>


Kinematics
########################################################

.. toctree::
   :maxdepth: 1 

   Stage Motion <api_plugin/plugins.kinematics.stage_motion>


Loaders
########################################################

.. toctree::
   :maxdepth: 1 

   Hdf5 Template Loader <api_plugin/plugins.loaders.hdf5_template_loader>
   Image Template Loader <api_plugin/plugins.loaders.image_template_loader>
   Multi Savu Loader <api_plugin/plugins.loaders.multi_savu_loader>
   Random Hdf5 Loader <api_plugin/plugins.loaders.random_hdf5_loader>
   Savu Nexus Loader <api_plugin/plugins.loaders.savu_nexus_loader>
   Yaml Converter <api_plugin/plugins.loaders.yaml_converter>


Full Field Loaders
********************************************************

.. toctree::
   :maxdepth: 1 

   Dxchange Loader <api_plugin/plugins.loaders.full_field_loaders.dxchange_loader>
   Image Loader <api_plugin/plugins.loaders.full_field_loaders.image_loader>
   Mrc Loader <api_plugin/plugins.loaders.full_field_loaders.mrc_loader>
   Multi Nxtomo Loader <api_plugin/plugins.loaders.full_field_loaders.multi_nxtomo_loader>
   Nxtomo Loader <api_plugin/plugins.loaders.full_field_loaders.nxtomo_loader>
   Random 3D Tomo Loader <api_plugin/plugins.loaders.full_field_loaders.random_3d_tomo_loader>
   Lfov Loader <api_plugin/plugins.loaders.full_field_loaders.lfov_loader>


Mapping Loaders
********************************************************

.. toctree::
   :maxdepth: 1 

   Mm Loader <api_plugin/plugins.loaders.mapping_loaders.mm_loader>
   Nxfluo Loader <api_plugin/plugins.loaders.mapping_loaders.nxfluo_loader>
   Nxmonitor Loader <api_plugin/plugins.loaders.mapping_loaders.nxmonitor_loader>
   Nxstxm Loader <api_plugin/plugins.loaders.mapping_loaders.nxstxm_loader>
   Nxxrd Loader <api_plugin/plugins.loaders.mapping_loaders.nxxrd_loader>


Reconstructions
########################################################

.. toctree::
   :maxdepth: 1 

   Scikitimage Sart <api_plugin/plugins.reconstructions.scikitimage_sart>
   Scikitimage Filter Back Projection <api_plugin/plugins.reconstructions.scikitimage_filter_back_projection>
   Simple Recon <api_plugin/plugins.reconstructions.simple_recon>
   Tomopy Recon <api_plugin/plugins.reconstructions.tomopy_recon>
   Visual Hulls Recon <api_plugin/plugins.reconstructions.visual_hulls_recon>
   Ccpi Cgls Recon <api_plugin/plugins.reconstructions.ccpi_cgls_recon>


Astra Recons
********************************************************

.. toctree::
   :maxdepth: 1 

   Astra Recon Cpu <api_plugin/plugins.reconstructions.astra_recons.astra_recon_cpu>
   Astra Recon Gpu <api_plugin/plugins.reconstructions.astra_recons.astra_recon_gpu>


Projectors
********************************************************

.. toctree::
   :maxdepth: 1 

   Forward Projector Cpu <api_plugin/plugins.reconstructions.projectors.forward_projector_cpu>
   Forward Projector Gpu <api_plugin/plugins.reconstructions.projectors.forward_projector_gpu>


Tomobar
********************************************************

.. toctree::
   :maxdepth: 1 

   Tomobar Recon <api_plugin/plugins.reconstructions.tomobar.tomobar_recon>
   Tomobar Recon 3D <api_plugin/plugins.reconstructions.tomobar.tomobar_recon_3D>
   Tomobar Recon Cpu <api_plugin/plugins.reconstructions.tomobar.tomobar_recon_cpu>


Reshape
########################################################

.. toctree::
   :maxdepth: 1 

   Data Removal <api_plugin/plugins.reshape.data_removal>
   Downsample Filter <api_plugin/plugins.reshape.downsample_filter>
   Mipmap <api_plugin/plugins.reshape.mipmap>
   Image Stitching <api_plugin/plugins.reshape.image_stitching>


Ring Removal
########################################################

.. toctree::
   :maxdepth: 1 

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
   Ring Removal Interpolation <api_plugin/plugins.ring_removal.ring_removal_interpolation>


Savers
########################################################

.. toctree::
   :maxdepth: 1 

   Hdf5 Saver <api_plugin/plugins.savers.hdf5_saver>
   Image Saver <api_plugin/plugins.savers.image_saver>
   Tiff Saver <api_plugin/plugins.savers.tiff_saver>
   Xrf Saver <api_plugin/plugins.savers.xrf_saver>


Morphological Operations
********************************************************

.. toctree::
   :maxdepth: 1 

   Morph Proc <api_plugin/plugins.segmentation.morphological_operations.morph_proc>
   Morph Remove Objects <api_plugin/plugins.segmentation.morphological_operations.morph_remove_objects>
   Morph Proc Line3D <api_plugin/plugins.segmentation.morphological_operations.morph_proc_line3D>
   Morph Proc Line <api_plugin/plugins.segmentation.morphological_operations.morph_proc_line>


Evolving Contours
********************************************************

.. toctree::
   :maxdepth: 1 

   Morph Snakes <api_plugin/plugins.segmentation.evolving_contours.morph_snakes>
   Morph Snakes3D <api_plugin/plugins.segmentation.evolving_contours.morph_snakes3D>
   Region Grow <api_plugin/plugins.segmentation.evolving_contours.region_grow>
   Region Grow3D <api_plugin/plugins.segmentation.evolving_contours.region_grow3D>


Gaussian Mixtures
********************************************************

.. toctree::
   :maxdepth: 1 

   Gmm Segment3D <api_plugin/plugins.segmentation.gaussian_mixtures.gmm_segment3D>


Geo Distance
********************************************************

.. toctree::
   :maxdepth: 1 

   Geo Distance <api_plugin/plugins.segmentation.geo_distance.geo_distance>
   Geo Distance3D <api_plugin/plugins.segmentation.geo_distance.geo_distance3D>


Masks Initialise
********************************************************

.. toctree::
   :maxdepth: 1 

   Mask Initialiser <api_plugin/plugins.segmentation.masks_initialise.mask_initialiser>


Thresholding
********************************************************

.. toctree::
   :maxdepth: 1 

   Thresh Segm <api_plugin/plugins.segmentation.thresholding.thresh_segm>


Stats
########################################################

.. toctree::
   :maxdepth: 1 

   Min And Max <api_plugin/plugins.stats.min_and_max>


Visualisation
########################################################

.. toctree::
   :maxdepth: 1 

   Ortho Slice <api_plugin/plugins.visualisation.ortho_slice>


Simulation
########################################################

.. toctree::
   :maxdepth: 1 

   Tomo Phantom <api_plugin/plugins.simulation.tomo_phantom>
   Tomo Phantom Quantification <api_plugin/plugins.simulation.tomo_phantom_quantification>


