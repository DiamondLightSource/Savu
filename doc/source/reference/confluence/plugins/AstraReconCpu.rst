AstraReconCpu
-----------------------------

.. raw:: html

    <!DOCTYPE html>
    <html>
        <head>
            <title>Tomography Reconstruction : AstraReconCpu</title>
            <link rel="stylesheet" href="styles/site.css" type="text/css" />
            <META http-equiv="Content-Type" content="text/html; charset=UTF-8">
        </head>

        <body class="theme-default aui-theme-default">
            <div id="page">
                <div id="main" class="aui-page-panel">
                    <div id="main-header">

                    </div>

                    <div id="content" class="view">
                        <div class="page-metadata">







                Created by <span class='author'> Kaz Wanelik</span>, last modified on Oct 28, 2019
                            </div>
                        <div id="main-content" class="wiki-content group">
                        <p><br/></p><p><style type='text/css'>/*<![CDATA[*/
    div.rbtoc1592231714887 {padding: 0px;}
    div.rbtoc1592231714887 ul {list-style: disc;margin-left: 0px;}
    div.rbtoc1592231714887 li {margin-left: 0px;padding-left: 0px;}
    .syntaxhighlighter-pre {font-size: small;}
    table {font-size: small;}

    /*]]>*/</style><div class='toc-macro rbtoc1592231714887'>
    <ul class='toc-indentation'>
    <li><a href='#AstraReconCpu-Summary'>Summary</a></li>
    <li><a href='#AstraReconCpu-Parameters'>Parameters</a>
    <ul class='toc-indentation'>
    <li><a href='#AstraReconCpu-Briefdescription'>Brief description</a></li>
    <li><a href='#AstraReconCpu-Additionalnotes'>Additional notes</a></li>
    </ul>
    </li>
    <li><a href='#AstraReconCpu-Usage'>Usage</a></li>
    </ul>
    </div></p><h2 id="AstraReconCpu-Summary"><strong>Summary</strong></h2><p><strong><br/></strong></p><div class="table-wrap"><table class="wrapped relative-table confluenceTable" style="width: 99.9519%;"><colgroup><col style="width: 6.49896%;"/><col style="width: 20.2584%;"/><col style="width: 13.7161%;"/><col style="width: 26.1764%;"/><col style="width: 25.3105%;"/><col style="width: 8.03964%;"/></colgroup><tbody><tr><td class="highlight-red confluenceTd" colspan="6" data-highlight-colour="red" style="text-align: center;"><strong>AstraReconCpu</strong></td></tr><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" style="text-align: center;">Process category</th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow" style="text-align: center;">Brief description</th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow"><p style="text-align: center;">Computational demand</p><p style="text-align: center;">for typical tomography data</p><p style="text-align: center;">(low, medium, high)</p></th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow" style="text-align: center;">Comment(s)</th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow" style="text-align: center;">Reference(s)</th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow" style="text-align: center;">Common alternative process(es)</th></tr><tr><td class="confluenceTd">reconstructor</td><td colspan="1" class="confluenceTd"><p>To reconstruct normalised and conditioned data.</p></td><td colspan="1" class="confluenceTd">Depends on the reconstruction algorithm selected.</td><td colspan="1" class="confluenceTd">Uses CPU resources.</td><td colspan="1" class="confluenceTd"><a class="external-link" href="http://www.astra-toolbox.com/" rel="nofollow">The Astra Toolbox</a></td><td colspan="1" class="confluenceTd"><ol><li><strong><a href="AstraReconGpu_76392313.html">AstraReconGpu</a></strong></li><li><strong><a href="TomopyRecon_76392350.html">TomopyRecon</a></strong></li></ol></td></tr></tbody></table></div><p><br/></p><h2 id="AstraReconCpu-Parameters"><strong>Parameters</strong></h2><p><strong><br/></strong></p><div class="table-wrap"><table class="wrapped confluenceTable"><colgroup><col/></colgroup><tbody><tr><th class="highlight-red confluenceTh" data-highlight-colour="red"><h3 id="AstraReconCpu-Briefdescription">Brief description</h3></th></tr></tbody></table></div><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b>Savu Configurator command</b></div><div class="codeContent panelContent pdl">
    <pre class="syntaxhighlighter-pre" data-syntaxhighlighter-params="brush: java; gutter: false; theme: Confluence" data-theme="Confluence">&gt;&gt;&gt; disp -avv

    -------------------------------------------------------------------------------------
     2) AstraReconCpu(savu.plugins.reconstructions.astra_recons.astra_recon_cpu)
      Wrapper around the Astra toolbox for cpu reconstruction.
        1)               init_vol : None
        Dataset to use as volume initialiser (doesn&#39;t currently work with preview).
        2)                    log : True
        Take the log of the data before reconstruction (True or False).
        3)              algorithm : FBP
        Reconstruction type (FBP|SIRT|SART|ART|CGLS|FP|BP|).
        4)           n_iterations : 1
        Number of Iterations - only valid for iterative algorithms.
        5)                preview : []
        A slice list of required frames.
        6)     centre_of_rotation : 0.0
        Centre of rotation to use for the reconstruction.
        7)            in_datasets : []
        Create a list of the dataset(s) to process.
        8)                  ratio : 0.95
        Ratio of the masks diameter in pixels to the smallest edge size along given axis.
        9)           out_datasets : []
        Create a list of the dataset(s) to create.
       10)             centre_pad : False
        Pad the sinogram to centre it in order to fill the reconstructed volume ROI for
        asthetic purposes. NB: Only available for selected algorithms and will be ignored
        otherwise. WARNING: This will significantly increase the size of the data and the
        time to compute the reconstruction).
       11)              outer_pad : False
        Pad the sinogram width to fill the reconstructed volume for asthetic purposes.
        Choose from True (defaults to sqrt(2)), False or float &lt;= 2.1. NB: Only available
        for selected algorithms and will be ignored otherwise. WARNING: This will
        increase the size of the data and the time to compute the reconstruction).
       12)               log_func : np.nan_to_num(-np.log(sino))
        Override the default log function.
       13)             force_zero : [None, None]
        Set any values in the reconstructed image outside of this range to zero.
       14)              projector : line
        Set astra projector (line|strip|linear).
    -------------------------------------------------------------------------------------

    &gt;&gt;&gt; </pre>
    </div></div><div class="table-wrap"><table class="wrapped confluenceTable"><colgroup><col/></colgroup><tbody><tr><th class="highlight-red confluenceTh" data-highlight-colour="red"><h3 id="AstraReconCpu-Additionalnotes">Additional notes</h3></th></tr></tbody></table></div><p>For basic information on this process, please use the <em><strong>disp -av </strong></em>(or <em><strong>disp -avv </strong></em>or <em><strong>disp</strong></em><strong> </strong><strong>-v</strong>[<strong>v</strong>] <strong>&lt;</strong><em>process index</em><strong>&gt;</strong>) command in <strong>Savu Configurator </strong>(see above). The table below is intended to provide some additional notes on a number of selected topics:</p><div class="table-wrap"><table class="relative-table wrapped confluenceTable" style="width: 99.9366%;"><colgroup><col style="width: 3.13956%;"/><col style="width: 12.7838%;"/><col style="width: 17.5%;"/><col style="width: 10.0021%;"/><col style="width: 24.4166%;"/><col style="width: 32.1262%;"/></colgroup><tbody><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" rowspan="2" style="text-align: center;">Item</th><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" rowspan="2" style="text-align: center;">Parameter name</th><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" rowspan="2" style="text-align: center;">Parameter format</th><th class="highlight-yellow confluenceTh" colspan="2" data-highlight-colour="yellow" style="text-align: center;">Example(s)</th><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" rowspan="2" style="text-align: center;">Comment(s)</th></tr><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" style="text-align: center;">Parameter value</th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow" style="text-align: center;">Effect</th></tr><tr><td colspan="1" class="confluenceTd">1</td><td colspan="1" class="confluenceTd"><p><em><em>init_vol</em><br/></em></p></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">2</td><td colspan="1" class="confluenceTd"><p><em><em>log<br/></em></em></p></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd">The <strong><em>log</em></strong><em> </em>parameter needs to be set to <span style="color: rgb(128,0,0);">False</span>, if <strong><a href="PaganinFilter_76392338.html">PaganinFilter</a></strong> is applied beforehand.</td></tr><tr><td colspan="1" class="confluenceTd">3</td><td colspan="1" class="confluenceTd"><em><em><em>algorithm</em></em></em></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">4</td><td colspan="1" class="confluenceTd"><em><em><em>n_iterations</em></em></em></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">5</td><td colspan="1" class="confluenceTd"><em><em><em>preview</em></em></em></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">6</td><td colspan="1" class="confluenceTd"><p><em>centre_of_rotation</em></p></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd">The default value of the <strong><em>centre_of_rotation</em></strong> parameter is <span style="color: rgb(128,0,0);">0.0</span>, which normally needs to be manually modified  to a more appropriate value or, if <strong><a href="VoCentering_76392254.html">VoCentering</a></strong> is used beforehand in the process chain, then this parameter is automatically set to a value determined by this auto-centring process.</td></tr><tr><td colspan="1" class="confluenceTd">7</td><td colspan="1" class="confluenceTd"><p><em><em>in_datasets</em></em></p></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">8</td><td colspan="1" class="confluenceTd"><em><em>ratio</em></em></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">19</td><td colspan="1" class="confluenceTd"><em><em>out_datasets</em></em></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">10</td><td colspan="1" class="confluenceTd"><p><em><em><em><em>centre_pad</em></em></em><br/></em></p></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">11</td><td colspan="1" class="confluenceTd"><em><em>outer_pad</em></em></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">12</td><td colspan="1" class="confluenceTd"><em><em>force_zero</em></em></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">13</td><td colspan="1" class="confluenceTd"><em><em>projector</em></em></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr></tbody></table></div><p><br/></p><p><br/></p><h2 id="AstraReconCpu-Usage"><strong>Usage<br/></strong></h2><p>TBC.</p><p><br/></p><p><strong><br/></strong></p><p><strong><br/></strong></p>
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
