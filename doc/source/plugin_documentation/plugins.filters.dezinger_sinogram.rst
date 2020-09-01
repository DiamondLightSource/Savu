Dezinger Sinogram
#################################################################

Description
--------------------------

Method to remove scratches in the reconstructed image caused by
zingers. Remove zingers (caused by scattered X-rays hitting the CCD chip
directly)
    
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
        
        tolerance:
            visibility: basic
            dtype: float
            description: Threshold for detecting zingers, greater is less sensitive.
            default: 0.08
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml
