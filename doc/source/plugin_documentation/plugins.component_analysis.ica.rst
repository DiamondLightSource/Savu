Ica
#################################################################

Description
--------------------------

This plugin performs independent component analysis on XRD/XRF spectra.
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        w_init:
             visibility: basic
             dtype: list
             description: The initial mixing matrix.
             default: None

        random_state:
             visibility: intermediate
             dtype: int
             description: The state
             default: 1

        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
