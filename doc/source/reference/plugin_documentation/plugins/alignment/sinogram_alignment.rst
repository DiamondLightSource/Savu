{% extends "/home/glb23482/git_projects/Savu/doc/source/reference/savu_commands/plugin_template.rst" %}

{% block title %}Sinogram Alignment{% endblock %}

{% block description %}
The centre of mass of each row is determined and then a sine function fit through these to determine the centre of rotation.  The residual between each centre of mass and the sine function is then used to align each row. 
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
        
        threshold:
            visibility: basic
            dtype: "[None,str]"
            description: e.g. a.b will set all values above a to b.
            default: None
        
        p0:
            visibility: basic
            dtype: "list[float,float,float]"
            description: Initial guess for the parameters of scipy.optimize.curve_fit.
            default: "[1, 1, 1]"
        
        type:
            visibility: intermediate
            dtype: str
            description: Either centre_of_mass or shift, with the latter requiring ProjectionVerticalAlignment prior to this plugin.
            default: centre_of_mass
            options: "['centre_of_mass', 'shift']"
        
{% endblock %}

{% block plugin_citations %}
        
        **Chemical imaging of single catalyst particles with scanning μ-XANES-CT and μ-XRF-CT by Price, SWT et al.**
        
        **Bibtex**
        
        .. code-block:: none
        
            @article{price2015chemical,
            title={Chemical imaging of single catalyst particles with scanning $\mu$-XANES-CT and $\mu$-XRF-CT},
            author={Price, SWT and Ignatyev, K and Geraki, K and Basham, M and Filik, J and Vo, NT and Witte, PT and Beale, AM and Mosselmans, JFW},
            journal={Physical Chemistry Chemical Physics},
            volume={17},
            number={1},
            pages={521--529},
            year={2015},
            publisher={Royal Society of Chemistry}}
            
        
        **Endnote**
        
        .. code-block:: none
        
            %0 Journal Article
            %T Chemical imaging of single catalyst particles with scanning μ-XANES-CT and μ-XRF-CT
            %A Price, SWT
            %A Ignatyev, K
            %A Geraki, K
            %A Basham, M
            %A Filik, J
            %A Vo, NT
            %A Witte, PT
            %A Beale, AM
            %A Mosselmans, JFW
            %J Physical Chemistry Chemical Physics
            %V 17
            %N 1
            %P 521-529
            %D 2015
            %I Royal Society of Chemistry
            
        
        
{% endblock %}

{% block plugin_file %}../../../plugin_api/plugins.alignment.sinogram_alignment.rst{% endblock %}
