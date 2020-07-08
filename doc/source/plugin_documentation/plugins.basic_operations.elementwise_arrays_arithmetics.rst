Elementwise Arrays Arithmetics
#################################################################

Description
--------------------------

Basic arithmetic operations on two input datasets:
addition, subtraction, multiplication and division.

    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        operation:
              visibility: basic
              dtype: str
              description: Arithmetic operation to apply to data, choose from addition, subtraction,
                multiplication and division.
              options: [addition, subtraction, multiplication, division]
              default: multiplication
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
