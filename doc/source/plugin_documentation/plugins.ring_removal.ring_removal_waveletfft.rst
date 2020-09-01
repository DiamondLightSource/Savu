Ring Removal Waveletfft
#################################################################

Description
--------------------------

Ring artefact removal method
    
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
        
        nvalue:
            visibility: intermediate
            dtype: int
            description: Order of the the Daubechies (DB) wavelets.
            default: 5
        
        sigma:
            visibility: intermediate
            dtype: int
            description: Damping parameter. Larger is stronger.
            default: 1
        
        level:
            visibility: intermediate
            dtype: int
            description: Wavelet decomposition level.
            default: 3
        
        padFT:
            visibility: intermediate
            dtype: int
            description: Padding for Fourier transform
            default: 20
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml
