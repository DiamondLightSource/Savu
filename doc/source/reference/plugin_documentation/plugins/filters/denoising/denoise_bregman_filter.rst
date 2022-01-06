{% extends "/home/glb23482/git_projects/Savu/doc/source/reference/savu_commands/plugin_template.rst" %}

{% block title %}Denoise Bregman Filter{% endblock %}

{% block description %}
Split Bregman method for solving the denoising Total Variation ROF model. 
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
        
        weight:
            visibility: basic
            dtype: float
            description: Denoising factor.
            default: "2.0"
        
        max_iterations:
            visibility: basic
            dtype: int
            description: Total number of regularisation iterations. The smaller the number of iterations, the smaller the effect of the filtering is. A larger number will affect the speed of the algorithm.
            default: "30"
        
        error_threshold:
            visibility: advanced
            dtype: float
            description: Convergence threshold.
            default: "0.001"
        
        isotropic:
            visibility: advanced
            dtype: "[bool, str]"
            description: Isotropic or Anisotropic filtering.
            options: "['Isotropic', 'Anisotropic']"
            default: "False"
        
{% endblock %}

{% block plugin_citations %}
    No citations
{% endblock %}

{% block plugin_file %}../../../../plugin_api/plugins.filters.denoising.denoise_bregman_filter.rst{% endblock %}
