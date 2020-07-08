Mc Near Absorption Correction
#################################################################

Description
--------------------------

McNears absorption correction, takes in a normalised absorption sinogram
and xrf sinogram stack.
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        in_datasets:
              visibility: datasets
              dtype: list
              description: "A list of the dataset(s) to process."
              default: ['xrf','stxm']
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
