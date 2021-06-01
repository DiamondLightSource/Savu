Mtf Deconvolution
########################################################

Description
--------------------------

Method to correct the point-spread-function effect. Working on raw     projections and flats. 

.. toctree::
    Plugin documention and guidelines on use </../../../plugin_guides/plugins/corrections/mtf_deconvolution_doc.rst>

Parameter definitions
--------------------------

.. code-block:: yaml

        in_datasets:
            visibility: datasets
            dtype: "[list[],list[str]]"
            description: 
                summary: A list of the dataset(s) to process.
                verbose: A list of strings, where each string gives the name of a dataset that was either specified by a loader plugin or created as output to a previous plugin.  The length of the list is the number of input datasets requested by the plugin.  If there is only one dataset and the list is left empty it will default to that dataset.
            default: "[]"
        
        out_datasets:
            visibility: datasets
            dtype: "[list[],list[str]]"
            description: 
                summary: A list of the dataset(s) to create.
                verbose: A list of strings, where each string is a name to be assigned to a dataset output by the plugin. If there is only one input dataset and one output dataset and the list is left empty, the output will take the name of the input dataset. The length of the list is the number of output datasets created by the plugin.
            default: "[]"
        
        file_path:
            visibility: basic
            dtype: "[None,filepath]"
            description: "Path to file containing a 2D array of a MTF function. File formats are 'npy', or 'tif'."
            default: None
        
        pad_width:
            visibility: basic
            dtype: int
            description: Pad the image before the deconvolution.
            default: "128"
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
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
    

