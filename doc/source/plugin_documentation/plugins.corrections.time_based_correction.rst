Time Based Correction
#################################################################

Description
--------------------------

Apply a time-based dark and flat field correction to data.
    
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
            description: Create a list of the dataset(s) to create
            default: []
        
        in_range:
            visibility: basic
            dtype: ['range', 'bool']
            description: "Set to True if you require values in the range [0, 1]."
            default: False
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml
