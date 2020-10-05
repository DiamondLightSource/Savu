Remove Large Rings
#################################################################

Description
--------------------------

Method to remove large stripe artefacts in a sinogram (<-> ring
artefacts in a reconstructed image).
    
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
        
        size:
            visibility: intermediate
            dtype: int
            description: Size of the median filter window. Greater is stronger
            default: 71
        
        snr:
            visibility: intermediate
            dtype: int
            description: Ratio used to detect locations of large stripes. Greater is less sensitive.
            default: 3.0
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml

Citations
--------------------------

Superior techniques for eliminating ring artifacts in X-ray micro-tomography by Vo, Nghia T et al.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Bibtex
""""""""""""""""""""""""""""""""""""""""""

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
""""""""""""""""""""""""""""""""""""""""""

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
    

