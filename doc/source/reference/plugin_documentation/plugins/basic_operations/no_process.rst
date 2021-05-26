No Process
########################################################

Description
--------------------------

The base class from which all plugins should inherit. 

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
        
        preview:
            visibility: basic
            dtype: preview
            description: None
            default: "[]"
        
        savu_nexus_preview:
            visibility: basic
            dtype: "[preview, dict{str:preview}, dict{}]"
            description: A slice list of required frames to apply to ALL datasets, else a dictionary of slice lists where the key is the dataset name.
            default: 
        
        pattern:
            visibility: advanced
            dtype: "[str, None]"
            description: Explicitly state the slicing pattern.
            default: None
        
        int_param:
            visibility: advanced
            dtype: int
            description: Temporary parameter for testing.
            default: "10"
        
        float_param:
            visibility: advanced
            dtype: float
            description: Temporary parameter for testing.
            default: "10.0"
        
        yaml_file:
            visibility: advanced
            dtype: "[yamlfilepath,None]"
            description: Yaml file path.
            default: None
        
        vocentering_search_area:
            visibility: basic
            dtype: "list[int,int]"
            description: Search area around the estimated centre of rotation
            default: "[-50, 50]"
        
        ica_w_init:
            visibility: intermediate
            dtype: "[list,None]"
            description: The initial mixing matrix
            default: None
        
        distcorr_polynomial_coeffs:
            visibility: basic
            dtype: list
            description: Parameters of the radial distortion function.
            default: "[1.0, 0.0, 0.0, 0.0, 0.0]"
        
        pymca_config:
            visibility: intermediate
            dtype: filepath
            description: Pattern used to create and store the hdf5 dataset default is the first pattern in the pattern dictionary.
            default: Savu/test_data/data/test_config.cfg
        
        medianfilt_kernel_size:
            visibility: basic
            dtype: list
            description: Kernel size for filter
            default: "[1, 3, 3]"
        
        yamlconverter_yaml_file:
            visibility: basic
            dtype: "[yamlfilepath,None]"
            description: Path to file containing data descriptions
            default: None
        
        savunexusloader_datasets:
            visibility: basic
            dtype: "[list[],list]"
            description: Override the default by choosing specific dataset(s) to load, by stating the NXdata name
            default: "[]"
        
        savunexusloader_names:
            visibility: basic
            dtype: "[list[],list]"
            description: Override the dataset names associated with the datasets parameter above
            default: "[]"
        
        randomhdf5loader_axis_labels:
            visibility: basic
            dtype: "[list[],list[str]]"
            description: "A list of the axis labels to be associated with each dimension, of the form ['name1.unit1', 'name2. unit2',...]."
            default: "[]"
        
        randomhdf5loader_patterns:
            visibility: basic
            dtype: "[list[],list[str]]"
            description: "A list of data access patterns e.g. [SINOGRAM.0c.1s.2c, PROJECTION.0s.1c.2s], where 'c' and 's' represent core and slice dimensions respectively and every dimension must be specified."
            default: "[]"
        
        randomhdf5loader_nptype:
            visibility: basic
            dtype: nptype
            description: A numpy array data type
            default: int16
        
        randomhdf5loader_angles:
            visibility: basic
            dtype: "[str,list,None]"
            description: A python statement to be evaluated or a file
            default: None
        
        multisavuloader_filename:
            visibility: basic
            dtype: "[str,None]"
            description: The shared part of the name of each file (not including .nxs)
            default: None
        
        multisavuloader_stack_or_cat_dim:
            visibility: basic
            dtype: int
            description: Dimension to stack or concatenate
            default: "3"
        
        multisavuloader_axis_label:
            visibility: basic
            dtype: str
            description: "New axis label if required, in form 'name.units'."
            default: scan.number
        
        random3Dtomoloader_image_key:
            visibility: basic
            dtype: list
            description: Specify position of darks and flats (in that order) in the data
            default: "[[0, 1], [2, 3]]"
        
        dxchangeloader_dark:
            visibility: basic
            dtype: "list[h5path,int]"
            description: dark data path and scale value
            default: "['exchange/data_dark', 1]"
        
        dxchangeloader_flat:
            visibility: basic
            dtype: "list[h5path,int]"
            description: flat data path and scale value
            default: "['exchange/data_white', 1]"
        
        positive_test:
            visibility: basic
            dtype: int
            description: flat data path and scale value
            default: "4"
        
        algorithm:
            visibility: basic
            dtype: str
            description: Option list
            default: FBP
            options: "['SIRT', 'SART', 'FBP', 'ART', 'CGLS', 'BP', 'FP']"
        
        range_param:
            visibility: basic
            dtype: "list[int,int]"
            description: Range required
            default: "[0, 1]"
        
        integer_list_param:
            visibility: basic
            dtype: "list[int]"
            description: int list required
            default: "[0, 1]"
        
        string_list_param:
            visibility: basic
            dtype: "list[str]"
            description: string list required
            default: "['item_one', 'item_two']"
        
        float_list_param:
            visibility: basic
            dtype: "list[float]"
            description: list of numbers required
            default: "[0, 1]"
        
        empty_list_param:
            visibility: basic
            dtype: "[list[],None]"
            description: empty list required
            default: None
        
        dict_param:
            visibility: basic
            dtype: dict
            description: dictionary required
            default: 
                2: "4"
        
        cor_dict_param:
            visibility: basic
            dtype: dict{int:float}
            description: dictionary required
            default: 
                2: "4.0"
        
        savunexusloader_dict_param:
            visibility: basic
            dtype: "[dict{str:preview}, dict{}]"
            description: Dictionary of str and preview dtypes
            default: 
        
        dict_param_2:
            visibility: basic
            dtype: dict{str:preview}
            description: Dictionary of str and preview dtypes
            default: 
                str: 
                    1:
        
        file_path_param:
            visibility: basic
            dtype: filepath
            description: Filepath required
            default: Savu/savu/plugins/loaders/templates/nexus_templates/fluo.yml
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml
