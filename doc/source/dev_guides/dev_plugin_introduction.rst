What is a Savu plugin
************************

Each plugin performs a specific independent task, such as correction, \
filtering or reconstruction.  For a list of available plugins \
see :ref:`plugin documentation<plugin_documentation>`.

Plugins are grouped into categories of similar functionality.  Loaders and \
savers are two of these categories and each process list must begin with a \
loader plugin and optionally end with a saver plugin (hdf5 is the default), \
with at least one processing plugin in-between. The loader informs the framework \
of the data location and format along with important metadata such as shape, \
axis information, and associated patterns (e.g. sinogram, projection). \
Therefore, the choice of loader is dependent upon the format of the data.


1. Plugin Module
================

This file contains your plugin definitions and statements.


2. Plugin Tools Module
======================

This tools module contains the parameter details in a yaml format. You can \
assign each parameter a data type, a description, a visibility level and a \
default value.

