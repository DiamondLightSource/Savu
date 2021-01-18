TomopyRecon
-----------------------------

.. raw:: html

    <!DOCTYPE html>
    <html>
        <head>
            <title>Tomography Reconstruction : TomopyRecon</title>
            <link rel="stylesheet" href="styles/site.css" type="text/css" />
            <META http-equiv="Content-Type" content="text/html; charset=UTF-8">
        </head>

        <body class="theme-default aui-theme-default">
            <div id="page">
                <div id="main" class="aui-page-panel">


                    <div id="content" class="view">
                        <div class="page-metadata">







                Created by <span class='author'> Kaz Wanelik</span>, last modified on Oct 28, 2019
                            </div>
                        <div id="main-content" class="wiki-content group">
                        <p><br/></p><p><style type='text/css'>/*<![CDATA[*/
    div.rbtoc1592231715567 {padding: 0px;}
    div.rbtoc1592231715567 ul {list-style: disc;margin-left: 0px;}
    div.rbtoc1592231715567 li {margin-left: 0px;padding-left: 0px;}
    .syntaxhighlighter-pre {font-size: small;}
    table {font-size: small;}
    /*]]>*/</style><div class='toc-macro rbtoc1592231715567'>
    <ul class='toc-indentation'>
    <li><a href='#TomopyRecon-Summary'>Summary</a></li>
    <li><a href='#TomopyRecon-Parameters'>Parameters</a>
    <ul class='toc-indentation'>
    <li><a href='#TomopyRecon-Briefdescription'>Brief description</a></li>
    <li><a href='#TomopyRecon-Additionalnotes'>Additional notes</a></li>
    </ul>
    </li>
    <li><a href='#TomopyRecon-Usage'>Usage</a></li>
    </ul>
    </div></p><h2 id="TomopyRecon-Summary"><strong>Summary</strong></h2><p><strong><br/></strong></p><div class="table-wrap"><table class="wrapped relative-table confluenceTable" style="width: 99.9038%;"><colgroup><col style="width: 6.6466%;"/><col style="width: 15.0217%;"/><col style="width: 15.9851%;"/><col style="width: 25.9481%;"/><col style="width: 24.4075%;"/><col style="width: 11.991%;"/></colgroup><tbody><tr><td class="highlight-red confluenceTd" colspan="6" data-highlight-colour="red" style="text-align: center;"><strong>TomopyRecon</strong></td></tr><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" style="text-align: center;">Process category</th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow" style="text-align: center;">Brief description</th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow"><p style="text-align: center;">Computational demand</p><p style="text-align: center;">for typical tomography data</p><p style="text-align: center;">(low, medium, high)</p></th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow" style="text-align: center;">Comment(s)</th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow" style="text-align: center;">Reference(s)</th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow" style="text-align: center;">Common alternative process(es)</th></tr><tr><td class="confluenceTd">reconstructor</td><td colspan="1" class="confluenceTd"><p>To reconstruct normalised and conditioned data.</p></td><td colspan="1" class="confluenceTd">Depends on the reconstruction algorithm selected.</td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><a class="external-link" href="https://www.osapublishing.org/oe/abstract.cfm?URI=oe-22-16-19078" rel="nofollow"> </a><a class="external-link" href="https://tomopy.readthedocs.io/en/latest/" rel="nofollow"> TomoPy</a></td><td colspan="1" class="confluenceTd"><ol><li><strong><a href="AstraReconCpu_76392346.html">AstraReconCpu</a></strong></li><li><strong><a href="AstraReconGpu_76392313.html">AstraReconGpu</a></strong></li></ol></td></tr></tbody></table></div><p><br/></p><h2 id="TomopyRecon-Parameters"><strong>Parameters</strong></h2><p><strong><br/></strong></p><div class="table-wrap"><table class="wrapped confluenceTable"><colgroup><col/></colgroup><tbody><tr><th class="highlight-red confluenceTh" data-highlight-colour="red"><h3 id="TomopyRecon-Briefdescription">Brief description</h3></th></tr></tbody></table></div><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b>Savu Configurator command</b></div><div class="codeContent panelContent pdl">
    <pre class="syntaxhighlighter-pre" data-syntaxhighlighter-params="brush: java; gutter: false; theme: Confluence" data-theme="Confluence">&gt;&gt;&gt; disp -avv

    -------------------------------------------------------------------------------------
     2) TomopyRecon(savu.plugins.reconstructions.tomopy_recon)
      Wrapper around the tomopy reconstruction algorithms. See
      &#39;http://tomopy.readthedocs.io/en/latest/api/tomopy.recon.algorithm.html&#39;.
        1)                reg_par : 0.0
        Regularization parameter for smoothing, valid for
        ospml_hybrid|ospml_quad|pml_hybrid|pml_quad.
        2)                    log : True
        Take the log of the data before reconstruction (True or False).
        3)              algorithm : gridrec
        The reconstruction algorithm (art|bart|fbp|gridrec|
        mlem|osem|ospml_hybrid|ospml_quad|pml_hybrid|pml_quad |sirt).
        4)            filter_name : None
        Valid for fbp|gridrec, options: none|shepp|cosine|
        hann|hamming|ramlak|parzen|butterworth).
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
       10)              outer_pad : False
        Pad the sinogram width to fill the reconstructed volume for asthetic purposes.
        Choose from True (defaults to sqrt(2)), False or float &lt;= 2.1. NB: Only available
        for selected algorithms and will be ignored otherwise. WARNING: This will
        increase the size of the data and the time to compute the reconstruction).
       11)               log_func : np.nan_to_num(-np.log(sino))
        Override the default log function.
       12)           n_iterations : 1
        Number of iterations - only valid for iterative algorithms.
       13)             force_zero : [None, None]
        Set any values in the reconstructed image outside of this range to zero.
    -------------------------------------------------------------------------------------

    &gt;&gt;&gt; </pre>
    </div></div><div class="table-wrap"><table class="wrapped confluenceTable"><tbody><tr><th class="highlight-red confluenceTh" data-highlight-colour="red"><h3 id="TomopyRecon-Additionalnotes">Additional notes</h3></th></tr></tbody></table></div><p>For basic information on this process, please use the <em><strong>disp -av </strong></em>(or <em><strong>disp -avv </strong></em>or <em><strong>disp</strong></em><strong> </strong><strong>-v</strong>[<strong>v</strong>] <strong>&lt;</strong><em>process index</em><strong>&gt;</strong>) command in <strong>Savu Configurator </strong>(see above). The table below is intended to provide some additional notes on a number of selected topics:</p><div class="table-wrap"><table class="relative-table wrapped confluenceTable" style="width: 99.9366%;"><colgroup><col style="width: 3.13956%;"/><col style="width: 12.7838%;"/><col style="width: 17.5%;"/><col style="width: 10.0021%;"/><col style="width: 24.4166%;"/><col style="width: 32.1262%;"/></colgroup><tbody><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" rowspan="2" style="text-align: center;">Item</th><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" rowspan="2" style="text-align: center;">Parameter name</th><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" rowspan="2" style="text-align: center;">Parameter format</th><th class="highlight-yellow confluenceTh" colspan="2" data-highlight-colour="yellow" style="text-align: center;">Example(s)</th><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" rowspan="2" style="text-align: center;">Comment(s)</th></tr><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" style="text-align: center;">Parameter value</th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow" style="text-align: center;">Effect</th></tr><tr><td colspan="1" class="confluenceTd">1</td><td colspan="1" class="confluenceTd"><p><em><em>reg_par</em><br/></em></p></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">2</td><td colspan="1" class="confluenceTd"><p><em><em><em>log</em></em><br/></em></p></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd">The <strong><em>log</em></strong><em> </em>parameter needs to be set to <span style="color: rgb(128,0,0);">False</span>, if <a href="https://confluence.diamond.ac.uk/display/TOMTE/PaganinFilter" rel="nofollow">PaganinFilter</a> is applied beforehand.</td></tr><tr><td colspan="1" class="confluenceTd">3</td><td colspan="1" class="confluenceTd"><p><em><em>algorithm<br/></em></em></p></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">4</td><td colspan="1" class="confluenceTd"><em><em><em>filter_name</em></em></em></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">5</td><td colspan="1" class="confluenceTd"><em>preview</em></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">6</td><td colspan="1" class="confluenceTd"><p><em>centre_of_rotation</em></p></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd">The default value of the <strong><em>centre_of_rotation</em></strong> parameter is <span style="color: rgb(128,0,0);">0.0</span>, which normally needs to be manually modified to a more appropriate value or, if <strong><a href="VoCentering_76392254.html">VoCentering</a></strong> is used beforehand in the process chain, then this parameter is automatically set to a value determined by this auto-centring process.</td></tr><tr><td colspan="1" class="confluenceTd">7</td><td colspan="1" class="confluenceTd"><p><em><em>in_datasets</em></em></p></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">8</td><td colspan="1" class="confluenceTd"><em><em>ratio</em></em></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">9</td><td colspan="1" class="confluenceTd"><em><em>out_datasets</em></em></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">10</td><td colspan="1" class="confluenceTd"><p><em><em><em><em>centre_pad</em></em></em><br/></em></p></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">11</td><td colspan="1" class="confluenceTd"><em><em>outer_pad</em></em></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">12</td><td colspan="1" class="confluenceTd"><p><em>n_iterations<br/></em></p></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">13</td><td colspan="1" class="confluenceTd"><em><em>force_zero</em></em></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr></tbody></table></div><p><br/></p><p><br/></p><h2 id="TomopyRecon-Usage"><strong>Usage<br/></strong></h2><p>TBC.</p><p><br/></p><p><strong><br/></strong></p><p><strong><br/></strong></p>
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
