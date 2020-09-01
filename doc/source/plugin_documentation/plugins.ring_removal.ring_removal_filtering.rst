Ring Removal Filtering
#################################################################

Description
--------------------------

Method to remove stripe artefacts in a sinogram (<-> ring
artefacts in a reconstructed image) using a filtering-based
method in the combination with a sorting-based method.
Note that it's different to a FFT-based or wavelet-FFT-based
method.
    
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
        
        sigma:
            visibility: intermediate
            dtype: int
            description: Sigma of the Gaussian window. Used to separate the low-pass and high-pass components of each sinogram column.
            default: 3
        
        size:
            visibility: intermediate
            dtype: int
            description: Size of the median filter window. Used to clean stripes.
            default: 31
        
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

The code of ring removal is the implementation of the work of Nghia T. Vo et al. taken from algorithm 2 and 3 in this paper

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
    

