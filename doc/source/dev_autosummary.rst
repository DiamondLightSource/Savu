API Documentation 
===================
Information on specific functions, classes, and methods.
 
savu
------------------------------------------------------------

.. toctree::
   api_plugin_dev/savu.tomo_recon
   api_plugin_dev/savu.test_runner


savu.core
------------------------------------------------------------

.. toctree::
   api_plugin_dev/savu.core.utils
   api_plugin_dev/savu.core.plugin_runner
   api_plugin_dev/savu.core.dist_array_process
   api_plugin_dev/savu.core.transport_control


savu.core.transports
------------------------------------------------------------

.. toctree::
   api_plugin_dev/savu.core.transports.hdf5_transport
   api_plugin_dev/savu.core.transports.dist_array_transport
   api_plugin_dev/savu.core.transports.dist_array_utils


savu.data
------------------------------------------------------------

.. toctree::
   api_plugin_dev/savu.data.experiment_collection
   api_plugin_dev/savu.data.plugin_list
   api_plugin_dev/savu.data.transport_data
   api_plugin_dev/savu.data.chunking
   api_plugin_dev/savu.data.meta_data


savu.data.transport_data
------------------------------------------------------------

.. toctree::
   api_plugin_dev/savu.data.transport_data.hdf5_transport_data
   api_plugin_dev/savu.data.transport_data.distArray_transport_data


savu.data.data_structures
------------------------------------------------------------

.. toctree::
   api_plugin_dev/savu.data.data_structures.utils
   api_plugin_dev/savu.data.data_structures.data
   api_plugin_dev/savu.data.data_structures.plugin_data
   api_plugin_dev/savu.data.data_structures.data_create
   api_plugin_dev/savu.data.data_structures.preview
   api_plugin_dev/savu.data.data_structures.data_notes
   api_plugin_dev/savu.data.data_structures.data_add_ons


savu.plugins
------------------------------------------------------------

.. toctree::
   api_plugin_dev/savu.plugins.base_recon
   api_plugin_dev/savu.plugins.utils
   api_plugin_dev/savu.plugins.base_loader
   api_plugin_dev/savu.plugins.base_saver
   api_plugin_dev/savu.plugins.base_filter
   api_plugin_dev/savu.plugins.plugin
   api_plugin_dev/savu.plugins.plugin_datasets_notes
   api_plugin_dev/savu.plugins.plugin_datasets
   api_plugin_dev/savu.plugins.test_plugin
   api_plugin_dev/savu.plugins.base_correction
   api_plugin_dev/savu.plugins.dimension_adder
   api_plugin_dev/savu.plugins.simple_fit_xrf_bounded


savu.plugins.reconstructions
------------------------------------------------------------

.. toctree::
   api_plugin_dev/savu.plugins.reconstructions.base_astra_recon
   api_plugin_dev/savu.plugins.reconstructions.cgls_recon
   api_plugin_dev/savu.plugins.reconstructions.scikitimage_sart
   api_plugin_dev/savu.plugins.reconstructions.simple_fake_gpu_recon
   api_plugin_dev/savu.plugins.reconstructions.simple_recon
   api_plugin_dev/savu.plugins.reconstructions.scikitimage_filter_back_projection
   api_plugin_dev/savu.plugins.reconstructions.old_base_astra_recon


savu.plugins.reconstructions.astra_recons
------------------------------------------------------------

.. toctree::
   api_plugin_dev/savu.plugins.reconstructions.astra_recons.astra_recon_gpu
   api_plugin_dev/savu.plugins.reconstructions.astra_recons.astra_recon_cpu


savu.plugins.corrections
------------------------------------------------------------

.. toctree::
   api_plugin_dev/savu.plugins.corrections.i12_dark_flat_field_correction
   api_plugin_dev/savu.plugins.corrections.timeseries_field_corrections


savu.plugins.driver
------------------------------------------------------------

.. toctree::
   api_plugin_dev/savu.plugins.driver.all_cpus_plugin
   api_plugin_dev/savu.plugins.driver.cpu_plugin
   api_plugin_dev/savu.plugins.driver.gpu_plugin
   api_plugin_dev/savu.plugins.driver.plugin_driver


