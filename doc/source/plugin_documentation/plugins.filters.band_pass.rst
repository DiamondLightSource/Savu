Band Pass
#################################################################

Description
--------------------------

A plugin to filter each frame with a BandPass T

    
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
        
        blur_width:
            visibility: basic
            dtype: tuple
            description: Kernel size
            default: (0, 3, 3)
        
        type:
            visibility: basic
            dtype: str
            description: Filter type (High|Low).
            options: ['High', 'Low']
            default: High
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml
