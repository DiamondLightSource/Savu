Visual Hulls Recon
#################################################################

Description
--------------------------

A Plugin to reconstruct an image by filter back projection
using the inverse radon transform from scikit-image.
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        threshold:
            visibility: advanced
            dtype: float
            description: Threshold to binarize the input sinogram.
            default: 0.5

        outer_pad:
            visibility: hidden
            dtype: str
            description: Not required.
            default: False

        centre_pad:
            visibility: hidden
            dtype: int
            description: Not required.
            default: False

        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml

Documentation
--------------------------

Bibtex
^^^^^^^^^^^^^^^^^^

.. code-block:: none

    @article{laurentini1994visual,
          title={The visual hull concept for silhouette-based image understanding},
          author={Laurentini, Aldo},
          journal={IEEE Transactions on pattern analysis and machine intelligence},
          volume={16},
          number={2},
          pages={150--162},
          year={1994},
          publisher={IEEE}
          }
        

Endnote
^^^^^^^^^^^^^^^^^^^^

.. code-block:: none

    %0 Journal Article
            %T The visual hull concept for silhouette-based image understanding
            %A Laurentini, Aldo
            %J IEEE Transactions on pattern analysis and machine intelligence
            %V 16
            %N 2
            %P 150-162
            %@ 0162-8828
            %D 1994
            %I IEEE
        

