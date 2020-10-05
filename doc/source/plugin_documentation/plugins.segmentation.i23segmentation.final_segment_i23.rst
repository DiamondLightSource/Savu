Final Segment I23
#################################################################

Description
--------------------------

Apply at the end when all objects have been segmented independently (crystal, liquor, whole object)
    
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
        
        set_classes_val:
            visibility: basic
            dtype: list
            description: Set the values for all 4 classes (crystal, liquor, loop, vacuum).
            default: [255, 128, 64, 0]
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml
