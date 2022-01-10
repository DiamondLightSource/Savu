{% extends "plugin_template.rst" %}

{% block title %}Ccpi Denoising Cpu{% endblock %}

{% block description %}
Wrapper for CCPi-Regularisation Toolkit (CPU) for efficient 2D/3D denoising 
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
        
        method:
            visibility: advanced
            dtype: str
            options: "['ROF_TV', 'PD_TV', 'FGP_TV', 'SB_TV', 'NLTV', 'TGV', 'LLT_ROF', 'NDF', 'Diff4th']"
            description: 
                summary: The denoising method
                verbose: Variational denoising algorithms can be used to filter the data while preserving the important features
                options: 
                    ROF_TV: Rudin-Osher-Fatemi Total Variation model
                    PD_TV: Primal-Dual Total variation model
                    FGP_TV: Fast Gradient Projection Total Variation model
                    SB_TV: Split Bregman Total Variation model
                    LLT_ROF: Lysaker, Lundervold and Tai model combined with Rudin-Osher-Fatemi
                    NDF: Nonlinear/Linear Diffusion model (Perona-Malik, Huber or Tukey)
                    TGV: Total Generalised Variation
                    NLTV: Non Local Total Variation
                    Diff4th: Fourth-order nonlinear diffusion model
            default: FGP_TV
        
        reg_parameter:
            visibility: basic
            dtype: float
            description: 
                summary: The regularisation (smoothing) parameter. The higher the value, the stronger the smoothing effect
                range: Recommended between 0 and 0.001
            default: "1e-05"
        
        max_iterations:
            visibility: basic
            dtype: int
            description: 
                summary: Total number of regularisation iterations.  The smaller the number of iterations, the smaller the effect of the filtering is.  A larger number will affect the speed of the algorithm.
                range: Recommended value dependent upon method.
            default: 
                method: 
                    ROF_TV: "2000"
                    FGP_TV: "500"
                    PD_TV: "500"
                    SB_TV: "100"
                    LLT_ROF: "2000"
                    NDF: "2000"
                    Diff4th: "1000"
                    TGV: "500"
                    NLTV: "5"
        
        time_step:
            visibility: advanced
            dtype: float
            dependency: 
                regularisation_method: 
                    ROF_TV
                    LLT_ROF
                    NDF
                    Diff4th
            description: 
                summary: Time marching parameter for convergence of explicit schemes
                verbose: the time step constant defines the speed of convergence, the larger values can lead to divergence
                range: Recommended between 0.0001 and 0.003
            default: "0.003"
        
        lipshitz_constant:
            visibility: advanced
            dtype: float
            description: TGV method, Lipshitz constant.
            default: "12"
            dependency: 
                method: TGV
        
        alpha1:
            visibility: advanced
            dtype: float
            description: TGV method, parameter to control the 1st-order term.
            default: "1.0"
            dependency: 
                method: TGV
        
        alpha0:
            visibility: advanced
            dtype: float
            description: TGV method, parameter to control the 2nd-order term.
            default: "2.0"
            dependency: 
                method: TGV
        
        reg_parLLT:
            visibility: advanced
            dtype: float
            dependency: 
                method: LLT_ROF
            description: LLT-ROF method, parameter to control the 2nd-order term.
            default: "0.05"
        
        penalty_type:
            visibility: advanced
            dtype: str
            options: "['huber', 'perona', 'tukey', 'constr', 'constrhuber']"
            description: 
                summary: Penalty type
                verbose: Nonlinear/Linear Diffusion model (NDF) specific penalty type.
                options: 
                    huber: Huber
                    perona: Perona-Malik model
                    tukey: Tukey
                    constr: None
                    constrhuber: None
            dependency: 
                method: NDF
            default: huber
        
        edge_par:
            visibility: advanced
            dtype: float
            dependency: 
                method: 
                    NDF
                    Diff4th
            description: NDF and Diff4th methods, noise magnitude parameter.
            default: "0.01"
        
        tolerance_constant:
            visibility: advanced
            dtype: float
            description: Tolerance constant to stop iterations earlier.
            default: "0.0"
        
        pattern:
            visibility: advanced
            dtype: str
            description: Pattern to apply this to.
            default: VOLUME_XZ
        
{% endblock %}

