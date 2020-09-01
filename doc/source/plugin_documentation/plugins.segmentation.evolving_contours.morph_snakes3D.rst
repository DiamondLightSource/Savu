Morph Snakes3D
#################################################################

Description
--------------------------

A Plugin to 3D segment reconstructed data using
Morphsnakes module. When initialised with a mask, the active contour
propagates to find the minimum of energy (a possible edge countour).
    
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
        
        lambda1:
            visibility: basic
            dtype: int
            description: Weight parameter for the outer region, if lambda1 is larger than lambda2, the outer region will contain a larger range of values than the inner region.
            default: 1
        
        lambda2:
            visibility: basic
            dtype: int
            description: Weight parameter for the inner region, if lambda2 is larger than lambda1, the inner region will contain a larger range of values than the outer region.
            default: 1
        
        smoothing:
            visibility: basic
            dtype: int
            description: Number of times the smoothing operator is applied per iteration, reasonable values are around 1-4 and larger values lead to smoother segmentations.
            default: 1
        
        iterations:
            visibility: basic
            dtype: int
            description: The number of iterations.
            default: 350
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml
