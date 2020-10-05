Threshold Filter
#################################################################

Description
--------------------------

A plugin to quantise an image into discrete levels.

    
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
        
        explicit_threshold:
            visibility: basic
            dtype: bool
            description: "False if plugin calculates black/white threshold, True if it's user-defined."
            default: True
        
        intensity_threshold:
            visibility: basic
            dtype: int
            description: Threshold for black/white quantisation.
            default: 32768
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml
