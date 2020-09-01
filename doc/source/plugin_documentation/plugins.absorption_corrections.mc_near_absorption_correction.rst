Mc Near Absorption Correction
#################################################################

Description
--------------------------

McNears absorption correction, takes in a normalised absorption sinogram
and xrf sinogram stack.
    
Parameter definitions
--------------------------

.. code-block:: yaml

        in_datasets:
            visibility: datasets
            dtype: list
            description: A list of the dataset(s) to process.
            default: ['xrf', 'stxm']
        
        out_datasets:
            visibility: datasets
            dtype: list
            description: Create a list of the dataset(s) to create
            default: []
        
        azimuthal_offset:
            visibility: basic
            dtype: float
            description: Angle between detectors.
            default: -90.0
        
        density:
            visibility: intermediate
            dtype: float
            description: The density
            default: 3.5377
        
        compound:
            visibility: intermediate
            dtype: str
            description: The compound
            default: Co0.1Re0.01Ti0.05(SiO2)0.84
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml
