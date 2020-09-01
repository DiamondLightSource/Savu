Astra Recon Cpu
#################################################################

Description
--------------------------

A Plugin to run the astra reconstruction
    
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
        
        n_iterations:
            visibility: basic
            dtype: int
            description: Number of Iterations is only valid for iterative algorithms
            default: 1
        
        algorithm:
            visibility: basic
            dtype: str
            options: ['FBP', 'SIRT', 'SART', 'ART', 'CGLS', 'FP', 'BP']
            description: 
                summary: Reconstruction type
                options: 
                    FBP: Filtered Backprojection Method
                    SIRT: Simultaneous Iterative Reconstruction Technique
                    SART: Simultaneous Algebraic Reconstruction Technique
                    ART: Iterative Reconstruction Technique
                    CGLS: Conjugate Gradient Least Squares
                    FP: Forward Projection
                    BP: Back Projection
            default: FBP
        
        FBP_filter:
            visibility: basic
            dtype: str
            options: ['none', 'ram-lak', 'shepp-logan', 'cosine', 'hamming', 'hann', 'tukey', 'lanczos', 'triangular', 'gaussian', 'barlett-hann', 'blackman', 'nuttall', 'blackman-harris', 'blackman-nuttall', 'flat-top', 'kaiser', 'parzen']
            description: 
                summary: The FBP reconstruction filter type
                options: 
                    none: No filtering
                    ram-lak: Ram-Lak or ramp filter
                    shepp-logan: Multiplies the Ram-Lak filter by a sinc function
                    cosine: Multiplies the Ram-Lak filter by a cosine function
                    hamming: Multiplies the Ram-Lak filter by a hamming window
                    hann: Multiplies the Ram-Lak filter by a hann window
                    tukey:
                    lanczos:
                    triangular:
                    gaussian:
                    barlett-hann:
                    blackman:
                    nuttall:
                    blackman-harris:
                    blackman-nuttall:
                    flat-top:
                    kaiser:
                    parzen:
            default: ram-lak
        
        projector:
            visibility: advanced
            dtype: str
            options: ['line', 'strip', 'linear']
            description: 
                summary: Set astra projector
                options: 
                    line: The weight of a ray/pixel pair is given by the length of the intersection of the pixel and the ray, considered as a zero-thickness line.
                    strip: The weight of a ray/pixel pair is given by the area of the intersection of the pixel and the ray, considered as a strip with the same width as a detector pixel.
                    linear: Linear interpolation between the two nearest volume pixels of the intersection of the ray and the column/row.
            default: line
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml

Documentation
--------------------------

Citations
^^^^^^^^^^^^^^^^^^^^^^^^

Fast and flexible X-ray tomography using the ASTRA toolbox by  Van Aarle, Wim et al.
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

The tomography reconstruction algorithm used in this processing pipeline is part of the ASTRA Toolbox

Bibtex
````````````````````````````````````````````````

.. code-block:: none

    @article{van2016fast,
    title={Fast and flexible X-ray tomography using the ASTRA toolbox},
    author={Van Aarle, Wim and Palenstijn, Willem Jan and Cant, Jeroen and Janssens, Eline and Bleichrodt, Folkert and Dabravolski, Andrei and De Beenhouwer, Jan and Batenburg, K Joost and Sijbers, Jan},
    journal={Optics express},
    volume={24},
    number={22},
    pages={25129--25147},
    year={2016},
    publisher={Optical Society of America}
    }
    

Endnote
````````````````````````````````````````````````

.. code-block:: none

    %0 Journal Article
    %T Fast and flexible X-ray tomography using the ASTRA toolbox
    %A Van Aarle, Wim
    %A Palenstijn, Willem Jan
    %A Cant, Jeroen
    %A Janssens, Eline
    %A Bleichrodt, Folkert
    %A Dabravolski, Andrei
    %A De Beenhouwer, Jan
    %A Batenburg, K Joost
    %A Sijbers, Jan
    %J Optics express
    %V 24
    %N 22
    %P 25129-25147
    %@ 1094-4087
    %D 2016
    %I Optical Society of America
    

The ASTRA Toolbox: A platform for advanced algorithm development in electron tomography by  Van Aarle, Wim et al.
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

The tomography reconstruction algorithm used in this processing pipeline is part of the ASTRA Toolbox

Bibtex
````````````````````````````````````````````````

.. code-block:: none

    @article{van2015astra,
    title={The ASTRA Toolbox: A platform for advanced algorithm development in electron tomography},
    author={Van Aarle, Wim and Palenstijn, Willem Jan and De Beenhouwer, Jan and Altantzis, Thomas and Bals, Sara and Batenburg, K Joost and Sijbers, Jan},
    journal={Ultramicroscopy},
    volume={157},
    pages={35--47},
    year={2015},
    publisher={Elsevier}
    }
    

Endnote
````````````````````````````````````````````````

.. code-block:: none

    %0 Journal Article
    %T The ASTRA Toolbox: A platform for advanced algorithm development in electron tomography
    %A Van Aarle, Wim
    %A Palenstijn, Willem Jan
    %A De Beenhouwer, Jan
    %A Altantzis, Thomas
    %A Bals, Sara
    %A Batenburg, K Joost
    %A Sijbers, Jan
    %J Ultramicroscopy
    %V 157
    %P 35-47
    %@ 0304-3991
    %D 2015
    %I Elsevier
    

