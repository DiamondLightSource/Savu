Gmm Segment3D
#################################################################

Description
--------------------------

A Plugin to segment data using Gaussian Mixtures from scikit
    
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
            description: Create a list of the dataset(s) to create
            default: []
        
        classes:
            visibility: basic
            dtype: int
            description: The number of classes for GMM
            default: 5
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml
