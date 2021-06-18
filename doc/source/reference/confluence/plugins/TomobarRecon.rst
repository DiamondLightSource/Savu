TomobarRecon
-----------------------------

.. raw:: html

    <!DOCTYPE html>
    <html>
        <head>
            <title>Tomography Reconstruction : TomobarRecon</title>
            <link rel="stylesheet" href="styles/site.css" type="text/css" />
            <META http-equiv="Content-Type" content="text/html; charset=UTF-8">
        </head>

        <body class="theme-default aui-theme-default">
            <div id="page">
                <div id="main" class="aui-page-panel">


                    <div id="content" class="view">
                        <div class="page-metadata">







                Created by <span class='author'> Daniil Kazantsev</span>, last modified by <span class='editor'> Kaz Wanelik</span> on Oct 28, 2019
                            </div>
                        <div id="main-content" class="wiki-content group">
                        <p><br/></p><p><style type='text/css'>/*<![CDATA[*/
    div.rbtoc1592231715518 {padding: 0px;}
    div.rbtoc1592231715518 ul {list-style: disc;margin-left: 0px;}
    div.rbtoc1592231715518 li {margin-left: 0px;padding-left: 0px;}
    .syntaxhighlighter-pre {font-size: small;}
    table {font-size: small;}
    /*]]>*/</style><div class='toc-macro rbtoc1592231715518'>
    <ul class='toc-indentation'>
    <li><a href='#TomobarRecon-Summary'>Summary</a></li>
    <li><a href='#TomobarRecon-Parameters'>Parameters</a>
    <ul class='toc-indentation'>
    <li><a href='#TomobarRecon-Briefdescription'>Brief description</a></li>
    <li><a href='#TomobarRecon-Additionalnotes'>Additional notes</a></li>
    </ul>
    </li>
    <li><a href='#TomobarRecon-Usage'>Usage</a></li>
    </ul>
    </div></p><h2 id="TomobarRecon-Summary"><strong>Summary</strong></h2><p><strong> <br/></strong></p><div class="table-wrap"><table class="wrapped relative-table confluenceTable" style="width: 99.9038%;"><colgroup> <col style="width: 6.6466%;"/> <col style="width: 15.0217%;"/> <col style="width: 15.9851%;"/> <col style="width: 25.9481%;"/> <col style="width: 24.4075%;"/> <col style="width: 11.991%;"/> </colgroup><tbody><tr><td class="highlight-red confluenceTd" colspan="6" data-highlight-colour="red" style="text-align: center;"><strong>TomopyRecon</strong></td></tr><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" style="text-align: center;">Process category</th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow" style="text-align: center;">Brief description</th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow"><p style="text-align: center;">Computational demand</p><p style="text-align: center;">for typical tomography data</p><p style="text-align: center;">(low, medium, high)</p></th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow" style="text-align: center;">Comment(s)</th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow" style="text-align: center;">Reference(s)</th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow" style="text-align: center;">Common alternative process(es)</th></tr><tr><td class="confluenceTd">reconstructor</td><td colspan="1" class="confluenceTd"><p><span class="flex-auto mb-2"><span class="text-gray-dark mr-2">TOmographic MOdel-BAsed Reconstruction (ToMoBAR) software.</span></span></p></td><td colspan="1" class="confluenceTd">medium-high. Note that there is 2D and 3D version of the plugin. 3D is more computationally demanding and doesn't exploit the MPI fully.</td><td colspan="1" class="confluenceTd"><p>ToMoBAR is a library of direct and model-based regularised iterative reconstruction algorithms with a <em>plug-and-play</em> capability. Current Savu wrapper uses the regularised FISTA algorithm</p></td><td colspan="1" class="confluenceTd"><a class="external-link" href="https://www.osapublishing.org/oe/abstract.cfm?URI=oe-22-16-19078" rel="nofollow"></a> <a class="external-link" href="https://github.com/dkazanc/ToMoBAR" rel="nofollow">ToMoBAR</a></td><td colspan="1" class="confluenceTd"><ol><li><strong> <a href="AstraReconCpu_76392346.html">AstraReconCpu</a> </strong></li><li><strong> <a href="AstraReconGpu_76392313.html">AstraReconGpu</a> </strong></li><li><strong>TomoPy</strong></li></ol></td></tr></tbody></table></div><p><br/></p><h2 id="TomobarRecon-Parameters"><strong>Parameters</strong></h2><p><strong> <br/></strong></p><div class="table-wrap"><table class="wrapped confluenceTable"><colgroup> <col/> </colgroup><tbody><tr><th class="highlight-red confluenceTh" data-highlight-colour="red"><h3 id="TomobarRecon-Briefdescription">Brief description</h3></th></tr></tbody></table></div><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b>Savu Configurator command</b></div><div class="codeContent panelContent pdl">
    <pre class="syntaxhighlighter-pre" data-syntaxhighlighter-params="brush: java; gutter: false; theme: Confluence" data-theme="Confluence">&gt;&gt;&gt; disp -avv

    -------------------------------------------------------------------------------------
      TomobarRecon3d(savu.plugins.reconstructions.tomobar_recon_3D)
      A wrapper around TOmographic MOdel-BAsed Reconstruction (ToMoBAR) software for
      advanced iterative image reconstruction using _3D_ capabilities of regularisation.
      The plugin will run on one cluster node, i.e. it can be slow.
        1)               init_vol : None
        Dataset to use as volume initialiser (doesn&#39;t currently work with preview).
        2)                preview : []
        A slice list of required frames.
        3)                    log : True
        Take the log of the data before reconstruction (True or False).
        4)     centre_of_rotation : 0.0
        Centre of rotation to use for the reconstruction.
        5)            in_datasets : []
        Create a list of the dataset(s) to process.
        6)       ring_accelerator : 50.0
        Acceleration constant for ring removal (use with care).
        7)            output_size : auto
        The dimension of the reconstructed volume (only X-Y dimension).
        8)          nonnegativity : ENABLE
        Nonnegativity constraint, choose Enable or None.
        9)         regularisation : ROF_TV
        To regularise choose methods ROF_TV, FGP_TV, SB_TV, LLT_ROF, NDF, Diff4th.
       10)             iterations : 15
        Number of outer iterations for FISTA method.
       11)             edge_param : 0.01
        Edge (noise) related parameter, relevant for NDF and Diff4th.
       12)                  ratio : 0.95
        Ratio of the m2asks diameter in pixels to the smallest edge size along given
        axis.
       13)               log_func : np.nan_to_num(-np.log(sino))
        Override the default log function.
       14)   regularisation_parameter2 : 0.005
        Regularisation (smoothing) value for LLT_ROF method.
       15)            NDF_penalty : Huber
        NDF specific penalty type Huber, Perona, Tukey.
       16)              tolerance : 1e-10
        Tolerance to stop outer iterations earlier.
       17)           ordersubsets : 6
        The number of ordered-subsets to accelerate reconstruction.
       18)           out_datasets : []
        Create a list of the dataset(s) to create.
       19)             centre_pad : False
        Pad the sinogram to centre it in order to fill the reconstructed volume ROI for
        asthetic purposes. NB: Only available for selected algorithms and will be ignored
        otherwise. WARNING: This will significantly increase the size of the data and the
        time to compute the reconstruction).
       20)   regularisation_iterations : 400
        The number of regularisation iterations.
       21)   regularisation_parameter : 0.0002
        Regularisation (smoothing) value, higher the value stronger the smoothing effect.
       22)             force_zero : [None, None]
        Set any values in the reconstructed image outside of this range to zero.
       23)              vol_shape : fixed
        Override the size of the reconstuction volume with an integer value.
       24)          converg_const : power
        Lipschitz constant, can be set to a scalar value or automatic calculation using
        power methods.
       25)   time_marching_parameter : 0.002
        Time marching parameter, relevant for (ROF_TV, LLT_ROF, NDF, Diff4th) penalties.
       26)           datafidelity : LS
        Data fidelity, Least Squares (LS) or PWLS.
       27)              outer_pad : False
        Pad the sinogram width to fill the reconstructed volume for asthetic purposes.
        Choose from True (defaults to sqrt(2)), False or float &lt;= 2.1. NB: Only available
        for selected algorithms and will be ignored otherwise. WARNING: This will
        increase the size of the data and the time to compute the reconstruction).
       28)          ring_variable : 0.0
        Regularisation variable for ring removal.

    -------------------------------------------------------------------------------------
    &gt;&gt;&gt; </pre>
    </div></div><div class="table-wrap"><table class="wrapped confluenceTable"><colgroup><col/></colgroup><tbody><tr><th class="highlight-red confluenceTh" data-highlight-colour="red"><h3 id="TomobarRecon-Additionalnotes">Additional notes</h3></th></tr></tbody></table></div><p>For basic information on this process, please use the <em><strong>disp -av </strong></em>(or <em><strong>disp -avv </strong></em>or <em><strong>disp</strong></em><strong> </strong><strong>-v</strong>[<strong>v</strong>] <strong>&lt;</strong><em>process index</em><strong>&gt;</strong>) command in <strong>Savu Configurator </strong>(see above). The table below is intended to provide some additional notes on a number of selected topics:</p><div class="table-wrap"><table class="relative-table wrapped confluenceTable" style="width: 99.9366%;"><colgroup> <col style="width: 3.13956%;"/> <col style="width: 12.7838%;"/> <col style="width: 17.5%;"/> <col style="width: 10.0021%;"/> <col style="width: 24.4166%;"/> <col style="width: 32.1262%;"/> </colgroup><tbody><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" rowspan="2" style="text-align: center;">Item</th><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" rowspan="2" style="text-align: center;">Parameter name</th><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" rowspan="2" style="text-align: center;">Parameter format</th><th class="highlight-yellow confluenceTh" colspan="2" data-highlight-colour="yellow" style="text-align: center;">Example(s)</th><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" rowspan="2" style="text-align: center;">Comment(s)</th></tr><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" style="text-align: center;">Parameter value</th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow" style="text-align: center;">Effect</th></tr><tr><td colspan="1" class="confluenceTd">1</td><td colspan="1" class="confluenceTd"><p><em> regularisation_parameter<br/></em></p></td><td colspan="1" style="text-align: center;" class="confluenceTd">float</td><td colspan="1" style="text-align: center;" class="confluenceTd">0.0002</td><td colspan="1" class="confluenceTd">Should be chosen for a specific dataset. Higher the value stronger the smoothing effect.</td><td colspan="1" class="confluenceTd">The value depends on the data. If zero is passed, no regularisation will be applied (reconstruction without filtering).</td></tr><tr><td colspan="1" class="confluenceTd">2</td><td colspan="1" class="confluenceTd"><p><em> regularisation<br/></em></p></td><td colspan="1" style="text-align: center;" class="confluenceTd">string</td><td colspan="1" class="confluenceTd">ROF_TV, FGP_TV, SB_TV, LLT_ROF, NDF, Diff4th, TGV</td><td colspan="1" class="confluenceTd"><p>ROF_TV, FGP_TV, SB_TV, NDF - deliver piecewise-constant recovery (regions with uniform intensity)</p><p>LLT_ROF, Diff4th, TGV - piecewise-smooth recovery.</p></td><td colspan="1" class="confluenceTd"><p>The plugin uses the CCPi-Regularisation toolkit which is available here:</p><p><a class="external-link" href="https://github.com/vais-ral/CCPi-Regularisation-Toolkit" rel="nofollow">https://github.com/vais-ral/CCPi-Regularisation-Toolkit</a></p><p>and based on this paper:</p><p><a class="external-link" href="https://www.sciencedirect.com/science/article/pii/S2352711018301912" rel="nofollow">https://www.sciencedirect.com/science/article/pii/S2352711018301912</a></p></td></tr><tr><td colspan="1" class="confluenceTd">3</td><td colspan="1" class="confluenceTd"><p><em><em>iterations</em> </em></p></td><td colspan="1" style="text-align: center;" class="confluenceTd">integer</td><td colspan="1" style="text-align: center;" class="confluenceTd">15-20</td><td colspan="1" class="confluenceTd">Less than 10 iterations for the iterative method (FISTA) can deliver a blurry reconstruction</td><td colspan="1" class="confluenceTd">The suggested value is 15 iterations, however the algorithm can stop prematurely based on the tolerance value (see bellow)</td></tr><tr><td colspan="1" class="confluenceTd">4</td><td colspan="1" class="confluenceTd"><em> tolerance</em></td><td colspan="1" style="text-align: center;" class="confluenceTd">float</td><td colspan="1" style="text-align: center;" class="confluenceTd">1e-10</td><td colspan="1" class="confluenceTd">can stop iterations prematurely when the solution is changing &quot;slowly&quot;</td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">5</td><td colspan="1" class="confluenceTd"><em>regularisation_iterations</em></td><td colspan="1" style="text-align: center;" class="confluenceTd">integer</td><td colspan="1" class="confluenceTd"><p>400 for OS methods,</p><p>70 for non-OS</p></td><td colspan="1" class="confluenceTd">Less iterations - less effect of filtering.</td><td colspan="1" class="confluenceTd">One needs to iterate &quot;long enough&quot; in order to get to the filtered solution. The number of iterations for regularisation (filtering) method is set to 400/OS number or 400 for non-OS method. It is not harmful to over-iterate, this, however will effect the speed of the algorithm.</td></tr><tr><td colspan="1" class="confluenceTd">6</td><td colspan="1" class="confluenceTd"><p><em>centre_of_rotation</em></p></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd">The default value of the <strong> <em>centre_of_rotation</em> </strong> parameter is <span style="color: rgb(128,0,0);">0.0</span>, which normally needs to be manually modified to a more appropriate value or, if <strong> <a href="VoCentering_76392254.html">VoCentering</a> </strong> is used beforehand in the process chain, then this parameter is automatically set to a value determined by this auto-centring process.</td></tr><tr><td colspan="1" class="confluenceTd">7</td><td colspan="1" class="confluenceTd"><p><em> ordersubsets<br/></em></p></td><td colspan="1" style="text-align: center;" class="confluenceTd"> integer</td><td colspan="1" style="text-align: center;" class="confluenceTd">6</td><td colspan="1" class="confluenceTd">effects the final solution by accelerating reconstruction process.</td><td colspan="1" class="confluenceTd">This directly effect the number of iterations to run. The high value (&gt; 12), however, can result in the algorithm to diverge.</td></tr><tr><td colspan="1" class="confluenceTd">8</td><td colspan="1" class="confluenceTd"><em> <em>ratio</em> </em></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">9</td><td colspan="1" class="confluenceTd"><em> <em>out_datasets</em> </em></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">10</td><td colspan="1" class="confluenceTd"><p><em> <em> <em> <em>centre_pad</em> </em> </em> <br/></em></p></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">11</td><td colspan="1" class="confluenceTd"><em> <em>outer_pad</em> </em></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">12</td><td colspan="1" class="confluenceTd"><p><em>n_iterations<br/></em></p></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">13</td><td colspan="1" class="confluenceTd"><em> <em>force_zero</em> </em></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr></tbody></table></div><p><br/></p><p><br/></p><h2 id="TomobarRecon-Usage"><strong>Usage<br/></strong></h2><p>There are 2D versions of the tomobar plugin - for 2D and 3D reconstruction. 2D version is fully MPI-ed while 3D work on a single GPU provided. Although 3D version can be significantly slower than 2D, the results are normally much better using 3D versus slice-by-slice 2D. Note, however, the passed data dimensions and the available GPU memory before running tomobar3D, the memory overflow can be easily reached. </p><p><br/></p><p><strong> <br/></strong></p><p><strong> <br/></strong></p>
                        </div>



                    </div>             </div>
                <div id="footer" role="contentinfo">
                    <section class="footer-body">
                        <p>Document generated by Confluence on Jun 15, 2020 15:35</p>
                        <div id="footer-logo"><a href="http://www.atlassian.com/">Atlassian</a></div>
                    </section>
                </div>
            </div>     </body>
    </html>
