{% extends "/home/glb23482/git_projects/Savu/doc/source/reference/savu_commands/plugin_template.rst" %}

{% block title %}Ring Removal Waveletfft{% endblock %}

{% block description %}
Wavelet-FFt-based method working in the sinogram space to remove ring artifacts. 

.. toctree::
    Plugin documention and guidelines on use </../../../plugin_guides/plugins/ring_removal/ring_removal_waveletfft_doc.rst>

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
        
        sigma:
            visibility: basic
            dtype: int
            description: Damping parameter. Larger is stronger.
            default: "1"
        
        level:
            visibility: basic
            dtype: int
            description: Wavelet decomposition level.
            default: "4"
        
        nvalue:
            visibility: intermediate
            dtype: int
            description: Order of the the Daubechies (DB) wavelets.
            default: "8"
        
        padFT:
            visibility: intermediate
            dtype: int
            description: Padding for Fourier transform
            default: "20"
        
{% endblock %}

{% block plugin_citations %}
    No citations
{% endblock %}

{% block plugin_file %}../../../plugin_api/plugins.ring_removal.ring_removal_waveletfft.rst{% endblock %}
