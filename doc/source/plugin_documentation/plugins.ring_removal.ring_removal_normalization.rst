Ring Removal Normalization
#################################################################

Description
--------------------------

Method to remove stripe artefacts in a sinogram (<-> ring artefacts in a
reconstructed image) using a normalization-based method. A simple
improvement to handle partial stripes is included.

    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        radius:
            visibility: intermediate
            dtype: int
            description: Radius of the Gaussian kernel.
            default: 11
        number_of_chunks:
            visibility: intermediate
            dtype: int
            description:  Divide the sinogram to many chunks of rows
            default: 1
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
