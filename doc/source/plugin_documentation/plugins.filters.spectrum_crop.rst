Spectrum Crop
#################################################################

Description
--------------------------

Crops a spectrum to a range
    
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
        
        crop_range:
            visibility: intermediate
            dtype: list
            description: Range to crop to.
            default: [2.0, 18.0]
        
        axis:
            visibility: intermediate
            dtype: str
            description: Axis.
            default: energy
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml
