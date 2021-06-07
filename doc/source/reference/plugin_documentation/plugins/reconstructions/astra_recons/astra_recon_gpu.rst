Astra Recon Gpu
########################################################

Description
--------------------------

A Plugin to run the astra reconstruction 

Parameter definitions
--------------------------

.. code-block:: yaml

        in_datasets:
            visibility: datasets
            dtype: "[list[],list[str]]"
            description: 
                summary: A list of the dataset(s) to process.
                verbose: A list of strings, where each string gives the name of a dataset that was either specified by a loader plugin or created as output to a previous plugin.  The length of the list is the number of input datasets requested by the plugin.  If there is only one dataset and the list is left empty it will default to that dataset.
            default: "[]"
        
        out_datasets:
            visibility: datasets
            dtype: "[list[],list[str]]"
            description: 
                summary: A list of the dataset(s) to create.
                verbose: A list of strings, where each string is a name to be assigned to a dataset output by the plugin. If there is only one input dataset and one output dataset and the list is left empty, the output will take the name of the input dataset. The length of the list is the number of output datasets created by the plugin.
            default: "[]"
        
        centre_of_rotation:
            visibility: basic
            dtype: "[float, str, dict{int:float}]"
            description: Centre of rotation to use for the reconstruction.
            default: "0.0"
            example: It could be a fixed value, a dictionary of (sinogram number, value) pairs for a polynomial fit of degree 1, or a dataset name.
        
        init_vol:
            visibility: intermediate
            dtype: "[None, str]"
            description: Dataset to use as volume initialiser (does not currently work with preview)
            default: None
            example: "Type the name of the initialised dataset e.g. ['tomo']"
        
        log:
            visibility: intermediate
            dtype: bool
            description: 
                summary: Option to take the log of the data before reconstruction.
                verbose: Should be set to false if you use PaganinFilter
            default: "True"
            example: Set to True to take the log of the data before reconstruction.
        
        preview:
            visibility: intermediate
            dtype: preview
            description: A slice list of required frames.
            default: "[]"
        
        force_zero:
            visibility: intermediate
            dtype: "[list[float,float],list[None,None]]"
            description: Set any values in the reconstructed image outside of this range to zero.
            default: "['None', 'None']"
            example: "[0, 1]"
        
        ratio:
            visibility: intermediate
            dtype: float
            description: Ratio of the masks diameter in pixels to the smallest edge size along given axis.
            default: "0.95"
        
        log_func:
            visibility: advanced
            dtype: str
            description: Override the default log function
            default: np.nan_to_num(-np.log(sino))
            example: You write a function as default
        
        vol_shape:
            visibility: basic
            dtype: "[str, int]"
            description: 
                summary: Override the size of the reconstruction volume with an integer value.
                verbose: When fixed, you get the dimension of the horizontal detector or you can specify any reconstruction size you like with an integer.
            default: fixed
        
        n_iterations:
            visibility: basic
            dtype: int
            description: Number of Iterations is only valid for iterative algorithms
            default: "1"
            dependency: 
                algorithm: 
                    SIRT_CUDA
                    SART_CUDA
                    CGLS_CUDA
        
        res_norm:
            visibility: basic
            dtype: "[int,bool]"
            description: Output the residual norm at each iteration (Error in the solution)
            default: "False"
            dependency: 
                algorithm: 
                    SIRT_CUDA
                    SART_CUDA
                    CGLS_CUDA
        
        algorithm:
            visibility: basic
            dtype: str
            options: "['FBP_CUDA', 'SIRT_CUDA', 'SART_CUDA', 'CGLS_CUDA', 'FP_CUDA', 'BP_CUDA', 'SIRT3D_CUDA', 'CGLS3D_CUDA']"
            description: 
                summary: Reconstruction type
                options: 
                    FBP_CUDA: Filtered Backprojection Method
                    SIRT_CUDA: Simultaneous Iterative Reconstruction Technique
                    SART_CUDA: Simultaneous Algebraic Reconstruction Technique
                    CGLS_CUDA: Conjugate Gradient Least Squares
                    FP_CUDA: Forward Projection
                    BP_CUDA: Backward Projection
                    SIRT3D_CUDA: Simultaneous Iterative Reconstruction Technique 3D
                    CGLS3D_CUDA: Conjugate Gradient Least Squares 3D
            default: FBP_CUDA
        
        FBP_filter:
            visibility: basic
            dtype: str
            options: "['none', 'ram-lak', 'shepp-logan', 'cosine', 'hamming', 'hann', 'tukey', 'lanczos', 'triangular', 'gaussian', 'barlett-hann', 'blackman', 'nuttall', 'blackman-harris', 'blackman-nuttall', 'flat-top', 'kaiser', 'parzen']"
            description: 
                summary: The FBP reconstruction filter type
                options: 
                    none: No filtering
                    ram-lak: Ram-Lak or ramp filter
                    shepp-logan: Multiplies the Ram-Lak filter by a sinc function
                    cosine: Multiplies the Ram-Lak filter by a cosine function
                    hamming: Multiplies the Ram-Lak filter by a hamming window
                    hann: Multiplies the Ram-Lak filter by a hann window
                    tukey: None
                    lanczos: None
                    triangular: None
                    gaussian: None
                    barlett-hann: None
                    blackman: None
                    nuttall: None
                    blackman-harris: None
                    blackman-nuttall: None
                    flat-top: None
                    kaiser: None
                    parzen: None
            default: ram-lak
        
        outer_pad:
            visibility: intermediate
            dtype: "[bool, float]"
            description: Pad the sinogram width to fill the reconstructed volume for asthetic purposes. Choose from True (defaults to sqrt(2)), False or float <= 2.1.
            warning: This will increase the size of the data and the time to compute the reconstruction. Only available for selected algorithms and will be ignored otherwise.
            default: "False"
            dependency: 
                algorithm: 
                    FP_CUDA
                    FBP_CUDA
                    BP_CUDA
        
        centre_pad:
            visibility: intermediate
            dtype: "[bool, float]"
            description: Pad the sinogram to centre it in order to fill the reconstructed volume ROI for asthetic purposes.
            warning: This will significantly increase the size of the data and the time to compute the reconstruction)
            default: "False"
            dependency: 
                algorithm: 
                    FP
                    FBP
                    BP
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml

Citations
--------------------------

Performance improvements for iterative electron tomography reconstruction using graphics processing units (GPUs) by Palenstijn, WJ et al.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Bibtex
""""""""""""""""""""""""""""""""""""""""""

.. code-block:: none

    @article{palenstijn2011performance,
      title={Performance improvements for iterative electron tomography reconstruction using graphics processing units (GPUs)},
      author={Palenstijn, WJ and Batenburg, KJ and Sijbers, J},
      journal={Journal of structural biology},
      volume={176},
      number={2},
      pages={250--253},
      year={2011},
      publisher={Elsevier}
    }
    

Endnote
""""""""""""""""""""""""""""""""""""""""""

.. code-block:: none

    %0 Journal Article
    %T Performance improvements for iterative electron tomography reconstruction using graphics processing units (GPUs)
    %A Palenstijn, WJ
    %A Batenburg, KJ
    %A Sijbers, J
    %J Journal of structural biology
    %V 176
    %N 2
    %P 250-253
    %@ 1047-8477
    %D 2011
    %I Elsevier
    

