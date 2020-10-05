Subpixel Shift
#################################################################

Description
--------------------------

A plugin to apply a sub-pixel correction to images, for example to allow
subpixel alignment for the AstraGpu plugin.
    
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
        
        x_shift:
            visibility: intermediate
            dtype: float
            description: The shift in x for the output image in pixels. Positive values correspond to data being shifted towards larger indices.
            default: 0.0
        
        transform_module:
            visibility: intermediate
            dtype: str
            description: The module (skimage|scipy) to be used for image translation. skimage corresponds to skimage.transform.SimilarityTransform while scipy corresponds to scipy.ndimage.interpolation.
            default: skimage
            options: ['skimage', 'scipy']
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml
