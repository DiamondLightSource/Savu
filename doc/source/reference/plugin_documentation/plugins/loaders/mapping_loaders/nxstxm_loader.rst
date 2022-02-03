{% extends "plugin_template.rst" %}

{% block title %}Nxstxm Loader{% endblock %}

{% block description %}
A class to load tomography data from an NXstxm file. 
{% endblock %}

{% block parameter_yaml %}

        preview:
            visibility: basic
            dtype: preview
            description: A slice list of required frames.
            default: "[]"
        
        name:
            visibility: basic
            dtype: str
            description: The name assigned to the dataset.
            default: stxm
        
{% endblock %}

{% block plugin_citations %}
    No citations
{% endblock %}

{% block plugin_file %}../../../../plugin_api/plugins.loaders.mapping_loaders.nxstxm_loader.rst{% endblock %}
