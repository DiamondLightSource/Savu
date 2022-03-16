{% extends "plugin_template.rst" %}

{% block title %}Phase Unwrapping{% endblock %}

{% block description %}
A plugin to unwrap a phase-image retrieved by another phase retrieval method (e.g. ptychography). Note that values of the input have to be in the range of [-pi; pi]

.. toctree::
    Plugin documention and guidelines on use </../../../plugin_guides/plugins/corrections/phase_unwrapping_doc.rst>

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
        
        n_iterations:
            visibility: basic
            dtype: int
            description: Number of iterations to perform.
            default: "4"
        
        pattern:
            visibility: basic
            dtype: str
            description: Data processing pattern.
            options: "['PROJECTION', 'SINOGRAM']"
            default: PROJECTION
        
{% endblock %}

{% block plugin_citations %}
        
        **by  et al.**
        
        **Bibtex**
        
        .. code-block:: none
        
            @article{Martinez-Carranza:17,
            author = {Juan Martinez-Carranza and Konstantinos Falaggis and Tomasz Kozacki},
            journal = {Appl. Opt.},
            number = {25},
            pages = {7079--7088},
            publisher = {OSA},
            title = {Fast and accurate phase-unwrapping algorithm based on the transport of intensity equation},
            volume = {56},
            month = {Sep},
            year = {2017},
            url = {http://www.osapublishing.org/ao/abstract.cfm?URI=ao-56-25-7079},
            doi = {10.1364/AO.56.007079}}
            
        
        **Endnote**
        
        .. code-block:: none
        
            TI  - Fast and accurate phase-unwrapping algorithm based on the transport of intensity equation
            AU  - Martinez-Carranza, Juan
            AU  - Falaggis, Konstantinos
            AU  - Kozacki, Tomasz
            PB  - OSA
            PY  - 2017
            JF  - Applied Optics
            VL  - 56
            IS  - 25
            SP  - 7079
            EP  - 7088
            UR  - http://www.osapublishing.org/ao/abstract.cfm?URI=ao-56-25-7079
            DO  - 10.1364/AO.56.007079
            
        
        
{% endblock %}

{% block plugin_file %}../../../plugin_api/plugins.corrections.phase_unwrapping.rst{% endblock %}
