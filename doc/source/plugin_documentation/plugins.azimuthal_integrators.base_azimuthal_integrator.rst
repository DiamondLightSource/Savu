Base Azimuthal Integrator
#################################################################

Description
--------------------------

A base azimuthal integrator for pyfai
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
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

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