{% block plugin_citations %}
        
        **Ccpi-regularisation toolkit for computed tomographic image reconstruction with proximal splitting algorithms by Kazantsev, Daniil et al.**
        
        **Bibtex**
        
        .. code-block:: none
        
            @article{kazantsev2019ccpi,
            title={Ccpi-regularisation toolkit for computed tomographic image reconstruction with proximal splitting algorithms},
            author={Kazantsev, Daniil and Pasca, Edoardo and Turner, Martin J and Withers, Philip J},
            journal={SoftwareX},
            volume={9},
            pages={317--323},
            year={2019},
            publisher={Elsevier}
            }
            
        
        **Endnote**
        
        .. code-block:: none
        
            %0 Journal Article
            %T Ccpi-regularisation toolkit for computed tomographic image reconstruction with proximal splitting algorithms
            %A Kazantsev, Daniil
            %A Pasca, Edoardo
            %A Turner, Martin J
            %A Withers, Philip J
            %J SoftwareX
            %V 9
            %P 317-323
            %@ 2352-7110
            %D 2019
            %I Elsevier
            
        
        
        **Nonlinear total variation based noise removal algorithms by Rudin, Leonid I et al.**
        
        (Please use this citation if you are using the ROF_TV method
        
        **Bibtex**
        
        .. code-block:: none
        
            @article{rudin1992nonlinear,
              title={Nonlinear total variation based noise removal algorithms},
              author={Rudin, Leonid I and Osher, Stanley and Fatemi, Emad},
              journal={Physica D: nonlinear phenomena},
              volume={60},
              number={1-4},
              pages={259--268},
              year={1992},
              publisher={North-Holland}
            }
            
        
        **Endnote**
        
        .. code-block:: none
        
            %0 Journal Article
            %T Nonlinear total variation based noise removal algorithms
            %A Rudin, Leonid I
            %A Osher, Stanley
            %A Fatemi, Emad
            %J Physica D: nonlinear phenomena
            %V 60
            %N 1-4
            %P 259-268
            %@ 0167-2789
            %D 1992
            %I North-Holland
            
        
        
        **Fast gradient-based algorithms for constrained total variation image denoising and deblurring problems by Beck, Amir et al.**
        
        (Please use this citation if you are using the FGP_TV method
        
        **Bibtex**
        
        .. code-block:: none
        
            @article{beck2009fast,
              title={Fast gradient-based algorithms for constrained total variation image denoising and deblurring problems},
              author={Beck, Amir and Teboulle, Marc},
              journal={IEEE transactions on image processing},
              volume={18},
              number={11},
              pages={2419--2434},
              year={2009},
              publisher={IEEE}
            }
            
        
        **Endnote**
        
        .. code-block:: none
        
            %0 Journal Article
            %T Fast gradient-based algorithms for constrained total variation image denoising and deblurring problems
            %A Beck, Amir
            %A Teboulle, Marc
            %J IEEE transactions on image processing
            %V 18
            %N 11
            %P 2419-2434
            %@ 1057-7149
            %D 2009
            %I IEEE
            
        
        
        **The split Bregman method for L1-regularized problems by Goldstein, Tom et al.**
        
        (Please use this citation if you are using the SB_TV method
        
        **Bibtex**
        
        .. code-block:: none
        
            @article{goldstein2009split,
               title={The split Bregman method for L1-regularized problems},
               author={Goldstein, Tom and Osher, Stanley},
               journal={SIAM journal on imaging sciences},
               volume={2},
               number={2},
               pages={323--343},
               year={2009},
               publisher={SIAM}
             }
            
        
        **Endnote**
        
        .. code-block:: none
        
            %0 Journal Article
            %T The split Bregman method for L1-regularized problems
            %A Goldstein, Tom
            %A Osher, Stanley
            %J SIAM journal on imaging sciences
            %V 2
            %N 2
            %P 323-343
            %@ 1936-4954
            %D 2009
            %I SIAM
            
        
        
        **Total generalized variation by Bredies, Kristian et al.**
        
        (Please use this citation if you are using the TGV method
        
        **Bibtex**
        
        .. code-block:: none
        
            @article{bredies2010total,
               title={Total generalized variation},
               author={Bredies, Kristian and Kunisch, Karl and Pock, Thomas},
               journal={SIAM Journal on Imaging Sciences},
               volume={3},
               number={3},
               pages={492--526},
               year={2010},
               publisher={SIAM}
             }
            
        
        **Endnote**
        
        .. code-block:: none
        
            %0 Journal Article
            %T Total generalized variation
            %A Bredies, Kristian
            %A Kunisch, Karl
            %A Pock, Thomas
            %J SIAM Journal on Imaging Sciences
            %V 3
            %N 3
            %P 492-526
            %@ 1936-4954
            %D 2010
            %I SIAM
            
        
        
        **Model-based iterative reconstruction using higher-order regularization of dynamic synchrotron data by Kazantsev, Daniil et al.**
        
        (Please use this citation if you are using the LLT_ROF method
        
        **Bibtex**
        
        .. code-block:: none
        
            @article{kazantsev2017model,
             title={Model-based iterative reconstruction using higher-order regularization of dynamic synchrotron data},
             author={Kazantsev, Daniil and Guo, Enyu and Phillion, AB and Withers, Philip J and Lee, Peter D},
             journal={Measurement Science and Technology},
             volume={28},
             number={9},
             pages={094004},
             year={2017},
             publisher={IOP Publishing}
             }
            
        
        **Endnote**
        
        .. code-block:: none
        
            %0 Journal Article
            %T Model-based iterative reconstruction using higher-order regularization of dynamic synchrotron data
            %A Kazantsev, Daniil
            %A Guo, Enyu
            %A Phillion, AB
            %A Withers, Philip J
            %A Lee, Peter D
            %J Measurement Science and Technology
            %V 28
            %N 9
            %P 094004
            %@ 0957-0233
            %D 2017
            %I IOP Publishing
            
        
        
        **Scale-space and edge detection using anisotropic diffusion by Perona, Pietro et al.**
        
        (Please use this citation if you are using the NDF method
        
        **Bibtex**
        
        .. code-block:: none
        
            @article{perona1990scale,
               title={Scale-space and edge detection using anisotropic diffusion},
               author={Perona, Pietro and Malik, Jitendra},
               journal={IEEE Transactions on pattern analysis and machine intelligence},
               volume={12},
               number={7},
               pages={629--639},
               year={1990},
               publisher={IEEE}}
            
        
        **Endnote**
        
        .. code-block:: none
        
            %0 Journal Article
            %T Scale-space and edge detection using anisotropic diffusion
            %A Perona, Pietro
            %A Malik, Jitendra
            %J IEEE Transactions on pattern analysis and machine intelligence
            %V 12
            %N 7
            %P 629-639
            %@ 0162-8828
            %D 1990
            %I IEEE
            
        
        
        **An anisotropic fourth-order diffusion filter for image noise removal by Hajiaboli, Mohammad Reza et al.**
        
        (Please use this citation if you are using the Diff4th method
        
        **Bibtex**
        
        .. code-block:: none
        
            @article{hajiaboli2011anisotropic,
             title={An anisotropic fourth-order diffusion filter for image noise removal},
             author={Hajiaboli, Mohammad Reza},
             journal={International Journal of Computer Vision},
             volume={92},
             number={2},
             pages={177--191},
             year={2011},
             publisher={Springer}
             }
            
        
        **Endnote**
        
        .. code-block:: none
        
            %0 Journal Article
            %T An anisotropic fourth-order diffusion filter for image noise removal
            %A Hajiaboli, Mohammad Reza
            %J International Journal of Computer Vision
            %V 92
            %N 2
            %P 177-191
            %@ 0920-5691
            %D 2011
            %I Springer
            
        
        
        **Nonlocal discrete regularization on weighted graphs, a framework for image and manifold processing by Elmoataz, Abderrahim et al.**
        
        (Please use this citation if you are using the NLTV method
        
        **Bibtex**
        
        .. code-block:: none
        
            @article{elmoataz2008nonlocal,
              title={Nonlocal discrete regularization on weighted graphs: a framework for image and manifold processing},
              author={Elmoataz, Abderrahim and Lezoray, Olivier and Bougleux, S{'e}bastien},
              journal={IEEE transactions on Image Processing},
              volume={17},
              number={7},
              pages={1047--1060},
              year={2008},
              publisher={IEEE}
            }
            
        
        **Endnote**
        
        .. code-block:: none
        
            %0 Journal Article
            %T Nonlocal discrete regularization on weighted graphs, a framework for image and manifold processing
            %A Elmoataz, Abderrahim
            %A Lezoray, Olivier
            %A Bougleux, Sebastien
            %J IEEE transactions on Image Processing
            %V 17
            %N 7
            %P 1047-1060
            %@ 1057-7149
            %D 2008
            %I IEEE
            
        
        
{% endblock %}

{% block plugin_file %}../../../../plugin_api/plugins.filters.denoising.ccpi_denoising_cpu.rst{% endblock %}
