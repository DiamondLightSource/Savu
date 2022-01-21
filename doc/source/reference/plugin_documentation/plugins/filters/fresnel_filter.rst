{% extends "plugin_template.rst" %}

{% block title %}Fresnel Filter{% endblock %}

{% block description %}
A low-pass filter to improve the contrast of reconstructed images which is similar to the Paganin filter but can work on both sinograms and projections. 

.. toctree::
    Plugin documention and guidelines on use </../../../plugin_guides/plugins/filters/fresnel_filter_doc.rst>

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
        
        ratio:
            visibility: basic
            dtype: float
            description: Control the strength of the filter. Greater is stronger
            default: "100.0"
        
        pattern:
            visibility: basic
            dtype: str
            description: Data processing pattern
            options: "['PROJECTION', 'SINOGRAM']"
            default: SINOGRAM
        
        apply_log:
            visibility: basic
            dtype: bool
            description: Apply the logarithm function to a sinogram before filtering.
            default: "True"
        
{% endblock %}

{% block plugin_citations %}
        
        **Superior techniques for eliminating ring artifacts in X-ray micro-tomography by Vo, Nghia T et al.**
        
        **Bibtex**
        
        .. code-block:: none
        
            @article{Vo:21,
            title = {Data processing methods and data acquisition for samples larger than the field of view in parallel-beam tomography},
            author = {Nghia T. Vo and Robert C. Atwood and Michael Drakopoulos and Thomas Connolley},
            journal = {Opt. Express},
            number = {12},
            pages = {17849--17874},
            publisher = {OSA},
            volume = {29},
            month = {Jun},
            year = {2021},
            doi = {10.1364/OE.418448}}
            
        
        **Endnote**
        
        .. code-block:: none
        
            %0 Journal Article
            %T Superior techniques for eliminating ring artifacts in X-ray micro-tomography
            %A Vo, Nghia T
            %A Atwood, Robert C
            %A Drakopoulos, Michael
            %J Optics express
            %V 26
            %N 22
            %P 28396-28412
            %@ 1094-4087
            %D 2018
            %I Optical Society of America
            
        
        
{% endblock %}

{% block plugin_file %}../../../plugin_api/plugins.filters.fresnel_filter.rst{% endblock %}
