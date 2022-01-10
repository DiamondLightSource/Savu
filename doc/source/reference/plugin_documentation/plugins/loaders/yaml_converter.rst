{% extends "plugin_template.rst" %}

{% block title %}Yaml Converter{% endblock %}

{% block description %}
A class to load data from a non-standard nexus/hdf5 file using descriptions loaded from a yaml file. 
{% endblock %}

{% block parameter_yaml %}

        preview:
            visibility: basic
            dtype: preview
            description: A slice list of required frames.
            default: "[]"
        
        yaml_file:
            visibility: basic
            dtype: "[None,yamlfilepath]"
            description: Path to the file containing the data descriptions.
            default: None
        
        template_param:
            visibility: hidden
            dtype: "[str,dict]"
            description: A hidden parameter to hold parameters passed in via a savu template file.
            default: 
        
{% endblock %}

{% block plugin_citations %}
    No citations
{% endblock %}

{% block plugin_file %}../../../plugin_api/plugins.loaders.yaml_converter.rst{% endblock %}
