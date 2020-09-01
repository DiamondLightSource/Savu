Dezinger Simple
#################################################################

Description
--------------------------

A plugin for cleaning x-ray strikes based on statistical evaluation of
the near neighbourhood
    
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
        
        outlier_mu:
            visibility: basic
            dtype: float
            description: Threshold for defecting outliers, greater is less sensitive.
            default: 1000.0
        
        kernel_size:
            visibility: basic
            dtype: int
            description: Number of frames included in average. If the number is not odd, use kernel_size + 1
            default: 5
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml
