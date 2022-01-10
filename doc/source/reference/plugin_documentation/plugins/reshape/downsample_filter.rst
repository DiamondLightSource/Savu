{% extends "plugin_template.rst" %}

{% block title %}Downsample Filter{% endblock %}

{% block description %}
A plugin to downsample and rescale data volume including options of flipping and rotating images 
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
        
        bin_size:
            visibility: basic
            dtype: int
            description: Bin Size for the downsample.
            default: "3"
        
        mode:
            visibility: basic
            dtype: str
            description: "One of 'mean', 'median', 'min', 'max'."
            default: mean
            options: "['mean', 'median', 'min', 'max']"
        
        pattern:
            visibility: basic
            dtype: str
            description: "One of 'PROJECTION' or 'SINOGRAM' or 'VOLUME_XZ'."
            default: PROJECTION
            options: "['PROJECTION', 'SINOGRAM', 'VOLUME_XZ']"
        
        num_bit:
            visibility: basic
            dtype: int
            description: Bit depth of the rescaled data (8, 16 or 32).
            default: "32"
            options: "[8, 16, 32]"
        
        flip_updown:
            visibility: basic
            dtype: bool
            description: Flip images up-down.
            default: "True"
        
        flip_leftright:
            visibility: basic
            dtype: bool
            description: Flip images left-right.
            default: "False"
        
        rotate_angle:
            visibility: basic
            dtype: "[float, str, list[float], dict{int:float}]"
            description: Rotate images by a given angle (Degree).
            default: "0.0"
        
        max:
            visibility: basic
            dtype: "[None,float]"
            description: Global max for scaling.
            default: None
        
        min:
            visibility: basic
            dtype: "[None,float]"
            description: Global min for scaling.
            default: None
        
{% endblock %}

{% block plugin_citations %}
    No citations
{% endblock %}

{% block plugin_file %}../../../plugin_api/plugins.reshape.downsample_filter.rst{% endblock %}
