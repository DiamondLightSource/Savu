{% extends "/home/glb23482/git_projects/Savu/doc/source/reference/savu_commands/plugin_template.rst" %}

{% block title %}Tomo Phantom Quantification{% endblock %}

{% block description %}
A plugin to calculate some standard image quality metrics 
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
            description: Default out dataset names.
            default: "['quantification_values']"
        
        pattern:
            visibility: intermediate
            dtype: str
            options: "['SINOGRAM', 'PROJECTION', 'VOLUME_XZ']"
            description: Pattern to apply this to.
            default: SINOGRAM
        
{% endblock %}

{% block plugin_citations %}
    No citations
{% endblock %}

{% block plugin_file %}../../../plugin_api/plugins.simulation.tomo_phantom_quantification.rst{% endblock %}
