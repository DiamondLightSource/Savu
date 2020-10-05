Pyfai Azimuthal Integrator
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
            description: Create a list of the dataset(s) to create
            default: []
        
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
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml
