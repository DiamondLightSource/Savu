Tomo Phantom Loader
########################################################

Description
--------------------------

A hdf5 dataset of a specified size is created at runtime using Tomophantom to generate synthetic data , saved with relevant meta_data to a NeXus file, and used as input. It recreates the behaviour of the nxtomo loader but with synthetic data.  The input file path passed to Savu will be ignored (use a dummy). 

Parameters
--------------------------

.. code-block:: yaml

        preview:
            visibility: basic
            dtype: preview
            description: A slice list of required frames.
            default: "[]"
        
        proj_data_dims:
            visibility: basic
            dtype: "[list[float], list[]]"
            description: "A list specifiying the sizes of dimensions of the generated 3D               projection data in the following format [Angles, DetectorsY, DetectorsX]."
            default: "[180, 128, 160]"
        
        axis_labels:
            visibility: basic
            dtype: "list[str]"
            description: A list of axis labels.
            default: "['rotation_angle.degrees', 'detector_y.pixels', 'detector_x.pixels']"
        
        tomo_model:
            visibility: basic
            dtype: int
            description: Select a model number from the library (see TomoPhantom dat files).
            default: "13"
        
        patterns:
            visibility: hidden
            dtype: "list[str]"
            description: Patterns.
            default: "['SINOGRAM.0c.1s.2c', 'PROJECTION.0s.1c.2c']"
        
        axis_labels_phantom:
            visibility: hidden
            dtype: "list[str]"
            description: A list of axis labels.
            default: "['detector_z.pixels', 'detector_y.pixels', 'detector_x.pixels']"
        
        patterns_tomo:
            visibility: hidden
            dtype: "list[str]"
            description: Patterns.
            default: "['VOLUME_XZ.0c.1s.2c']"
        
        out_datasets:
            visibility: datasets
            dtype: "list[str]"
            description: The names assigned to the datasets.
            default: "['synth_proj_data', 'phantom']"
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml

Citations
--------------------------

TomoPhantom, a software package to generate 2D-4D analytical phantoms for CT image reconstruction algorithm benchmarks by Kazantsev, Daniil et al.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Bibtex
""""""""""""""""""""""""""""""""""""""""""

.. code-block:: none

    @article{kazantsev2018tomophantom,
      title={TomoPhantom, a software package to generate 2D-4D analytical phantoms for CT image reconstruction algorithm benchmarks},
      author={Kazantsev, Daniil and Pickalov, Valery and Nagella, Srikanth and Pasca, Edoardo and Withers, Philip J},
      journal={SoftwareX},
      volume={7},
      pages={150--155},
      year={2018},
      publisher={Elsevier}
    }
    

Endnote
""""""""""""""""""""""""""""""""""""""""""

.. code-block:: none

    %0 Journal Article
    %T TomoPhantom, a software package to generate 2D-4D analytical phantoms for CT image reconstruction algorithm benchmarks
    %A Kazantsev, Daniil
    %A Pickalov, Valery
    %A Nagella, Srikanth
    %A Pasca, Edoardo
    %A Withers, Philip J
    %J SoftwareX
    %V 7
    %P 150-155
    %@ 2352-7110
    %D 2018
    %I Elsevier
    

