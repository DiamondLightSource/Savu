Autosummary 
==============
Information on specific functions, classes, and methods.
 
savu
------------------------------------------------------------

.. currentmodule::savu
.. autosummary::
   :toctree: api

   savu.tomo_recon
   savu.test_runner


savu.core
------------------------------------------------------------

.. currentmodule::savu.core
.. autosummary::
   :toctree: api

   savu.core.utils
   savu.core.plugin_runner
   savu.core.dist_array_process
   savu.core.transport_control


savu.core.transports
------------------------------------------------------------

.. currentmodule::savu.core.transports
.. autosummary::
   :toctree: api

   savu.core.transports.hdf5_transport
   savu.core.transports.dist_array_transport
   savu.core.transports.dist_array_utils


savu.data
------------------------------------------------------------

.. currentmodule::savu.data
.. autosummary::
   :toctree: api

   savu.data.data_structures
   savu.data.experiment_collection
   savu.data.plugin_list
   savu.data.transport_data
   savu.data.chunking
   savu.data.meta_data


savu.data.transport_data
------------------------------------------------------------

.. currentmodule::savu.data.transport_data
.. autosummary::
   :toctree: api

   savu.data.transport_data.hdf5_transport_data
   savu.data.transport_data.distArray_transport_data


savu.plugins
------------------------------------------------------------

.. currentmodule::savu.plugins
.. autosummary::
   :toctree: api

   savu.plugins.base_recon
   savu.plugins.utils
   savu.plugins.base_loader
   savu.plugins.base_saver
   savu.plugins.base_filter
   savu.plugins.plugin
   savu.plugins.plugin_datasets
   savu.plugins.test_plugin
   savu.plugins.base_correction
   savu.plugins.dimension_adder
   savu.plugins.simple_fit_xrf_bounded


savu.plugins.reconstructions
------------------------------------------------------------

.. currentmodule::savu.plugins.reconstructions
.. autosummary::
   :toctree: api

   savu.plugins.reconstructions.base_astra_recon
   savu.plugins.reconstructions.cgls_recon
   savu.plugins.reconstructions.scikitimage_sart
   savu.plugins.reconstructions.simple_fake_gpu_recon
   savu.plugins.reconstructions.simple_recon
   savu.plugins.reconstructions.scikitimage_filter_back_projection
   savu.plugins.reconstructions.old_base_astra_recon


savu.plugins.reconstructions.astra_recons
------------------------------------------------------------

.. currentmodule::savu.plugins.reconstructions.astra_recons
.. autosummary::
   :toctree: api

   savu.plugins.reconstructions.astra_recons.astra_recon_gpu
   savu.plugins.reconstructions.astra_recons.astra_recon_cpu


savu.plugins.corrections
------------------------------------------------------------

.. currentmodule::savu.plugins.corrections
.. autosummary::
   :toctree: api

   savu.plugins.corrections.i12_dark_flat_field_correction
   savu.plugins.corrections.timeseries_field_corrections


savu.plugins.driver
------------------------------------------------------------

.. currentmodule::savu.plugins.driver
.. autosummary::
   :toctree: api

   savu.plugins.driver.all_cpus_plugin
   savu.plugins.driver.cpu_plugin
   savu.plugins.driver.gpu_plugin
   savu.plugins.driver.plugin_driver


savu.plugins.filters
------------------------------------------------------------

.. currentmodule::savu.plugins.filters
.. autosummary::
   :toctree: api

   savu.plugins.filters.band_pass
   savu.plugins.filters.base_fitter
   savu.plugins.filters.denoise_bregman_filter
   savu.plugins.filters.dezing_filter
   savu.plugins.filters.distortion_correction
   savu.plugins.filters.downsample_filter
   savu.plugins.filters.fastxrf_fitting
   savu.plugins.filters.find_peaks
   savu.plugins.filters.median_filter
   savu.plugins.filters.paganin_filter
   savu.plugins.filters.raven_filter
   savu.plugins.filters.ring_artefact_filter
   savu.plugins.filters.sinogram_alignment
   savu.plugins.filters.spectrum_crop
   savu.plugins.filters.stats
   savu.plugins.filters.strip_background
   savu.plugins.filters.vo_centering
   savu.plugins.filters.base_component_analysis
   savu.plugins.filters.dials_find_spots
   savu.plugins.filters.monitor_correction
   savu.plugins.filters.histogram
   savu.plugins.filters.no_process_plugin
   savu.plugins.filters.base_azimuthal_integrator
   savu.plugins.filters.poly_background_estimator


savu.plugins.filters.component_analysis
------------------------------------------------------------

.. currentmodule::savu.plugins.filters.component_analysis
.. autosummary::
   :toctree: api

   savu.plugins.filters.component_analysis.ica


savu.plugins.filters.fitters
------------------------------------------------------------

.. currentmodule::savu.plugins.filters.fitters
.. autosummary::
   :toctree: api

   savu.plugins.filters.fitters.base_fluo_fitter
   savu.plugins.filters.fitters.simple_fit


savu.plugins.filters.fitters.fluo_fitters
------------------------------------------------------------

.. currentmodule::savu.plugins.filters.fitters.fluo_fitters
.. autosummary::
   :toctree: api

   savu.plugins.filters.fitters.fluo_fitters.simple_fit_xrf


savu.plugins.filters.azimuthal_integrators
------------------------------------------------------------

.. currentmodule::savu.plugins.filters.azimuthal_integrators
.. autosummary::
   :toctree: api

   savu.plugins.filters.azimuthal_integrators
   savu.plugins.filters.azimuthal_integrators


savu.plugins.loaders
------------------------------------------------------------

.. currentmodule::savu.plugins.loaders
.. autosummary::
   :toctree: api

   savu.plugins.loaders.base_multi_modal_loader
   savu.plugins.loaders.mm_loader
   savu.plugins.loaders.nxtomo_loader
   savu.plugins.loaders.projection_tomo_loader
   savu.plugins.loaders.i12_tomo_loader
   savu.plugins.loaders.savu_loader
   savu.plugins.loaders.i18loader


savu.plugins.loaders.multi_modal_loaders
------------------------------------------------------------

.. currentmodule::savu.plugins.loaders.multi_modal_loaders
.. autosummary::
   :toctree: api

   savu.plugins.loaders.multi_modal_loaders.nxfluo_loader
   savu.plugins.loaders.multi_modal_loaders.nxmonitor_loader
   savu.plugins.loaders.multi_modal_loaders.nxstxm_loader
   savu.plugins.loaders.multi_modal_loaders.nxxrd_loader
   savu.plugins.loaders.multi_modal_loaders.nxxrd_loader_old


savu.plugins.savers
------------------------------------------------------------

.. currentmodule::savu.plugins.savers
.. autosummary::
   :toctree: api

   savu.plugins.savers.hdf5_tomo_saver


