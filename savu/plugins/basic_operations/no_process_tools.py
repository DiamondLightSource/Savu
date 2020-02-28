from savu.plugins.plugin_tools import PluginTools

class NoProcessTools(PluginTools):
    """The base class from which all plugins should inherit.
    """
    def define_parameters(self):
        """---
        pattern:
            visibility: not_param
            dtype: str
            description: Explicitly state the slicing pattern.
            default: None
        other:
            visibility: param
            dtype: int
            description: Temporary parameter for testing.
            default: 10
        yaml_file:
            visibility: param
            dtype: yaml_file
            description: Yaml file path.
            default: savu/plugins/loaders/full_field_loaders/nxtomo_loader.yaml
        vocentering_search_area:
            visibility: user
            dtype: tuple
            description: Search area around the estimated centre of
              rotation
            default: '(-50, 50)'
        ica_w_init:
            visibility: param
            dtype: list
            description: The initial mixing matrix
            default: 'None'
        distcorr_polynomial_coeffs:
            visibility: user
            dtype: tuple
            description: Parameters of the radial distortion function.
            default: '(1.0, 0.0e-1, 0.0e-2, 0.0e-3, 0.0e-4)'
        pymca_config:
            visibility: user
            dtype: config_file
            description: Path to config file
            default: 'Savu/test_data/data/test_config.cfg'
        medianfilt_kernel_size:
            visibility: user
            dtype: tuple
            description: Kernel size for filter
            default: "(1, 3, 3)"
        yamlconverter_yaml_file:
            visibility: user
            dtype: yaml_file
            description: Path to file containing data descriptions
            default: None
        savunexusloader_datasets:
            visibility: user
            dtype: list
            description: Override the default by choosing specific
              dataset(s) to load, by stating the NXdata name
            default: []
        savunexusloader_names:
            visibility: user
            dtype: list
            description: Override the dataset names associated with
              the datasets parameter above
            default: []
        randomhdf5loader_axis_labels:
            visibility: user
            dtype: list
            description: A list of the axis labels to be associated
              with each dimension, of the form ['name1.unit1', 'name2.
              unit2',...].
            default: []
        randomhdf5loader_patterns:
            visibility: user
            dtype: list
            description: A list of data access patterns e.g.
              [SINOGRAM.0c.1s.2c, PROJECTION.0s.1c.2s], where 'c'
              and 's' represent core and slice dimensions respectively
              and every dimension must be specified.
            default: []
        randomhdf5loader_dtype:
            visibility: user
            dtype: nptype
            description: A numpy array data type
            default: int16
        randomhdf5loader_angles:
            visibility: user
            dtype: list
            description: A python statement to be evaluated or a file
            default: None
        multisavuloader_filename:
            visibility: param
            dtype: filename
            description: The shared part of the name of each file
              (not including .nxs)
            default: None
        multisavuloader_stack_or_cat_dim:
            visibility: param
            dtype: int
            description: Dimension to stack or concatenate
            default: 3
        multisavuloader_axis_label:
            visibility: param
            dtype: str
            description: New axis label if required, in form
              'name.units'.
            default: 'scan.number'
        random3Dtomoloader_image_key:
            visibility: user
            dtype: list
            description: Specify position of darks and flats
              (in that order) in the data
            default: "[[0, 1], [2, 3]]"
        dxchangeloader_dark:
            visibility: param
            dtype: '[path, int]'
            description: dark data path and scale value
            default: "['exchange/data_dark', 1]"
        dxchangeloader_flat:
            visibility: param
            dtype: '[path, int]'
            description: flat data path and scale value
            default: "['exchange/data_white', 1]"

"""