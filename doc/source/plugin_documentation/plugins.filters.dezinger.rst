Dezinger
#################################################################

Description
--------------------------

A plugin for cleaning x-ray strikes based on statistical evaluation of
the near neighbourhood
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        outlier_mu:
              visibility: basic
              dtype: float
              description: Threshold for defecting outliers, greater is less
                sensitive.
              default: 10.0
        kernel_size:
              visibility: basic
              dtype: int
              description: Number of frames included in average.
              default: 5
        mode:
              visibility: basic
              dtype: int
              description: 'output mode, 0=normal 5=zinger strength 6=zinger
                yes/no.'
              default: 0

        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
