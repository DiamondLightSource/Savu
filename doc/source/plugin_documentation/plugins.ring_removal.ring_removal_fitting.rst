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
        
        sigmax:
            visibility: intermediate
            dtype: int
            description: Sigma of the Gaussian window in x-direction which controls the strength of the removal.
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

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml

Documentation
--------------------------

Citations
^^^^^^^^^^^^^^^^^^^^^^^^

Superior techniques for eliminating ring artifacts in X-ray micro-tomography by  Vo, Nghia T et al.
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

The code of ring removal is the implementation of the work of Nghia T. Vo et al. taken from algorithm 1 in this paper

Bibtex
````````````````````````````````````````````````

.. code-block:: none

    @article{vo2018superior,
    title = {Superior techniques for eliminating ring artifacts in X-ray micro-tomography},
    author={Vo, Nghia T and Atwood, Robert C and Drakopoulos, Michael},
    journal={Optics express},
    volume={26},
    number={22},
    pages={28396--28412},
    year={2018},
    publisher={Optical Society of America}}
    

Endnote
````````````````````````````````````````````````

.. code-block:: none

    %0 Journal Article
    %T Superior techniques for eliminating ring artifacts in X-ray micro-tomography
    %A Vo, Nghia T
    %A Atwood, Robert C
    %A Drakopoulos, Michael
    %J Optics express
    %V 26
    %N 22
    %P 28396-28412
    %@ 1094-4087
    %D 2018
    %I Optical Society of America
    

