from savu.plugins.plugin_tools import PluginTools

class NoProcessTools(PluginTools):
    """The base class from which all plugins should inherit.
    """
    def define_parameters(self):
        """
        preview:
            visibility: basic
            dtype: preview
            description:
            default: []
        savu_nexus_preview:
          visibility: basic
          dtype: [preview, dict{str:preview}, dict{}]
          description: A slice list of required frames to apply to ALL
            datasets, else a dictionary of slice lists where the key is
            the dataset name.
          default: {}
        pattern:
            visibility: advanced
            dtype: [str, None]
            description: Explicitly state the slicing pattern.
            default: None
        int_param:
            visibility: advanced
            dtype: int
            description: Temporary parameter for testing.
            default: 10
        float_param:
            visibility: advanced
            dtype: float
            description: Temporary parameter for testing.
            default: 10.0
        yaml_file:
            visibility: advanced
            dtype: [yamlfilepath,None]
            description: Yaml file path.
            default: None
        vocentering_search_area:
            visibility: basic
            dtype: list[int,int]
            description: Search area around the estimated centre of
              rotation
            default: [-50, 50]
        ica_w_init:
            visibility: intermediate
            dtype: [list,None]
            description: The initial mixing matrix
            default: 'None'
        distcorr_polynomial_coeffs:
            visibility: basic
            dtype: list
            description: Parameters of the radial distortion function.
            default: [1.0, 0.0e-1, 0.0e-2, 0.0e-3, 0.0e-4]
        pymca_config:
            visibility: basic
            dtype: filepath
            description: Path to config file
            default: Savu/test_data/data/test_config.cfg
            visibility: intermediate
            description: Pattern used to create and store the hdf5 dataset
              default is the first pattern in the pattern dictionary.
        medianfilt_kernel_size:
            visibility: basic
            dtype: list
            description: Kernel size for filter
            default: [1, 3, 3]
        yamlconverter_yaml_file:
            visibility: basic
            dtype: [yamlfilepath,None]
            description: Path to file containing data descriptions
            default: None
        savunexusloader_datasets:
            visibility: basic
            dtype: [list[],list]
            description: Override the default by choosing specific
              dataset(s) to load, by stating the NXdata name
            default: []
        savunexusloader_names:
            visibility: basic
            dtype: [list[],list]
            description: Override the dataset names associated with
              the datasets parameter above
            default: []
        randomhdf5loader_axis_labels:
            visibility: basic
            dtype: [list[],list[str]]
            description: A list of the axis labels to be associated
              with each dimension, of the form ['name1.unit1', 'name2.
              unit2',...].
            default: []
        randomhdf5loader_patterns:
            visibility: basic
            dtype: [list[],list[str]]
            description: A list of data access patterns e.g.
              [SINOGRAM.0c.1s.2c, PROJECTION.0s.1c.2s], where 'c'
              and 's' represent core and slice dimensions respectively
              and every dimension must be specified.
            default: []
        randomhdf5loader_nptype:
            visibility: basic
            dtype: nptype
            description: A numpy array data type
            default: int16
        randomhdf5loader_angles:
            visibility: basic
            dtype: [str,list,None]
            description: A python statement to be evaluated or a file
            default: None
        multisavuloader_filename:
            visibility: basic
            dtype: [str,None]
            description: The shared part of the name of each file
              (not including .nxs)
            default: None
        multisavuloader_stack_or_cat_dim:
            visibility: basic
            dtype: int
            description: Dimension to stack or concatenate
            default: 3
        multisavuloader_axis_label:
            visibility: basic
            dtype: str
            description: New axis label if required, in form
              'name.units'.
            default: 'scan.number'
        random3Dtomoloader_image_key:
            visibility: basic
            dtype: list
            description: Specify position of darks and flats
              (in that order) in the data
            default: [[0, 1], [2, 3]]
        dxchangeloader_dark:
            visibility: basic
            dtype: list[h5path,int]
            description: dark data path and scale value
            default: ['exchange/data_dark', 1]
        dxchangeloader_flat:
            visibility: basic
            dtype: list[h5path,int]
            description: flat data path and scale value
            default: ['exchange/data_white', 1]
        positive_test:
            visibility: basic
            dtype: int
            description: flat data path and scale value
            default: 4
        algorithm:
            visibility: basic
            dtype: str
            description: Option list
            default: FBP
            options: [SIRT,SART,FBP,ART,CGLS,BP,FP]
        range_param:
            visibility: basic
            dtype: list[int,int]
            description: Range required
            default: [0,1]
        integer_list_param:
            visibility: basic
            dtype: list[int]
            description: int list required
            default: [0,1]
        string_list_param:
            visibility: basic
            dtype: list[str]
            description: string list required
            default: ['item_one','item_two']
        float_list_param:
            visibility: basic
            dtype: list[float]
            description: list of numbers required
            default: [0,1]
        empty_list_param:
            visibility: basic
            dtype: [list[],None]
            description: empty list required
            default: None
        dict_param:
            visibility: basic
            dtype: dict
            description: dictionary required
            default: "{2:4}"
        cor_dict_param:
            visibility: basic
            dtype: dict{int:float}
            description: dictionary required
            default: "{'2':4.0}"
        savunexusloader_dict_param:
            visibility: basic
            dtype: [dict{str:preview}, dict{}]
            description: Dictionary of str and preview dtypes
            default: {}
        dict_param_2:
            visibility: basic
            dtype: dict{str:preview}
            description: Dictionary of str and preview dtypes
            default: "{'str':['1:']}"
        file_path_param:
            visibility: basic
            dtype: filepath
            description: Filepath required
            default: Savu/savu/plugins/loaders/templates/nexus_templates/fluo.yml
        regularisation_method:
            visibility: advanced
            dtype: str
            options: [ROF_TV, FGP_TV, SB_TV, NLTV, TGV, LLT_ROF, NDF, Diff4th,None]
            description:
                summary: The denoising method
                verbose: Iterative methods can help to solve ill-posed
                  inverse problems by choosing a suitable noise
                  model for the measurement
                options:
                    ROF_TV: Rudin-Osher-Fatemi Total Variation model.
                     It is a good model for piecewise-constant images with
                     sharp abrupt boundaries.
                    FGP_TV: Fast Gradient Projection Total Variation model
                    SB_TV: Split Bregman Total Variation model
                    LLT_ROF: "Lysaker, Lundervold and Tai model combined
                         with Rudin-Osher-Fatemi"
                    NDF: "Nonlinear/Linear Diffusion model (Perona-Malik,
                         Huber or Tukey)"
                    TGV: Total Generalised Variation
                    NLTV: Non Local Total Variation
                    Diff4th: Fourth-order nonlinear diffusion model
            default: FGP_TV
        max_iterations:
            visibility: basic
            dtype: int
            description:
               summary: Total number of regularisation iterations.
                 The smaller the number of iterations, the smaller the effect
                 of the filtering is. A larger number will affect the speed
                 of the algorithm.
               range: Recommended value dependent upon method.
            default:
                 regularisation_method:
                   ROF_TV: 2000
                   FGP_TV: 500
                   SB_TV: 100
                   LLT_ROF: 2000
                   NDF: 2000
                   Diff4th: 1000
                   TGV: 500
                   NLTV: 5
            dependency:
                regularisation_method: [ROF_TV,FGP_TV,SB_TV,LLT_ROF,NDF,Diff4th,TGV,NLTV]
"""