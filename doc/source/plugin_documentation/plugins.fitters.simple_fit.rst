Simple Fit
#################################################################

Description
--------------------------

This plugin fits peaks.
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        width_guess:
            visibility: basic
            dtype: float
            description: An initial guess at the width.
            default: 0.02

        PeakIndex:
            visibility: basic
            dtype: list
            description: The peak index
            default: []

        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
