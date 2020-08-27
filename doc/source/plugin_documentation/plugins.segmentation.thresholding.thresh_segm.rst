Thresh Segm
#################################################################

Description
--------------------------

A Plugin to segment the data by providing two scalar values for lower and upper intensities
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        min_intensity:
            visibility: basic
            dtype: float
            description: A scalar to define lower limit for intensity, all values below are set to zero.
            default: 0

        max_intensity:
            visibility: basic
            dtype: float
            description: A scalar to define upper limit for intensity, all values above are set to zero.
            default: 0.01

        value:
            visibility: basic
            dtype: int
            description: An integer to set all values between min_intensity and max_intensity.
            default: 1

        pattern:
            visibility: intermediate
            dtype: str
            description: Pattern to apply this to.
            default: 'VOLUME_XY'

        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
