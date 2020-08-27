Geo Distance
#################################################################

Description
--------------------------

Geodesic transformation of images with manual initialisation.
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        lambda:
            visibility: basic
            dtype: float
            description: Weighting between 0 and 1
            default: 0.5

        iterations:
            visibility: basic
            dtype: int
            description: The number of iterations for raster scanning.
            default: 4

        out_datasets:
            visibility: datasets
            dtype: list
            description: The default names.
            default: "['GeoDist, 'max_values']"

        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
