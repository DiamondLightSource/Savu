Morph Remove Objects
#################################################################

Description
--------------------------

A Plugin to remove objects smaller than the specified size.
    
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
        
        min_size:
            visibility: basic
            dtype: int
            description: The smallest allowable object size.
            default: 64
        
        connectivity:
            visibility: basic
            dtype: int
            description: The connectivity defining the neighborhood of a pixel.
            default: 1
        
        pattern:
            visibility: intermediate
            dtype: str
            description: Pattern to apply this to.
            default: VOLUME_XZ
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml
