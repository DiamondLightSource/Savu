Ring Removal Regularization
#################################################################

Description
--------------------------

Method to remove stripe artefacts in a sinogram (<-> ring
artefacts in a reconstructed image) using a regularization-based
method. A simple improvement to handle partial stripes is included.
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        alpha:
            visibility: intermediate
            dtype: float
            description: The correction strength. Smaller is stronger.
            default: 0.005
        number_of_chunks:
            visibility: intermediate
            dtype: int
            description: Divide the sinogram to many chunks of rows.
            default: 1
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
