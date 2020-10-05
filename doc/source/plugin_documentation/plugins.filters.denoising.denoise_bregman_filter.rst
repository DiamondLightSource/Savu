Denoise Bregman Filter
#################################################################

Description
--------------------------

Split Bregman method for solving the denoising Total Variation ROF model.
    
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
        
        weight:
            visibility: basic
            dtype: float
            description: Denoising factor.
            default: 2.0
        
        max_iterations:
            visibility: basic
            dtype: int
            description: Total number of regularisation iterations. The smaller the number of iterations, the smaller the effect of the filtering is. A larger number will affect the speed of the algorithm.
            default: 30
        
        error_threshold:
            visibility: advanced
            dtype: float
            description: Convergence threshold.
            default: 0.001
        
        isotropic:
            visibility: advanced
            dtype: ['bool', 'str']
            description: Isotropic or Anisotropic filtering.
            options: ['Isotropic', 'Anisotropic']
            default: False
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml
