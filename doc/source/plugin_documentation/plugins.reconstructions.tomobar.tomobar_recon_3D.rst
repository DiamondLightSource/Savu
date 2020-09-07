Tomobar Recon 3D
#################################################################

Description
--------------------------

A Plugin to reconstruct full-field tomographic projection data using
state-of-the-art regularised iterative algorithms from the ToMoBAR package.
ToMoBAR includes FISTA and ADMM iterative methods and depends on the ASTRA
toolbox and the CCPi RGL toolkit: https://github.com/vais-ral/CCPi-Regularisation-Toolkit.
    
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
            description: Dataset to use as volume initialiser (does not currently work with preview)
            default: None
            example: "Type the name of the initialised dataset e.g. ['tomo']"
        
        centre_pad:
            visibility: intermediate
            dtype: float
            description: Pad the sinogram to centre it in order to fill the reconstructed volume ROI for asthetic purposes.
            default: False
            dependency: 
                algorithm: 
                    FP_CUDA
                    FBP_CUDA
                    BP_CUDA
                    FP
                    FBP
                    BP
            example: "Is it a scalar or a list?"
        
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
        
        output_size:
            visibility: advanced
            dtype: tuple
            description: The dimension of the reconstructed volume (only X-Y dimension).
            default: auto
        
        param_padding:
            visibility: advanced
            dtype: int
            description: The amount of pixels to pad each slab of the cropped projection data.
            default: 17
        
        data_fidelity:
            visibility: advanced
            dtype: str
            description: Least Squares only at the moment.
            default: LS
        
        data_Huber_thresh:
            visibility: advanced
            dtype: int
            description: Threshold parameter for __Huber__ data fidelity.
            default: None
        
        data_any_rings:
            visibility: hidden
            dtype: int
            description: A parameter to suppress various artifacts including rings and streaks
            default: None
        
        data_any_rings_winsizes:
            visibility: hidden
            dtype: tuple
            description: "half window sizes to collect background information [detector, angles, num of projections]"
            default: (9,7,9)
        
        data_any_rings_power:
            visibility: hidden
            dtype: float
            description: A power parameter for Huber model.
            default: 1.5
        
        data_full_ring_GH:
            visibility: advanced
            dtype: str
            description: Regularisation variable for full constant ring removal (GH model).
            default: None
        
        data_full_ring_accelerator_GH:
            visibility: advanced
            dtype: float
            description: Acceleration constant for GH ring removal. (use with care)
            default: 10.0
        
        algorithm_iterations:
            visibility: basic
            dtype: int
            description: 
                summary: Number of outer iterations for FISTA (default)or ADMM methods.
                verbose: Less than 10 iterations for the iterative method (FISTA) can deliver a blurry reconstruction. The suggested value is 15 iterations, however the algorithm can stop prematurely based on the tolerance value.
            default: 20
        
        algorithm_verbose:
            visibility: advanced
            dtype: bool
            description: Print iterations number and other messages (off by default).
            default: off
        
        algorithm_ordersubsets:
            visibility: advanced
            dtype: int
            description: The number of ordered-subsets to accelerate reconstruction.
            default: 6
        
        algorithm_nonnegativity:
            visibility: advanced
            dtype: str
            options: ['ENABLE', 'DISABLE']
            description: 
                summary: ENABLE or DISABLE nonnegativity constraint.
            default: ENABLE
        
        regularisation_method:
            visibility: advanced
            dtype: str
            options: ['ROF_TV', 'FGP_TV', 'PD_TV', 'SB_TV', 'LLT_ROF', 'NDF', 'TGV', 'NLTV', 'Diff4th']
            description: 
                summary: The denoising method
                verbose: Iterative methods can help to solve ill-posed inverse problems by choosing a suitable noise model for the measurement
                options: 
                    ROF_TV: Rudin-Osher-Fatemi Total Variation model
                    FGP_TV: Fast Gradient Projection Total Variation model
                    PD_TV: Primal-Dual Total Variation
                    SB_TV: Split Bregman Total Variation model
                    LLT_ROF: Lysaker, Lundervold and Tai model combined with Rudin-Osher-Fatemi
                    NDF: Nonlinear/Linear Diffusion model (Perona-Malik, Huber or Tukey)
                    TGV: Total Generalised Variation
                    NLTV: Non Local Total Variation
                    Diff4th: Fourth-order nonlinear diffusion model
            default: FGP_TV
        
        regularisation_parameter:
            visibility: basic
            dtype: float
            description: 
                summary: Regularisation parameter. The higher the value, the stronger the smoothing effect
                range: Recommended between 0 and 1
            default: 0.0001
        
        regularisation_iterations:
            visibility: basic
            dtype: int
            description: 
                summary: Total number of regularisation iterations. The smaller the number of iterations, the smaller the effect of the filtering is. A larger number will affect the speed of the algorithm.
            default: 80
        
        regularisation_device:
            visibility: advanced
            dtype: str
            description: The device for regularisation
            default: gpu
        
        regularisation_PD_lip:
            visibility: advanced
            dtype: int
            description: Primal-dual parameter for convergence.
            default: 8
            dependency: 
                regularisation_method: PD_TV
        
        regularisation_methodTV:
            visibility: advanced
            dtype: str
            description: 0/1 - TV specific isotropic/anisotropic choice.
            default: 0
            dependency: 
                regularisation_method: 
                    ROF_TV
                    FGP_TV
                    SB_TV
                    NLTV
        
        regularisation_timestep:
            visibility: advanced
            dtype: float
            dependency: 
                regularisation_method: 
                    ROF_TV
                    LLT_ROF
                    NDF
                    Diff4th
            description: 
                summary: Time marching parameter
                range: Recommended between 0.0001 and 0.003
            default: 0.003
        
        regularisation_edge_thresh:
            visibility: advanced
            dtype: float
            dependency: 
                regularisation_method: 
                    NDF
                    Diff4th
            description: 
                summary: Edge (noise) related parameter
            default: 0.01
        
        regularisation_parameter2:
            visibility: advanced
            dtype: float
            dependency: 
                regularisation_method: LLT_ROF
            description: 
                summary: Regularisation (smoothing) value
                verbose: The higher the value stronger the smoothing effect
            default: 0.005
        
        regularisation_NDF_penalty:
            visibility: advanced
            dtype: str
            options: ['Huber', 'Perona', 'Tukey']
            description: 
                summary: Penalty dtype
                verbose: Nonlinear/Linear Diffusion model (NDF) specific penalty type.
                options: 
                    Huber: Huber
                    Perona: Perona-Malik model
                    Tukey: Tukey
            dependency: 
                regularisation_method: NDF
            default: Huber
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml

Documentation
--------------------------

Citations
^^^^^^^^^^^^^^^^^^^^^^^^

A fast iterative shrinkage-thresholding algorithm for linear inverse problems by  Beck, Amir et al.
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

First-order optimisation algorithm for linear inverse problems

Bibtex
````````````````````````````````````````````````

.. code-block:: none

    @article{beck2009fast,
    title={A fast iterative shrinkage-thresholding algorithm for linear inverse problems},
    author={Beck, Amir and Teboulle, Marc},
    journal={SIAM journal on imaging sciences},
    volume={2},
    number={1},
    pages={183--202},
    year={2009},
    publisher={SIAM}
    }
    

Endnote
````````````````````````````````````````````````

.. code-block:: none

    %0 Journal Article
    %T A fast iterative shrinkage-thresholding algorithm for linear inverse problems
    %A Beck, Amir
    %A Teboulle, Marc
    %J SIAM journal on imaging sciences
    %V 2
    %N 1
    %P 183-202
    %@ 1936-4954
    %D 2009
    %I SIAM
    

