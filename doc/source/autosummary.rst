API Documentation 
===================
Information on specific functions, classes, and methods.
 
savu
------------------------------------------------------------

.. toctree::
   api/savu.tomo_recon
   api/savu.version


savu.core
------------------------------------------------------------

.. toctree::
   api/savu.core.utils
   api/savu.core.plugin_runner
   api/savu.core.dist_array_process
   api/savu.core.transport_setup


savu.core.transports
------------------------------------------------------------

.. toctree::
   api/savu.core.transports.hdf5_transport
   api/savu.core.transports.dist_array_utils
   api/savu.core.transports.base_transport
   api/savu.core.transports.dist_array_transport


savu.data
------------------------------------------------------------

.. toctree::
   api/savu.data.experiment_collection
   api/savu.data.plugin_list
   api/savu.data.chunking
   api/savu.data.meta_data
   api/savu.data.framework_citations


savu.data.transport_data
------------------------------------------------------------

.. toctree::
   api/savu.data.transport_data.hdf5_transport_data
   api/savu.data.transport_data.dist_array_transport_data
   api/savu.data.transport_data.base_transport_data


savu.data.data_structures
------------------------------------------------------------

.. toctree::
   api/savu.data.data_structures.data
   api/savu.data.data_structures.data_add_ons
   api/savu.data.data_structures.data_create
   api/savu.data.data_structures.data_notes
   api/savu.data.data_structures.plugin_data
   api/savu.data.data_structures.preview
   api/savu.data.data_structures.utils


savu.data.data_structures.data_types
------------------------------------------------------------

.. toctree::
   api/savu.data.data_structures.data_types.base_type
   api/savu.data.data_structures.data_types.data_plus_darks_and_flats
   api/savu.data.data_structures.data_types.fabIO
   api/savu.data.data_structures.data_types.map_3dto4d_h5
   api/savu.data.data_structures.data_types.mrc
   api/savu.data.data_structures.data_types.replicate
   api/savu.data.data_structures.data_types.stitch_data


savu.plugins
------------------------------------------------------------

.. toctree::
   api/savu.plugins.utils
   api/savu.plugins.plugin
   api/savu.plugins.plugin_datasets
   api/savu.plugins.plugin_datasets_notes


savu.plugins.others
------------------------------------------------------------

.. toctree::
   api/savu.plugins.others.basic_operations
   api/savu.plugins.others.no_process_plugin


savu.plugins.developing
------------------------------------------------------------

.. toctree::
   api/savu.plugins.developing.testing_sino_align


savu.plugins.absorption_corrections
------------------------------------------------------------

.. toctree::
   api/savu.plugins.absorption_corrections.mc_near_absorption_correction
   api/savu.plugins.absorption_corrections.base_absorption_correction


savu.plugins.ptychography
------------------------------------------------------------

.. toctree::
   api/savu.plugins.ptychography.dummy_ptycho
   api/savu.plugins.ptychography.ptypy_compact
   api/savu.plugins.ptychography.ptypy_batch
   api/savu.plugins.ptychography.base_ptycho


savu.plugins.azimuthal_integrators
------------------------------------------------------------

.. toctree::
   api/savu.plugins.azimuthal_integrators
   api/savu.plugins.azimuthal_integrators
   api/savu.plugins.azimuthal_integrators
   api/savu.plugins.azimuthal_integrators.base_azimuthal_integrator


savu.plugins.fitters
------------------------------------------------------------

.. toctree::
   api/savu.plugins.fitters.base_fitter
   api/savu.plugins.fitters.simple_fit
   api/savu.plugins.fitters.ral_fit
   api/savu.plugins.fitters.reproduce_fit


savu.plugins.component_analysis
------------------------------------------------------------

.. toctree::
   api/savu.plugins.component_analysis.ica
   api/savu.plugins.component_analysis.base_component_analysis
   api/savu.plugins.component_analysis.pca


savu.plugins.fluo_fitters
------------------------------------------------------------

.. toctree::
   api/savu.plugins.fluo_fitters.simple_fit_xrf
   api/savu.plugins.fluo_fitters.fastxrf_fitting
   api/savu.plugins.fluo_fitters.base_fluo_fitter


savu.plugins.analysis
------------------------------------------------------------

.. toctree::
   api/savu.plugins.analysis.stats
   api/savu.plugins.analysis.histogram


savu.plugins.reconstructions
------------------------------------------------------------

.. toctree::
   api/savu.plugins.reconstructions.base_astra_recon
   api/savu.plugins.reconstructions.cgls_recon
   api/savu.plugins.reconstructions.old_base_astra_recon
   api/savu.plugins.reconstructions.scikitimage_sart
   api/savu.plugins.reconstructions.simple_fake_gpu_recon
   api/savu.plugins.reconstructions.simple_recon
   api/savu.plugins.reconstructions.scikitimage_filter_back_projection
   api/savu.plugins.reconstructions.non_local_regularised_cgls
   api/savu.plugins.reconstructions.really_old_base_astra_recon
   api/savu.plugins.reconstructions.tomopy_recon
   api/savu.plugins.reconstructions.base_recon


savu.plugins.reconstructions.astra_recons
------------------------------------------------------------

.. toctree::
   api/savu.plugins.reconstructions.astra_recons.astra_recon_gpu
   api/savu.plugins.reconstructions.astra_recons.astra_recon_cpu


