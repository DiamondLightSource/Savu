Projection Shift
#################################################################

Description
--------------------------

Horizontal and vertical shift are calculated using a chosen method and
added to the metadata.  The vertical and horizontal shifts can be corrected
using the ProjectionVerticalAlignment and SinogramAlignment (in 'shift' mode)
plugins respectively.

Method: Uses either skimage template_matching or orb feature tracking plus
robust ransac matching to calculate the translation between different
combinations of 10 consecutive projection images. A least squares solution to
the shift values between images is calculated and returned for the middle 8 images.
    
.. toctree::
    Plugin documention and guidelines on use </../documentation/projection_shift_doc.rst>

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
            description: Set the output dataset name
            default: ['proj_shift']
        
        method:
            visibility: basic
            dtype: str
            description: "Method used to calculate the shift between images. Choose from 'template_matching' and 'orb_ransac'."
            default: orb_ransac
            options: ['template_matching', 'orb_ransac']
        
        template:
            visibility: basic
            dtype: list
            description: "Position of the template to match (required) e.g. [300:500, 300:500]."
            default: None
        
        threshold:
            visibility: intermediate
            dtype: list
            description: "e.g. [a, b] will set all values above a to b."
            default: None
        
        n_keypoints:
            visibility: intermediate
            dtype: int
            description: Number of keypoints to use in ORB feature detector.
            default: 20
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml
