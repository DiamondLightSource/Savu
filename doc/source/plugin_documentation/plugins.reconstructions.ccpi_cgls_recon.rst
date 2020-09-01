Ccpi Cgls Recon
#################################################################

Description
--------------------------

A Plugin to run the CCPi implementation of the CGLS reconstruction
algorithm.
    
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
        
        centre_of_rotation:
            visibility: basic
            dtype: ['float', 'int']
            description: Centre of rotation to use for the reconstruction.
            default: 0.0
            example: It could be scalar or list of centre of rotation
        
        init_vol:
            visibility: advanced
            dtype: str
            description: Not an option.
            default: None
        
        centre_pad:
            visibility: hidden
            dtype: int
            description: Not an option.
            default: False
        
        outer_pad:
            visibility: advanced
            dtype: str
            description: Not an option.
            default: False
        
        log:
            visibility: advanced
            dtype: bool
            description: 
                summary: Take the log of the data before reconstruction (true or false).
                verbose: Should be set to false if PaganinFilter is set beforehand
            default: True
            example: Set to True to take the log of the data before reconstruction
        
        preview:
            visibility: advanced
            dtype: list
            description: A slice list of required frames.
            default: "[]"
            example: "[angle, detectorZ, detectorY], where detectorZ is the vertical coordinate, detectorY is the horizontal coordinate."
        
        force_zero:
            visibility: intermediate
            dtype: range
            description: Set any values in the reconstructed image outside of this range to zero.
            default: "[None, None]"
            example: "[0,1]"
        
        ratio:
            visibility: intermediate
            dtype: float
            description: Ratio of the masks diameter in pixels to the smallest edge size along given axis.
            default: 0.95
            example: "Is this a proper name for this parameter? Would mask_diameter or mask_circle be more accurate?"
        
        log_func:
            visibility: advanced
            dtype: str
            description: Override the default log function
            default: np.nan_to_num(-np.log(sino))
            example: You write a function as default
        
        vol_shape:
            visibility: basic
            dtype: ['str', 'int']
            description: 
                summary: Override the size of the reconstuction volume with an integer value.
                verbose: When fixed, you get the dimension of the horizontal detector Or you can specify any reconstruction size you like with an integer.
            default: fixed
        
        n_iterations:
            visibility: basic
            dtype: tuple
            description: Number of rows and columns in the reconstruction.
            default: 5
        
        resolution:
            visibility: basic
            dtype: str
            description: Number of output voxels (res = n_pixels/n_voxels), set res > 1 for reduced resolution.
            default: 1
        
        n_frames:
            visibility: basic
            dtype: int
            description: This algorithm requires a multiple of 8 frames for processing and this number may affect performance depending on your data size (choose from 8, 16, 24, 32)
            options: [8, 16, 24, 32]
            default: 16
        
        enforce_position:
            visibility: advanced
            dtype: int
            description: Not an option.
            default: False
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml
