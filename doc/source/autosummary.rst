API Documentation 
===================
Information on specific functions, classes, and methods.
 
savu
------------------------------------------------------------

.. toctree::
   api/savu.tomo_recon
   api/savu.test_runner


savu.core
------------------------------------------------------------

.. toctree::
   api/savu.core.utils
   api/savu.core.plugin_runner
   api/savu.core.dist_array_process
   api/savu.core.transport_control


savu.core.transports
------------------------------------------------------------

.. toctree::
   api/savu.core.transports.hdf5_transport
   api/savu.core.transports.dist_array_transport
   api/savu.core.transports.dist_array_utils


savu.data
------------------------------------------------------------

.. toctree::
   api/savu.data.experiment_collection
   api/savu.data.plugin_list
   api/savu.data.chunking
   api/savu.data.meta_data
   api/savu.data.transport_data


savu.data.transport_data
------------------------------------------------------------

.. toctree::
   api/savu.data.transport_data.hdf5_transport_data
   api/savu.data.transport_data.distArray_transport_data


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
   api/savu.data.data_structures.data_type


savu.plugins
------------------------------------------------------------

.. toctree::
   api/savu.plugins.base_recon
   api/savu.plugins.utils
   api/savu.plugins.base_loader
   api/savu.plugins.base_saver
   api/savu.plugins.base_filter
   api/savu.plugins.plugin
   api/savu.plugins.base_correction
   api/savu.plugins.plugin_datasets
   api/savu.plugins.basic_operations
   api/savu.plugins.plugin_datasets_notes


savu.plugins.reconstructions
------------------------------------------------------------

.. toctree::
   api/savu.plugins.reconstructions.base_astra_recon
   api/savu.plugins.reconstructions.cgls_recon
   api/savu.plugins.reconstructions.scikitimage_sart
   api/savu.plugins.reconstructions.simple_fake_gpu_recon
   api/savu.plugins.reconstructions.simple_recon
   api/savu.plugins.reconstructions.scikitimage_filter_back_projection
   api/savu.plugins.reconstructions.old_base_astra_recon


savu.plugins.reconstructions.astra_recons
------------------------------------------------------------

.. toctree::
   api/savu.plugins.reconstructions.astra_recons.astra_recon_gpu
   api/savu.plugins.reconstructions.astra_recons.astra_recon_cpu


savu.plugins.corrections
------------------------------------------------------------

.. toctree::
   api/savu.plugins.corrections.i12_dark_flat_field_correction
   api/savu.plugins.corrections.timeseries_field_corrections


savu.plugins.driver
------------------------------------------------------------

.. toctree::
   api/savu.plugins.driver.all_cpus_plugin
   api/savu.plugins.driver.cpu_plugin
   api/savu.plugins.driver.gpu_plugin
   api/savu.plugins.driver.plugin_driver


savu.plugins.filters
------------------------------------------------------------

.. toctree::
   api/savu.plugins.filters.band_pass
   api/savu.plugins.filters.base_fitter
   api/savu.plugins.filters.denoise_bregman_filter
   api/savu.plugins.filters.dezing_filter
   api/savu.plugins.filters.distortion_correction
   api/savu.plugins.filters.downsample_filter
   api/savu.plugins.filters.no_process_plugin
   api/savu.plugins.filters.find_peaks
   api/savu.plugins.filters.median_filter
   api/savu.plugins.filters.paganin_filter
   api/savu.plugins.filters.raven_filter
   api/savu.plugins.filters.ring_artefact_filter
   api/savu.plugins.filters.sinogram_alignment
   api/savu.plugins.filters.spectrum_crop
   api/savu.plugins.filters.stats
   api/savu.plugins.filters.strip_background
   api/savu.plugins.filters.vo_centering
   api/savu.plugins.filters.base_component_analysis
   api/savu.plugins.filters.dials_find_spots
   api/savu.plugins.filters.monitor_correction
   api/savu.plugins.filters.histogram
   api/savu.plugins.filters.base_azimuthal_integrator
   api/savu.plugins.filters.poly_background_estimator
   api/savu.plugins.filters.old_centering
   api/savu.plugins.filters.base_absorption_correction


savu.plugins.filters.component_analysis
------------------------------------------------------------

.. toctree::
   api/savu.plugins.filters.component_analysis.ica


savu.plugins.filters.fitters
------------------------------------------------------------

.. toctree::
   api/savu.plugins.filters.fitters.base_fluo_fitter
   api/savu.plugins.filters.fitters.simple_fit


savu.plugins.filters.fitters.fluo_fitters
------------------------------------------------------------

.. toctree::
   api/savu.plugins.filters.fitters.fluo_fitters.simple_fit_xrf
   api/savu.plugins.filters.fitters.fluo_fitters.fastxrf_fitting


savu.plugins.filters.azimuthal_integrators
------------------------------------------------------------

.. toctree::
   api/savu.plugins.filters.azimuthal_integrators
   api/savu.plugins.filters.azimuthal_integrators
   api/savu.plugins.filters.azimuthal_integrators


savu.plugins.filters.absorption_corrections
------------------------------------------------------------

.. toctree::
   api/savu.plugins.filters.absorption_corrections.hogan_absorption_correction


savu.plugins.loaders
------------------------------------------------------------

.. toctree::
   api/savu.plugins.loaders.base_multi_modal_loader
   api/savu.plugins.loaders.mm_loader
   api/savu.plugins.loaders.nxtomo_loader
   api/savu.plugins.loaders.savu_loader
   api/savu.plugins.loaders.image_loader
   api/savu.plugins.loaders.i18_mm_loader


savu.plugins.loaders.multi_modal_loaders
------------------------------------------------------------

.. toctree::
   api/savu.plugins.loaders.multi_modal_loaders.nxfluo_loader
   api/savu.plugins.loaders.multi_modal_loaders.nxmonitor_loader
   api/savu.plugins.loaders.multi_modal_loaders.nxstxm_loader
   api/savu.plugins.loaders.multi_modal_loaders.nxxrd_loader
   api/savu.plugins.loaders.multi_modal_loaders.base_i18_multi_modal_loader
   api/savu.plugins.loaders.multi_modal_loaders.nxptycho_loader


savu.plugins.loaders.multi_modal_loaders.i18_loaders
------------------------------------------------------------

.. toctree::
   api/savu.plugins.loaders.multi_modal_loaders.i18_loaders.i18stxm_loader
   api/savu.plugins.loaders.multi_modal_loaders.i18_loaders.i18fluo_loader
   api/savu.plugins.loaders.multi_modal_loaders.i18_loaders.i18xrd_loader
   api/savu.plugins.loaders.multi_modal_loaders.i18_loaders.i13fluo_loader
   api/savu.plugins.loaders.multi_modal_loaders.i18_loaders.i18monitor_loader


savu.plugins.savers
------------------------------------------------------------

.. toctree::
   api/savu.plugins.savers.hdf5_tomo_saver


Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
