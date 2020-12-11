What is a Savu plugin
************************

A plugin is a short program which takes a piece of data as input and manipulates
it in a certain way. Each plugin performs a specific independent task, such as correction, \
filtering or reconstruction.

Plugins are grouped into categories of similar functionality. Loaders and \
savers are two of these categories. Each process list must begin with a \
loader plugin and end with a saver plugin (hdf5 is the default), \
with at least one processing plugin in-between. The loader informs the framework \
of the data location and format along with important metadata such as shape, \
axis information, and associated patterns (e.g. sinogram, projection). \
Therefore, the choice of loader is dependent upon the format of the data.

Tasks which plugins may perform:

    - Absorption correction
    - Alignment
    - Analysis
    - Centering
    - Corrections
    - Filtering
    - Fitting
    - Ring removal
    - Reconstruction
    - Segmentation

For a list of available plugins \
see :ref:`plugin documentation<plugin_documentation>`.

1. Plugin Module
================

This file contains your plugin definitions and statements.

For a list of templates, visit the :ref:`plugin template<plugin_templates>` page.


2. Plugin Tools Module
======================

This tools module contains the parameter details and citations in a yaml format. You can \
assign each parameter a data type, a description, a visibility level and a \
default value.

View further information about :ref:`plugin tools<toolclassguide>`