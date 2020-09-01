Ring Removal Regularization
#################################################################

Description
--------------------------

Method to remove stripe artefacts in a sinogram (<-> ring
artefacts in a reconstructed image) using a regularization-based
method. A simple improvement to handle partial stripes is included.
    
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
        
        alpha:
            visibility: intermediate
            dtype: float
            description: The correction strength. Smaller is stronger.
            default: 0.005
        
        number_of_chunks:
            visibility: intermediate
            dtype: int
            description: Divide the sinogram to many chunks of rows.
            default: 1
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml

Documentation
--------------------------

Citations
^^^^^^^^^^^^^^^^^^^^^^^^

An analytical formula for ring artefact suppression in X-ray tomography by  Titarenko, Sofya et al.
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

The code of ring removal is the implementation of the work of Sofya Titarenko et al. taken from this paper

Bibtex
````````````````````````````````````````````````

.. code-block:: none

    @article{titarenko2010analytical,
      title={An analytical formula for ring artefact suppression in X-ray tomography},
      author={Titarenko, Sofya and Withers, Philip J and Yagola, Anatoly},
      journal={Applied Mathematics Letters},
      volume={23},
      number={12},
      pages={1489--1495},
      year={2010},
      publisher={Elsevier}
    }
    

Endnote
````````````````````````````````````````````````

.. code-block:: none

    %0 Journal Article
    %T An analytical formula for ring artefact suppression in X-ray tomography
    %A Titarenko, Sofya
    %A Withers, Philip J
    %A Yagola, Anatoly
    %J Applied Mathematics Letters
    %V 23
    %N 12
    %P 1489-1495
    %@ 0893-9659
    %D 2010
    %I Elsevier
    

