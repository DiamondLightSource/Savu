Mtf Deconvolution
#################################################################

Description
--------------------------

Method to correct the point-spread-function effect.
Working on raw projections and flats.
    
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
        
        file_path:
            visibility: intermediate
            dtype: filepath
            description: "Path to file containing a 2D array of a MTF function. File formats are 'npy', or 'tif'."
            default: None
        
        pad_width:
            visibility: intermediate
            dtype: int
            description: Pad the image before the deconvolution.
            default: 128
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml

Citations
--------------------------

Preprocessing techniques for removing artifacts in synchrotron-based tomographic images by Vo, Nghia T et al.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Bibtex
""""""""""""""""""""""""""""""""""""""""""

.. code-block:: none

    @inproceedings{vo2019preprocessing,
      title={Preprocessing techniques for removing artifacts in synchrotron-based tomographic images},
      author={Vo, Nghia T and Atwood, Robert C and Drakopoulos, Michael},
      booktitle={Developments in X-Ray Tomography XII},
      volume={11113},
      pages={111131I},
      year={2019},
      organization={International Society for Optics and Photonics}
      publisher = {SPIE},
      pages = {309 -- 328},
      year = {2019},
      doi = {10.1117/12.2530324},
      URL = {https://doi.org/10.1117/12.2530324}
    }
    

Endnote
""""""""""""""""""""""""""""""""""""""""""

.. code-block:: none

    %0 Conference Proceedings
    %T Preprocessing techniques for removing artifacts in synchrotron-based tomographic images
    %A Vo, Nghia T
    %A Atwood, Robert C
    %A Drakopoulos, Michael
    %B Developments in X-Ray Tomography XII
    %V 11113
    %P 111131I
    %D 2019
    %I International Society for Optics and Photonics
    

