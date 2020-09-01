Tiff Saver
#################################################################

Description
--------------------------

A class to save tomography data to tiff files
    
Parameter definitions
--------------------------

.. code-block:: yaml

        in_datasets:
            visibility: datasets
            dtype: list
            description: none
            default: []
        
        out_datasets:
            visibility: datasets
            dtype: list
            description: none
            default: []
        
        pattern:
            visibility: basic
            dtype: str
            description: How to slice the data
            default: VOLUME_XZ
        
        prefix:
            visibility: basic
            dtype: str
            description: Override the default output tiff file prefix.
            default: None
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml
