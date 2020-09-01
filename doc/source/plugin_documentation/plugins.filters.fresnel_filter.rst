Fresnel Filter
#################################################################

Description
--------------------------

Method similar to the Paganin filter working both on sinograms and
projections. Used to improve the contrast of the reconstruction image.

    
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
        
        ratio:
            visibility: datasets
            dtype: float
            description: Control the strength of the filter. Greater is stronger
            default: 100.0
        
        pattern:
            visibility: basic
            dtype: str
            description: Data processing pattern
            options: ['PROJECTION', 'SINOGRAM']
            default: SINOGRAM
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml

Documentation
--------------------------

Citations
^^^^^^^^^^^^^^^^^^^^^^^^

by  et al.
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

The filter built is based on the Fresnel propagator

