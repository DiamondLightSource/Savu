.. _plugin_templates:

Plugin templates 
=======================

Plugin Template With Detailed Notes 1
------------------------------------------------------------------

A template to create a simple plugin that takes one dataset as input and returns a similar dataset as output

.. list-table::  
   :widths: 10

   * - :ref:`plugin_template1_with_detailed_notes`

Further Examples
------------------------------------------------------------------

.. list-table::  
   :widths: 10 90
   :header-rows: 1

   * - Link
     - Description
   * - :ref:`plugin_template1`
     - A simple plugin template with one in_dataset and one out_dataset with similar characteristics, e.g. median filter. 

   * - :ref:`plugin_template2`
     - A simple plugin template with multiple input and output datasets. 

   * - :ref:`plugin_template3`
     - A plugin template that reduces the data dimensions, e.g. azimuthal integration. 

   * - :ref:`plugin_template4`
     - A template for a plugin that takes in two datasets and returns one dataset, e.g. absorption correction. 

   * - :ref:`plugin_template5`
     - A plugin template with one in_dataset and two out_datasets that do not resemble the in_dataset and are not retained by the framework, e.g. vo_centering. 

   * - :ref:`plugin_template6`
     - A template to create a plugin that changes the shape of the data, e.g. downsample_filter. 

   * - :ref:`plugin_template7`
     - A plugin template that increases the data dimensions. 

   * - :ref:`plugin_template8`
     - A plugin template that dynamically determines the number of output datasets based on the number of entries in the out_datasets parameter list. 

   * - :ref:`plugin_template10`
     - A plugin template that dynamically determines the number of input datasets based on the number of entries in the in_datasets parameter list. 

