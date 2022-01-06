{% extends "/home/glb23482/git_projects/Savu/doc/source/reference/savu_commands/plugin_template.rst" %}

{% block title %}Pyfai Azimuthal Integrator With Bragg Filter{% endblock %}

{% block description %}
Uses pyfai to remap the data. We then remap, percentile file and integrate. 
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
        
        use_mask:
            visibility: basic
            dtype: bool
            description: Option to apply a mask.
            default: "False"
        
        num_bins:
            visibility: basic
            dtype: int
            description: Number of bins.
            default: "1005"
        
        num_bins_azim:
            visibility: basic
            dtype: int
            description: Number of azimuthal bins.
            default: "200"
        
        thresh:
            visibility: intermediate
            dtype: "list[float,float]"
            description: Threshold of the percentile filter
            default: "[5, 95]"
        
{% endblock %}

{% block plugin_citations %}
    No citations
{% endblock %}

{% block plugin_file %}../../../plugin_api/plugins.azimuthal_integrators.pyfai_azimuthal_integrator_with_bragg_filter.rst{% endblock %}
