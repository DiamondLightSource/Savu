Stats
#################################################################

Parameter definitions
--------------------------

.. code-block:: yaml

        in_datasets:
            visibility: datasets
            dtype: list
            description: Create a list of the dataset(s) to process
            default: []
        
        out_datasets:
            visibility: datasets
            dtype: list
            description: the output dataset.
            default: ['stats']
        
        required_stats:
            visibility: intermediate
            dtype: list
            description: Create a list of required stats calcs.
            default: ['max']
        
        direction:
            visibility: intermediate
            dtype: str
            description: Which direction to perform this.
            default: PROJECTION
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml
