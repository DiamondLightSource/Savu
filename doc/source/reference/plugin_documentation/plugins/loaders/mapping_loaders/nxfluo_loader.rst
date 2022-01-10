{% extends "plugin_template.rst" %}

{% block title %}Nxfluo Loader{% endblock %}

{% block description %}
A class to load tomography data from an NXFluo file. 
{% endblock %}

{% block parameter_yaml %}

        preview:
            visibility: basic
            dtype: preview
            description: A slice list of required frames.
            default: "[]"
        
        fluo_offset:
            visibility: basic
            dtype: float
            description: fluo scale offset.
            default: "0.0"
        
        fluo_gain:
            visibility: intermediate
            dtype: float
            description: fluo gain
            default: "0.01"
        
        name:
            visibility: basic
            dtype: str
            description: The name assigned to the dataset.
            default: fluo
        
{% endblock %}

{% block plugin_citations %}
    No citations
{% endblock %}

{% block plugin_file %}../../../../plugin_api/plugins.loaders.mapping_loaders.nxfluo_loader.rst{% endblock %}
