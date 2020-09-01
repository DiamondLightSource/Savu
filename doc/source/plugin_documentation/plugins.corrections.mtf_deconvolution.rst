Mtf Deconvolution
#################################################################

Description
--------------------------

Method to correct the point-spread-function effect.
Working on raw projections and flats.
    
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
        
        file_path:
            visibility: intermediate
            dtype: filepath
            description: "Path to file containing a 2D array of a MTF function. File formats are 'npy', or 'tif'."
            default: None
        
        pad_width:
            visibility: intermediate
            dtype: int
            description: Pad the image before the deconvolution.
            default: 128
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml
