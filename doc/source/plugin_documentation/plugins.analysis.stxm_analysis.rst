Stxm Analysis
#################################################################

Description
--------------------------

This plugin performs basic STXM analysis of diffraction patterns.
    
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
            description:
            default: ['bf', 'df', 'dpc_x', 'dpc_y', 'combined_dpc']
        
        mask_file:
            visibility: basic
            dtype: list
            description: Takes in a mask currently in hdf format.
            default: None
        
        mask_path:
            visibility: intermediate
            dtype: int_path
            description: Path to the mask inside the file.
            default: /mask
        
        threshold:
            visibility: intermediate
            dtype: float
            description: Intensity threshold for the dark field.
            default: 0.05
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml
