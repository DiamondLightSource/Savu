Image Saver
#################################################################

Description
--------------------------

A class to save tomography data to image files.  Run the MaxAndMin plugin
before this to rescale the data.
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        pattern:
            visibility: intermediate
            dtype: tuple
            description: How to slice the data.
            default: VOLUME_XZ

        format:
            visibility: intermediate
            dtype: str
            description: Image format.
            default: tif

        num_bit:
            visibility: intermediate
            dtype: int
            description: Bit depth of the tiff format (8, 16 or 32).
            default: 16

        max:
            visibility: intermediate
            dtype: float
            description: Global max for tiff scaling.
            default: None

        min:
           visibility: intermediate
           dtype: float
           description: Global min for tiff scaling.
           default: None

        jpeg_quality:
            visibility: intermediate
            dtype: range
            description: JPEG encoding quality (1 is worst, 100 is best).
            default: 75

        prefix:
             visibility: datasets
             dtype: str
             description: Override the default output jpg file prefix
             default: None
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
