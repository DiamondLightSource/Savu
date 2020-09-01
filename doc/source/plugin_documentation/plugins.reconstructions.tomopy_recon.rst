Tomopy Recon
#################################################################

Description
--------------------------

A wrapper to the tomopy reconstruction library. Extra keywords not
required for the chosen algorithm will be ignored.
    
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
            visibility: hidden
            dtype: int
            description: Not an option.
            default: None
        
        centre_pad:
            visibility: hidden
            dtype: int
            description: Not an option.
            default: None
        
        outer_pad:
            visibility: intermediate
            dtype: float
            description: Pad the sinogram width to fill the reconstructed volume for asthetic purposes. Choose from True (defaults to sqrt(2)), False or float <= 2.1.
            default: False
            dependency: 
                algorithm: 
                    FP_CUDA
                    FBP_CUDA
                    BP_CUDA
                    FP
                    FBP
                    BP
        
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
        
        algorithm:
            visibility: intermediate
            dtype: tuple
            description: The reconstruction algorithm (art|bart|fbp|gridrec| mlem|osem|ospml_hybrid|ospml_quad|pml_hybrid|pml_quad|sirt).
            default: gridrec
        
        filter_name:
            visibility: intermediate
            dtype: str
            description: Valid for fbp|gridrec, options - none|shepp|cosine| hann|hamming|ramlak|parzen|butterworth).
            default: ramlak
            options: ['none', 'shepp', 'cosine', 'hann', 'hamming', 'ramlak', 'parzen', 'butterworth']
        
        reg_par:
            visibility: intermediate
            dtype: float
            description: Regularization parameter for smoothing, valid for ospml_hybrid|ospml_quad|pml_hybrid|pml_quad.
            default: 0.0
        
        n_iterations:
            visibility: intermediate
            dtype: int
            description: Number of iterations - only valid for iterative algorithms.
            default: 1
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml
