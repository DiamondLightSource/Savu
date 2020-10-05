Geo Distance3D
#################################################################

Description
--------------------------

3D geodesic transformation of images with manual initialisation.
    
Parameter definitions
--------------------------

.. code-block:: yaml

        in_datasets:
            visibility: datasets
            dtype: list
            description: Create a list of the dataset(s) to process
            default: []
        
        out_datasets:
            visibility: datasets
            dtype: list
            description: The default names.
            default: "['GeoDist']"
        
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
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml
