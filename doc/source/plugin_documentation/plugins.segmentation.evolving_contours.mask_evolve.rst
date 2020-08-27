Mask Evolve
#################################################################

Description
--------------------------

Fast segmentation by evolving the given mask, the mask must be given
precisely through the object, otherwise segmentation will be incorrect.

    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        threshold:
            visibility: basic
            dtype: float
            description: Important parameter to control mask propagation.
            default: 1.0

        method:
            visibility: basic
            dtype: str
            description: 'Method to collect statistics from the mask (mean, median, value).'
            default: mean

        iterations:
            visibility: basic
            dtype: int
            description: The number of iterations.
            default: 500

        connectivity:
            visibility: intermediate
            dtype: int
            description: The connectivity of the local neighbourhood.
            default: 4

        pattern:
            visibility: intermediate
            dtype: str
            description: Pattern to apply this to.
            default: 'VOLUME_YZ'

        out_datasets:
            visibility: intermediate
            dtype: list
            description: The default names.
            default: '[MASK_EVOVED]'

        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
