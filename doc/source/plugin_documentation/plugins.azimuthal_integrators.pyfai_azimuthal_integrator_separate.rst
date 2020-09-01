Pyfai Azimuthal Integrator Separate
#################################################################

Description
--------------------------

1D azimuthal integrator by pyFAI
    
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
            description: A
            default: ['powder', 'spots']
        
        use_mask:
            visibility: basic
            dtype: bool
            description: Should we mask.
            default: False
        
        num_bins:
            visibility: basic
            dtype: int
            description: Number of bins.
            default: 1005
        
        percentile:
            visibility: intermediate
            dtype: int
            description: Percentile to threshold
            default: 50
        
        num_bins_azim:
            visibility: basic
            dtype: int
            description: Number of azimuthal bins.
            default: 20
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml
