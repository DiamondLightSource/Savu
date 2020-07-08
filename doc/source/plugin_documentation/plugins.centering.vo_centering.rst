Vo Centering
#################################################################

Description
--------------------------

A plugin to calculate the centre of rotation using the Vo Method
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        preview:
             visibility: basic
             dtype: int_list
             description: A slice list of required frames (sinograms) to use in
               the calculation of the centre of rotation (this will not reduce the data
               size for subsequent plugins).
             default: '[]'
        start_pixel:
             visibility: intermediate
             dtype: int
             description: The estimated centre of rotation. If value is None,
               use the horizontal centre of the image.
             default: 'None'
        search_area:
             visibility: intermediate
             dtype: tuple
             description: Search area around the estimated centre of rotation
             default: '(-50, 50)'
        ratio:
             visibility: intermediate
             dtype: float
             description: The ratio between the size of object and FOV of the camera
             default: 0.5
        search_radius:
             visibility: intermediate
             dtype: int
             description: Use for fine searching
             default: 6
        step:
             visibility: intermediate
             dtype: float
             description: Step of fine searching
             default: 0.5
        datasets_to_populate:
             visibility: advanced
             dtype: range
             description: A list of datasets which require this information
             default: '[]'
        out_datasets:
             visibility: datasets
             dtype: list
             description: The default names
             default: "['cor_preview', 'cor_broadcast']"
        broadcast_method:
             visibility: advanced
             dtype: str
             options: [median, mean, nearest, linear_fit]
             description:
               summary: Method of broadcasting centre values calculated
                 from preview slices to full dataset.
               options:
                   median:
                   mean:
                   nearest:
                   linear_fit:
             default: median
        row_drop:
             visibility: advanced
             dtype: int
             description: Drop lines around vertical center of the mask
             default: 20
        average_radius:
             visibility: advanced
             dtype: int
             description: Averaging sinograms around a required sinogram to
               improve signal-to-noise ratio
             default: 5
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml

Documentation
--------------------------

Bibtex
^^^^^^^^^^^^^^^^^^

.. code-block:: none

    @article{vo2014reliable,
          title={Reliable method for calculating the center of rotation in parallel-beam tomography},
          author={Vo, Nghia T and Drakopoulos, Michael and Atwood, Robert C and Reinhard, Christina},
          journal={Optics express},
          volume={22},
          number={16},
          pages={19078--19086},
          year={2014},
          publisher={Optical Society of America}
        }

Endnote
^^^^^^^^^^^^^^^^^^^^

.. code-block:: none

    %0 Journal Article
        %T Reliable method for calculating the center of rotation in parallel-beam tomography
        %A Vo, Nghia T
        %A Drakopoulos, Michael
        %A Atwood, Robert C
        %A Reinhard, Christina
        %J Optics express
        %V 22
        %N 16
        %P 19078-19086
        %@ 1094-4087
        %D 2014
        %I Optical Society of America
        

