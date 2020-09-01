Xrd Absorption Approximation
#################################################################

Description
--------------------------

McNears absorption correction, takes in a normalised absorption sinogram
and xrd sinogram stack. A base absorption correction for stxm and xrd
    
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
        
        azimuthal_offset:
            visibility: intermediate
            dtype: int
            description: angle between detectors.
            default: 0
        
        density:
            visibility: intermediate
            dtype: float
            description: The density
            default: 3.5377
        
        compound:
            visibility: intermediate
            dtype: str
            description: The compound
            default: Co0.2(Al2O3)0.8
        
        log_me:
            visibility: intermediate
            dtype: int
            description: should we log the transmission.
            default: 1
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml
