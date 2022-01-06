{% extends "/home/glb23482/git_projects/Savu/doc/source/reference/savu_commands/plugin_template.rst" %}

{% block title %}Ortho Slice{% endblock %}

{% block description %}
A plugin to extract slices in each direction of a 3D reconstructed volume. 
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
            default: "['XY', 'YZ', 'XZ']"
        
        xy_slices:
            visibility: basic
            dtype: int
            description: which XY slices to render.
            default: "500"
        
        yz_slices:
            visibility: basic
            dtype: int
            description: which YZ slices to render.
            default: "500"
        
        xz_slices:
            visibility: basic
            dtype: int
            description: which XZ slices to render.
            default: "500"
        
        file_type:
            visibility: basic
            dtype: str
            description: File type to save as
            default: png
        
{% endblock %}

{% block plugin_citations %}
    No citations
{% endblock %}

{% block plugin_file %}../../../plugin_api/plugins.visualisation.ortho_slice.rst{% endblock %}
