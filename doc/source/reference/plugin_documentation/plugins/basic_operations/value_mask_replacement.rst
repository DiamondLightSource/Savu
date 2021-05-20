Value Mask Replacement
#################################################################

Description
--------------------------

The function looks for a specific value in the provided second array
(e.g. a mask) and substitutes the value in the first array with a given value.
    
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
        
        seek_value:
            visibility: basic
            dtype: int
            description: The value to be located in the provided second array.
            default: 0
        
        new_value:
            visibility: basic
            dtype: int
            description: The value to be replaced with in the first array.
            default: 1
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml
