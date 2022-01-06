{% extends "/home/glb23482/git_projects/Savu/doc/source/reference/savu_commands/plugin_template.rst" %}

{% block title %}Projection Shift{% endblock %}

{% block description %}
Horizontal and vertical shift are calculated using a chosen method and added to the metadata.  The vertical and horizontal shifts can be corrected using the ProjectionVerticalAlignment and SinogramAlignment (in 'shift' mode) plugins respectively. Method: Uses either skimage template_matching or orb feature tracking plus robust ransac matching to calculate the translation between different combinations of 10 consecutive projection images. A least squares solution to the shift values between images is calculated and returned for the middle 8 images. 

.. toctree::
    Plugin documention and guidelines on use </../../../plugin_guides/plugins/alignment/projection_shift_doc.rst>

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
            description: Set the output dataset name
            default: "['proj_shift']"
        
        method:
            visibility: intermediate
            dtype: str
            description: Method used to calculate the shift between images.
            default: orb_ransac
            options: "['template_matching', 'orb_ransac']"
        
        template:
            visibility: basic
            dtype: "[list[str],None]"
            description: "Position of the template to match (required) e.g. [300:500, 300:500]."
            default: None
        
        threshold:
            visibility: intermediate
            dtype: "[list[float,float],None]"
            description: "e.g. [a, b] will set all values above a to b."
            default: None
        
        n_keypoints:
            dependency: 
                method: orb_ransac
            visibility: intermediate
            dtype: int
            description: Number of keypoints to use in ORB feature detector.
            default: "20"
        
{% endblock %}

{% block plugin_citations %}
    No citations
{% endblock %}

{% block plugin_file %}../../../plugin_api/plugins.alignment.projection_shift.rst{% endblock %}
