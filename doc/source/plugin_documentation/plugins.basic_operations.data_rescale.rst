Data Rescale
#################################################################

Description
--------------------------

The plugin performs stretching or shrinking the data intensity levels
based on skimage rescale_intensity module. Min-max scalars for rescaling can
be passed from METADATA OR by providing as an input.

    
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
        
        min_value:
            visibility: basic
            dtype: int
            description: the global minimum data value.
            default: None
        
        max_value:
            visibility: basic
            dtype: int
            description: the global maximum data value.
            default: None
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml
