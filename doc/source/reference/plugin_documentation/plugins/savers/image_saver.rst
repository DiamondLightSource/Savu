Image Saver
########################################################

Description
--------------------------

A class to save tomography data to image files.  Run the MaxAndMin plugin before this to rescale the data. 

.. toctree::
    Plugin documention and guidelines on use </../../../plugin_guides/plugins/savers/image_saver_doc.rst>

Parameter definitions
--------------------------

.. code-block:: yaml

        in_datasets:
            visibility: datasets
            dtype: "[list[],list[str]]"
            description: none
            default: "[]"
        
        out_datasets:
            visibility: datasets
            dtype: "[list[],list[str]]"
            description: none
            default: "[]"
        
        pattern:
            visibility: intermediate
            dtype: str
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
            default: "16"
            options: "[8, 16, 32]"
        
        max:
            visibility: intermediate
            dtype: "[None,float]"
            description: Global max for tiff scaling.
            default: None
        
        min:
            visibility: intermediate
            dtype: "[None,float]"
            description: Global min for tiff scaling.
            default: None
        
        jpeg_quality:
            visibility: intermediate
            dtype: int
            description: JPEG encoding quality (1 is worst, 100 is best).
            default: "75"
        
        prefix:
            visibility: datasets
            dtype: "[None,str]"
            description: Override the default output jpg file prefix
            default: None
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml
