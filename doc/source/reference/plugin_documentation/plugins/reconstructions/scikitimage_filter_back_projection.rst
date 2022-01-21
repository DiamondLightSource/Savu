{% extends "plugin_template.rst" %}

{% block title %}Scikitimage Filter Back Projection{% endblock %}

{% block description %}
A Plugin to reconstruct an image by filter back projection using the inverse radon transform from scikit-image. 
{% endblock %}

{% block parameter_yaml %}

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
        
        centre_of_rotation:
            visibility: basic
            dtype: "[float, str, dict{int:float}]"
            description: Centre of rotation to use for the reconstruction.
            default: "0.0"
            example: It could be a fixed value, a dictionary of (sinogram number, value) pairs for a polynomial fit of degree 1, or a dataset name.
        
        init_vol:
            visibility: intermediate
            dtype: "[None, str]"
            description: Dataset to use as volume initialiser (does not currently work with preview)
            default: None
            example: "Type the name of the initialised dataset e.g. ['tomo']"
        
        log:
            visibility: intermediate
            dtype: bool
            description: 
                summary: Option to take the log of the data before reconstruction.
                verbose: Should be set to false if you use PaganinFilter
            default: "True"
            example: Set to True to take the log of the data before reconstruction.
        
        preview:
            visibility: intermediate
            dtype: preview
            description: A slice list of required frames.
            default: "[]"
        
        force_zero:
            visibility: intermediate
            dtype: "[list[float,float],list[None,None]]"
            description: Set any values in the reconstructed image outside of this range to zero.
            default: "['None', 'None']"
            example: "[0, 1]"
        
        ratio:
            visibility: intermediate
            dtype: "[float, list[float, float]]"
            description: Ratio of the masks diameter in pixels to the smallest edge size along given axis. If a list of two floats is given, the second value is used to fill up the area outside the mask.
            default: "0.95"
        
        log_func:
            visibility: advanced
            dtype: str
            description: Override the default log function with a numpy statement
            default: np.nan_to_num(-np.log(sino))
        
        vol_shape:
            visibility: hidden
            dtype: "[str, int]"
            description: 
                summary: Override the size of the reconstruction volume with an integer value.
                verbose: When fixed, you get the dimension of the horizontal detector or you can specify any reconstruction size you like with an integer.
            default: fixed
        
        output_size:
            visibility: intermediate
            dtype: "[None, int,list[int,int],str]"
            description: "Integer number of rows and columns in the reconstruction, or 'auto'."
            default: auto
        
        filter:
            visibility: intermediate
            dtype: str
            description: Filter used in frequency domain filtering.
            options: "['ramp', 'shepp-logan', 'cosine', 'hamming', 'hann', 'None']"
            default: ramp
        
        interpolation:
            visibility: intermediate
            dtype: int
            description: "Interpolation method used in reconstruction ('cubic' option is slow)"
            options: "['linear', 'nearest', 'cubic']"
            default: linear
        
        circle:
            visibility: intermediate
            dtype: bool
            description: Assume the reconstructed image is zero outside the inscribed circle. Also changes the default output_size to match the behaviour of radon called with circle=True.
            default: "False"
        
{% endblock %}

{% block plugin_citations %}
        
        **Principles Of Ct Imaging by Kak, Avinash C et al.**
        
        **Bibtex**
        
        .. code-block:: none
        
            @article{kak2002principles,
            title={Principles of computerized tomographic imaging},
            author={Kak, Avinash C and Slaney, Malcolm and Wang, Ge},
            journal={Medical Physics},
            volume={29},
            number={1},
            pages={107--107},
            year={2002},
            publisher={Wiley Online Library}
            }
            
        
        **Endnote**
        
        .. code-block:: none
        
            %0 Journal Article
            %T Principles of computerized tomographic imaging
            %A Kak, Avinash C
            %A Slaney, Malcolm
            %A Wang, Ge
            %J Medical Physics
            %V 29
            %N 1
            %P 107-107
            %@ 0094-2405
            %D 2002
            %I Wiley Online Library
            
        
        
{% endblock %}

{% block plugin_file %}../../../plugin_api/plugins.reconstructions.scikitimage_filter_back_projection.rst{% endblock %}