savu.plugins.reshape
------------------------------------------------------------

.. toctree::
   api/savu.plugins.reshape.data_removal
   api/savu.plugins.reshape.downsample_filter


savu.plugins.corrections
------------------------------------------------------------

.. toctree::
   api/savu.plugins.corrections.timeseries_field_corrections
   api/savu.plugins.corrections.dark_flat_field_correction
   api/savu.plugins.corrections.time_based_correction
   api/savu.plugins.corrections.time_based_plus_drift_correction
   api/savu.plugins.corrections.base_correction
   api/savu.plugins.corrections.monitor_correction


savu.plugins.driver
------------------------------------------------------------

.. toctree::
   api/savu.plugins.driver.all_cpus_plugin
   api/savu.plugins.driver.cpu_plugin
   api/savu.plugins.driver.gpu_plugin
   api/savu.plugins.driver.plugin_driver
   api/savu.plugins.driver.multi_threaded_plugin
   api/savu.plugins.driver.single_node_multi_threaded_plugin


savu.plugins.filters
------------------------------------------------------------

.. toctree::
   api/savu.plugins.filters.band_pass
   api/savu.plugins.filters.denoise_bregman_filter
   api/savu.plugins.filters.dezing_filter
   api/savu.plugins.filters.distortion_correction
   api/savu.plugins.filters.find_peaks
   api/savu.plugins.filters.median_filter
   api/savu.plugins.filters.paganin_filter
   api/savu.plugins.filters.raven_filter
   api/savu.plugins.filters.ring_artefact_filter
   api/savu.plugins.filters.sinogram_alignment
   api/savu.plugins.filters.spectrum_crop
   api/savu.plugins.filters.strip_background
   api/savu.plugins.filters.vo_centering
   api/savu.plugins.filters.dials_find_spots
   api/savu.plugins.filters.poly_background_estimator
   api/savu.plugins.filters.xrd_absorption_approximation
   api/savu.plugins.filters.sinogram_clean
   api/savu.plugins.filters.quantisation_filter
   api/savu.plugins.filters.projection_vertical_alignment
   api/savu.plugins.filters.projection_shift
   api/savu.plugins.filters.ring_removal_waveletfft
   api/savu.plugins.filters
   api/savu.plugins.filters.threshold_filter
   api/savu.plugins.filters.base_filter


savu.plugins.loaders
------------------------------------------------------------

.. toctree::
   api/savu.plugins.loaders.base_multi_modal_loader
   api/savu.plugins.loaders.mm_loader
   api/savu.plugins.loaders.nxtomo_loader
   api/savu.plugins.loaders.savu_loader
   api/savu.plugins.loaders.image_loader
   api/savu.plugins.loaders.multi_nxtomo_loader
   api/savu.plugins.loaders.i18_mm_loader
   api/savu.plugins.loaders.multi_savu_loader
   api/savu.plugins.loaders.p2r_fly_scan_detector_loader
   api/savu.plugins.loaders.mrc_loader
   api/savu.plugins.loaders.base_loader


savu.plugins.loaders.multi_modal_loaders
------------------------------------------------------------

.. toctree::
   api/savu.plugins.loaders.multi_modal_loaders.nxfluo_loader
   api/savu.plugins.loaders.multi_modal_loaders.nxmonitor_loader
   api/savu.plugins.loaders.multi_modal_loaders.nxstxm_loader
   api/savu.plugins.loaders.multi_modal_loaders.nxxrd_loader
   api/savu.plugins.loaders.multi_modal_loaders.base_i18_multi_modal_loader
   api/savu.plugins.loaders.multi_modal_loaders.nxptycho_loader
   api/savu.plugins.loaders.multi_modal_loaders.i13_ptycho_loader
   api/savu.plugins.loaders.multi_modal_loaders.i13_stxm_loader
   api/savu.plugins.loaders.multi_modal_loaders.i13_stxm_monitor_loader
   api/savu.plugins.loaders.multi_modal_loaders.i13_stxm_xrf_loader
   api/savu.plugins.loaders.multi_modal_loaders.txm_loader


savu.plugins.loaders.multi_modal_loaders.i18_loaders
------------------------------------------------------------

.. toctree::
   api/savu.plugins.loaders.multi_modal_loaders.i18_loaders.i18stxm_loader
   api/savu.plugins.loaders.multi_modal_loaders.i18_loaders.i18fluo_loader
   api/savu.plugins.loaders.multi_modal_loaders.i18_loaders.i18xrd_loader
   api/savu.plugins.loaders.multi_modal_loaders.i18_loaders.i13fluo_loader
   api/savu.plugins.loaders.multi_modal_loaders.i18_loaders.i18monitor_loader
   api/savu.plugins.loaders.multi_modal_loaders.i18_loaders.i22_tomo_loader


savu.plugins.loaders.utils
------------------------------------------------------------

.. toctree::
   api/savu.plugins.loaders.utils.mrc_header


savu.plugins.savers
------------------------------------------------------------

.. toctree::
   api/savu.plugins.savers.tiff_saver
   api/savu.plugins.savers.hdf5_saver
   api/savu.plugins.savers.base_saver


savu.plugins.savers.utils
------------------------------------------------------------

.. toctree::
   api/savu.plugins.savers.utils.hdf5_utils


savu.IMAGES
------------------------------------------------------------

.. toctree::


Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
