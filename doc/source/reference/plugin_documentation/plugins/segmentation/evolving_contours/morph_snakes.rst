{% extends "/home/glb23482/git_projects/Savu/doc/source/reference/savu_commands/plugin_template.rst" %}

{% block title %}Morph Snakes{% endblock %}

{% block description %}
A Plugin to segment reconstructed data using Morphsnakes module. When initialised with a mask, the active contour propagates to find the minimum of energy (a possible edge countour). 
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
            description: The default names
            default: "['MASK_MORPH_EVOLVED']"
        
        lambda1:
            visibility: basic
            dtype: float
            description: Weight parameter for the outer region, if lambda1 is larger than lambda2, the outer region will contain a larger range of values than the inner region.
            default: "1"
        
        lambda2:
            visibility: basic
            dtype: float
            description: Weight parameter for the inner region, if lambda2 is larger than lambda1, the inner region will contain a larger range of values than the outer region.
            default: "1"
        
        smoothing:
            visibility: intermediate
            dtype: int
            description: Number of times the smoothing operator is applied per iteration, reasonable values are around 1-4 and larger values lead to smoother segmentations.
            default: "1"
        
        iterations:
            visibility: basic
            dtype: int
            description: The number of iterations.
            default: "350"
        
        pattern:
            visibility: intermediate
            dtype: str
            description: Pattern to apply to this.
            default: VOLUME_YZ
        
{% endblock %}

{% block plugin_citations %}
    No citations
{% endblock %}

{% block plugin_file %}../../../../plugin_api/plugins.segmentation.evolving_contours.morph_snakes.rst{% endblock %}