savu.plugins.filters
------------------------------------------------------------

.. toctree::
   api_plugin_dev/savu.plugins.filters.band_pass
   api_plugin_dev/savu.plugins.filters.base_fitter
   api_plugin_dev/savu.plugins.filters.denoise_bregman_filter
   api_plugin_dev/savu.plugins.filters.dezing_filter
   api_plugin_dev/savu.plugins.filters.distortion_correction
   api_plugin_dev/savu.plugins.filters.downsample_filter
   api_plugin_dev/savu.plugins.filters.fastxrf_fitting
   api_plugin_dev/savu.plugins.filters.find_peaks
   api_plugin_dev/savu.plugins.filters.median_filter
   api_plugin_dev/savu.plugins.filters.paganin_filter
   api_plugin_dev/savu.plugins.filters.raven_filter
   api_plugin_dev/savu.plugins.filters.ring_artefact_filter
   api_plugin_dev/savu.plugins.filters.sinogram_alignment
   api_plugin_dev/savu.plugins.filters.spectrum_crop
   api_plugin_dev/savu.plugins.filters.stats
   api_plugin_dev/savu.plugins.filters.strip_background
   api_plugin_dev/savu.plugins.filters.vo_centering
   api_plugin_dev/savu.plugins.filters.base_component_analysis
   api_plugin_dev/savu.plugins.filters.dials_find_spots
   api_plugin_dev/savu.plugins.filters.monitor_correction
   api_plugin_dev/savu.plugins.filters.histogram
   api_plugin_dev/savu.plugins.filters.no_process_plugin
   api_plugin_dev/savu.plugins.filters.base_azimuthal_integrator
   api_plugin_dev/savu.plugins.filters.poly_background_estimator


savu.plugins.filters.component_analysis
------------------------------------------------------------

.. toctree::
   api_plugin_dev/savu.plugins.filters.component_analysis.ica


savu.plugins.filters.fitters
------------------------------------------------------------

.. toctree::
   api_plugin_dev/savu.plugins.filters.fitters.base_fluo_fitter
   api_plugin_dev/savu.plugins.filters.fitters.simple_fit


savu.plugins.filters.fitters.fluo_fitters
------------------------------------------------------------

.. toctree::
   api_plugin_dev/savu.plugins.filters.fitters.fluo_fitters.simple_fit_xrf


savu.plugins.filters.azimuthal_integrators
------------------------------------------------------------

.. toctree::
   api_plugin_dev/savu.plugins.filters.azimuthal_integrators
   api_plugin_dev/savu.plugins.filters.azimuthal_integrators


savu.plugins.loaders
------------------------------------------------------------

.. toctree::
   api_plugin_dev/savu.plugins.loaders.base_multi_modal_loader
   api_plugin_dev/savu.plugins.loaders.mm_loader
   api_plugin_dev/savu.plugins.loaders.nxtomo_loader
   api_plugin_dev/savu.plugins.loaders.projection_tomo_loader
   api_plugin_dev/savu.plugins.loaders.i12_tomo_loader
   api_plugin_dev/savu.plugins.loaders.savu_loader
   api_plugin_dev/savu.plugins.loaders.i18loader


savu.plugins.loaders.multi_modal_loaders
------------------------------------------------------------

.. toctree::
   api_plugin_dev/savu.plugins.loaders.multi_modal_loaders.nxfluo_loader
   api_plugin_dev/savu.plugins.loaders.multi_modal_loaders.nxmonitor_loader
   api_plugin_dev/savu.plugins.loaders.multi_modal_loaders.nxstxm_loader
   api_plugin_dev/savu.plugins.loaders.multi_modal_loaders.nxxrd_loader
   api_plugin_dev/savu.plugins.loaders.multi_modal_loaders.nxxrd_loader_old


savu.plugins.savers
------------------------------------------------------------

.. toctree::
   api_plugin_dev/savu.plugins.savers.hdf5_tomo_saver


Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
