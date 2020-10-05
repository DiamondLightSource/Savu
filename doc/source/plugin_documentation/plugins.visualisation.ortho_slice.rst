Ortho Slice
#################################################################

Description
--------------------------

A plugin to calculate the centre of rotation using the Vo Method
    
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
            description: Default out dataset names.
            default: "['XY','YZ','XZ']"
        
        xy_slices:
            visibility: intermediate
            dtype: int
            description: which XY slices to render.
            default: 100
        
        yz_slices:
            visibility: intermediate
            dtype: int
            description: which YZ slices to render.
            default: 100
        
        xz_slices:
            visibility: intermediate
            dtype: int
            description: which XZ slices to render.
            default: 100
        
        file_type:
            visibility: intermediate
            dtype: str
            description: File type to save as. rings and streaks
            default: png
        
        colourmap:
            visibility: hidden
            dtype: str
            description: Colour scheme to apply to the image.
            default: magma
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml
