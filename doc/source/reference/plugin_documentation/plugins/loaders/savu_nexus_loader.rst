{% extends "plugin_template.rst" %}

{% block title %}Savu Nexus Loader{% endblock %}

{% block description %}
A class to load datasets, and associated metadata, from a Savu output nexus file. By default, the last instance of each unique dataset name will be loaded. Opt instead to load a subset of these datasets, or individual datasets by populating the parameters. 
{% endblock %}

{% block parameter_yaml %}

        preview:
            visibility: basic
            dtype: "[preview, dict{str:preview}, dict{}]"
            description: A slice list of required frames to apply to ALL datasets, else a dictionary of slice lists where the key is the dataset name.
            default: 
        
        datasets:
            visibility: basic
            dtype: "[list[],list[str]]"
            description: Override the default by choosing specific dataset(s) to load, by stating the NXdata name.
            default: "[]"
        
        names:
            visibility: intermediate
            dtype: "[list[],list[str]]"
            description: Override the dataset names associated with the datasets parameter above.
            default: "[]"
        
{% endblock %}

{% block plugin_citations %}
    No citations
{% endblock %}

{% block plugin_file %}../../../plugin_api/plugins.loaders.savu_nexus_loader.rst{% endblock %}
