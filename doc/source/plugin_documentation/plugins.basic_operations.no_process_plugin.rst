No Process Plugin
#################################################################

Description
--------------------------

The base class from which all plugins should inherit.
    
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
        
        pattern:
            visibility: intermediate
            dtype: list
            description: Explicitly state the slicing pattern.
            default: None
        
        dummy:
            visibility: basic
            dtype: int
            description: Dummy parameter for testing.
            default: 10
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml
