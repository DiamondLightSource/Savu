Ring Removal Fitting
#################################################################

Description
--------------------------

Method to remove stripe artefacts in a sinogram (<-> ring
artefacts in a reconstructed image) using a fitting-based method.
It's suitable for use on low-contrast sinogram and/or for removing
blurry rings.
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        sigmax:
            visibility: intermediate
            dtype: int
            description: Sigma of the Gaussian window in x-direction which              controls the strength of the removal.
            default: 5
        sigmay:
            visibility: intermediate
            dtype: int
            description: Sigma of the Gaussian window in y-direction
            default: 20
        order:
            visibility: intermediate
            dtype: int
            description: polynomial fit order.
            default: 2
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml

Documentation
--------------------------

Bibtex
^^^^^^^^^^^^^^^^^^

.. code-block:: none

    @article{vo2018superior,
            title = {Superior techniques for eliminating ring artifacts in X-ray micro-tomography},
            author={Vo, Nghia T and Atwood, Robert C and Drakopoulos, Michael},
            journal={Optics express},
            volume={26},
            number={22},
            pages={28396--28412},
            year={2018},
            publisher={Optical Society of America}
            }
        

