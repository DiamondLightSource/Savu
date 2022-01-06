{% extends "/home/glb23482/git_projects/Savu/doc/source/reference/savu_commands/plugin_template.rst" %}

{% block title %}Geo Distance3D{% endblock %}

{% block description %}
3D geodesic transformation of volumes with mask initialisation. 
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
            description: The default names.
            default: "['GeoDist']"
        
        lambda:
            visibility: intermediate
            dtype: float
            description: Weighting between 0 and 1
            default: "0.5"
        
        iterations:
            visibility: basic
            dtype: int
            description: The number of iterations for raster scanning.
            default: "4"
        
{% endblock %}

{% block plugin_citations %}
    No citations
{% endblock %}

{% block plugin_file %}../../../../plugin_api/plugins.segmentation.geo_distance.geo_distance3D.rst{% endblock %}
