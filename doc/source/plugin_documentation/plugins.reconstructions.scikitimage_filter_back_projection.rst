Scikitimage Filter Back Projection
#################################################################

Description
--------------------------

A Plugin to reconstruct an image by filter back projection using the
inverse radon transform from scikit-image.
    
Parameter definitions
--------------------------

.. code-block:: yaml

    

        output_size:
            visibility: basic
            dtype: tuple
            description: Number of rows and columns in the reconstruction.
            default: auto

        filter:
            visibility: intermediate
            dtype: str
            description: "Filter used in frequency domain filtering. Ramp
              filter used by default. Assign None to use no filter."
            options: [ramp, shepp-logan, cosine, hamming, hann, None]
            default: ramp

        interpolation:
            visibility: advanced
            dtype: int
            description: "Interpolation method used in reconstruction.
              Methods available: 'linear', 'nearest', and 'cubic'
              ('cubic' is slow)."
            options: [linear,nearest,cubic]
            default: linear

        circle:
            visibility: advanced
            dtype: bool
            description: "Assume the reconstructed image is zero outside
              the inscribed circle. Also changes the default output_size
              to match the behaviour of radon called with circle=True."
            default: False

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

    @article{kak2002principles,
            title={Principles of computerized tomographic imaging},
            author={Kak, Avinash C and Slaney, Malcolm and Wang, Ge},
            journal={Medical Physics},
            volume={29},
            number={1},
            pages={107--107},
            year={2002},
            publisher={Wiley Online Library}
            }
        

Endnote
^^^^^^^^^^^^^^^^^^^^

.. code-block:: none

    
        %0 Journal Article
        %T Principles of computerized tomographic imaging
        %A Kak, Avinash C
        %A Slaney, Malcolm
        %A Wang, Ge
        %J Medical Physics
        %V 29
        %N 1
        %P 107-107
        %@ 0094-2405
        %D 2002
        %I Wiley Online Library
        

