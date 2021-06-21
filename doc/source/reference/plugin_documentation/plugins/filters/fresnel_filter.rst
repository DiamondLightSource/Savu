Fresnel Filter
########################################################

Description
--------------------------

A low-pass filter to improve the contrast of reconstructed images which is similar to the Paganin filter but can work on both sinograms and projections. 

.. toctree::
    Plugin documention and guidelines on use </../../../plugin_guides/plugins/filters/fresnel_filter_doc.rst>

Parameter definitions
--------------------------

.. code-block:: yaml

        in_datasets:
            visibility: datasets
            dtype: "[list[],list[str]]"
            description: 
                summary: A list of the dataset(s) to process.
                verbose: A list of strings, where each string gives the name of a dataset that was either specified by a loader plugin or created as output to a previous plugin.  The length of the list is the number of input datasets requested by the plugin.  If there is only one dataset and the list is left empty it will default to that dataset.
            default: "[]"
        
        out_datasets:
            visibility: datasets
            dtype: "[list[],list[str]]"
            description: 
                summary: A list of the dataset(s) to create.
                verbose: A list of strings, where each string is a name to be assigned to a dataset output by the plugin. If there is only one input dataset and one output dataset and the list is left empty, the output will take the name of the input dataset. The length of the list is the number of output datasets created by the plugin.
            default: "[]"
        
        ratio:
            visibility: basic
            dtype: float
            description: Control the strength of the filter. Greater is stronger
            default: "100.0"
        
        pattern:
            visibility: basic
            dtype: str
            description: Data processing pattern
            options: "['PROJECTION', 'SINOGRAM']"
            default: SINOGRAM
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml

Citations
--------------------------

The filter built is based on the Fresnel propagator
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
