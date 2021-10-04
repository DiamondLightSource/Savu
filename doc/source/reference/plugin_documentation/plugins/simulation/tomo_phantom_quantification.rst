Tomo Phantom Quantification
########################################################

Description
--------------------------

A plugin to calculate some standard image quality metrics 

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
            description: Default out dataset names.
            default: "['quantification_values']"
        
        pattern:
            visibility: intermediate
            dtype: str
            options: "['SINOGRAM', 'PROJECTION', 'VOLUME_XZ']"
            description: Pattern to apply this to.
            default: SINOGRAM
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml
