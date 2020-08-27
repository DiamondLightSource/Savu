Testing Sino Align
#################################################################

Description
--------------------------

The centre of mass of each row is determined and then a sine function fit
through these to determine the centre of rotation.  The residual between
each centre of mass and the sine function is then used to align each row.
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        threshold:
              visibility: intermediate
              dtype: list
              description:  e.g. [a, b] will set all values above a to
                b.
              default: 0.0
        p0:
              visibility: basic
              dtype: tuple
              description: Initial guess for the parameters of
                scipy.optimize.curve_fit.
              default: (1,1,1)


        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
