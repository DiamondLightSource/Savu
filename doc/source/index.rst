.. Savu documentation master file, created by
   sphinx-quickstart on Tue Sep 16 10:25:51 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. include:: ../../README.rst

User and Developer Guide
========================

.. toctree::
   :maxdepth: 2
   
   user
   dev

Code Documentation
==================

.. autosummary::
   :toctree: _autosummary
   
   savu
   savu.core
   savu.core.process
   savu.data
   savu.data.process_data
   savu.data.structures
   savu.plugins
   savu.plugins.utils
   savu.plugins.plugin
   savu.plugins.cpu_plugin
   savu.plugins.gpu_plugin
   savu.plugins.timeseries_field_corrections
   savu.plugins.filter
   savu.plugins.median_filter
   savu.plugins.pass_through_plugin
   savu.plugins.vo_centering
   savu.plugins.base_recon
   savu.plugins.astra_recon
   savu.plugins.simple_fake_gpu_recon
   savu.plugins.simple_recon

Another Try at autodoc
======================

.. automodule:: savu
   :members:


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

