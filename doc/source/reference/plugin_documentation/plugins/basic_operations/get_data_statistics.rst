Get Data Statistics
########################################################

Description
--------------------------

Collects data global statistcs (max, min, sum, mean) and put it in metadata. 

Parameters
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
            description: The default names
            default: "['data', 'data_statistics']"
        
        pattern:
            visibility: intermediate
            dtype: str
            options: "['SINOGRAM', 'PROJECTION', 'VOLUME_XZ', 'VOLUME_YZ']"
            description: Pattern to apply this to.
            default: VOLUME_XZ
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml
