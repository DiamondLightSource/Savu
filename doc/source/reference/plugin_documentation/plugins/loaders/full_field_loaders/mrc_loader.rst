{% extends "/home/glb23482/git_projects/Savu/doc/source/reference/savu_commands/plugin_template.rst" %}

{% block title %}Mrc Loader{% endblock %}

{% block description %}
Load Medical Research Council (MRC) formatted image data. 
{% endblock %}

{% block parameter_yaml %}

        preview:
            visibility: basic
            dtype: preview
            description: A slice list of required frames.
            default: "[]"
        
        angles:
            visibility: basic
            dtype: "[str, int, None]"
            description: A python statement to be evaluated (e.g np.linspace(0, 180, nAngles)) or a txt file.
            default: None
        
        name:
            visibility: intermediate
            dtype: str
            description: The name assigned to the dataset
            default: tomo
        
{% endblock %}

{% block plugin_citations %}
    No citations
{% endblock %}

{% block plugin_file %}../../../../plugin_api/plugins.loaders.full_field_loaders.mrc_loader.rst{% endblock %}
