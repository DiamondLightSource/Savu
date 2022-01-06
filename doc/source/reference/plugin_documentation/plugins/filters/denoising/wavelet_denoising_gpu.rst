{% extends "/home/glb23482/git_projects/Savu/doc/source/reference/savu_commands/plugin_template.rst" %}

{% block title %}Wavelet Denoising Gpu{% endblock %}

{% block description %}
A Wrapper for pypwt package for wavelet GPU denoising. 
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
        
        family_name:
            visibility: intermediate
            dtype: str
            options: "['db3', 'db5', 'db7', 'db9', 'db11', 'haar', 'sym3', 'sym5', 'sym7', 'sym11']"
            description: Wavelet family.
            default: db5
        
        nlevels:
            visibility: intermediate
            dtype: int
            description: Level of refinement for filter coefficients.
            default: "3"
        
        threshold_level:
            visibility: basic
            dtype: float
            description: 
                summary: Threshold level to filter wavelet coefficients
                verbose: Smaller values lead to more smoothing
            default: "0.01"
        
        pattern:
            visibility: intermediate
            dtype: str
            description: Pattern to apply this to.
            default: PROJECTION
        
{% endblock %}

{% block plugin_citations %}
        
        **PDWT: Release 0.8 by Paleo, Pierre et al.**
        
        **Bibtex**
        
        .. code-block:: none
        
            @article{paleo_pdwt_2020,
            title={PDWT: Release 0.8},
            author={Pierre Paleo},
            journal={Zenodo},
            volume={},
            pages={},
            year={2020},
            publisher={Zenodo}
            }
            
        
        **Endnote**
        
        .. code-block:: none
        
            %0 Journal Article
            %T PDWT: Release 0.8
            %A Paleo, Pierre
            %J Zenodo
            %D 2020
            %I Zenodo
            
        
        
{% endblock %}

{% block plugin_file %}../../../../plugin_api/plugins.filters.denoising.wavelet_denoising_gpu.rst{% endblock %}
