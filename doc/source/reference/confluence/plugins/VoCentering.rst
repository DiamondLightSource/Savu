VoCentering
-----------

.. raw:: html

    <!DOCTYPE html>
    <html>
        <head>
            <title>Tomography Reconstruction : VoCentering</title>
            <link rel="stylesheet" href="styles/site.css" type="text/css" />
            <META http-equiv="Content-Type" content="text/html; charset=UTF-8">
        </head>

        <body class="theme-default aui-theme-default">
            <div id="page">
                <div id="main" class="aui-page-panel">


                    <div id="content" class="view">
                        <div class="page-metadata">







                Created by <span class='author'> Kaz Wanelik</span>, last modified on Dec 01, 2019
                            </div>
                        <div id="main-content" class="wiki-content group">
                        <p><br/></p><p><style type='text/css'>/*<![CDATA[*/
    div.rbtoc1592231715607 {padding: 0px;}
    div.rbtoc1592231715607 ul {list-style: disc;margin-left: 0px;}
    div.rbtoc1592231715607 li {margin-left: 0px;padding-left: 0px;}
    .syntaxhighlighter-pre {font-size: small;}
    table {font-size: small;}
    /*]]>*/</style><div class='toc-macro rbtoc1592231715607'>
    <ul class='toc-indentation'>
    <li><a href='#VoCentering-Summary'>Summary</a></li>
    <li><a href='#VoCentering-Parameters'>Parameters</a>
    <ul class='toc-indentation'>
    <li><a href='#VoCentering-Briefdescription'>Brief description</a></li>
    <li><a href='#VoCentering-Additionalnotes'>Additional notes</a></li>
    </ul>
    </li>
    <li><a href='#VoCentering-Usage'>Usage</a></li>
    </ul>
    </div></p><h2 id="VoCentering-Summary"><strong>Summary</strong></h2><p><strong><br/></strong></p><div class="table-wrap"><table class="wrapped relative-table confluenceTable" style="width: 99.9519%;"><colgroup><col style="width: 6.59204%;"/><col style="width: 14.3829%;"/><col style="width: 9.96068%;"/><col style="width: 15.6805%;"/><col style="width: 42.3632%;"/><col style="width: 11.0207%;"/></colgroup><tbody><tr><td class="highlight-red confluenceTd" colspan="6" data-highlight-colour="red" style="text-align: center;"><strong>VoCentering</strong></td></tr><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" style="text-align: center;">Process category</th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow" style="text-align: center;">Brief description</th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow"><p style="text-align: center;">Computational demand</p><p style="text-align: center;">for typical tomography data</p><p style="text-align: center;">(low, medium, high)</p></th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow" style="text-align: center;">Comment(s)</th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow" style="text-align: center;">Reference(s)</th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow" style="text-align: center;">Common alternative process(es)</th></tr><tr><td class="confluenceTd">filter</td><td colspan="1" class="confluenceTd"><p>To find an optimal value of <em>CoR</em> automatically.</p></td><td colspan="1" class="confluenceTd"><span style="color: rgb(255,0,0);">High</span></td><td colspan="1" class="confluenceTd"><ol><li>Since the computational cost of this auto-centring process is <span style="color: rgb(255,0,0);">high</span>, it is normally applied to a small but representative subset of data (this can most conveniently be done with the aid of the <strong><em>preview</em></strong> parameter of this process).</li><li>Any reconstructor process included in a process chain after<strong> VoCentering</strong> will have its <em><strong>centre_of_rotation</strong></em> parameter automatically set to the value determined by the auto-centring process.</li><li><strong>VoCentering </strong>should normally be included after a ring-artefact suppression process (such as, e.g. <strong>RemoveAllRings</strong>), but before any low-pass process such as <strong><a href="https://confluence.diamond.ac.uk/display/TOMTE/PaganinFilter" rel="nofollow">PaganinFilter</a></strong> or <strong>FresnelFilter</strong>. </li></ol></td><td colspan="1" class="confluenceTd"><a class="external-link" href="https://www.osapublishing.org/oe/abstract.cfm?URI=oe-22-16-19078" rel="nofollow">Reliable method for calculating the center of rotation in parallel-beam tomography </a></td><td colspan="1" class="confluenceTd"><strong>VoCenteringIterative</strong></td></tr></tbody></table></div><p><br/></p><h2 id="VoCentering-Parameters"><strong>Parameters</strong></h2><p><strong><br/></strong></p><div class="table-wrap"><table class="wrapped confluenceTable"><tbody><tr><th class="highlight-red confluenceTh" data-highlight-colour="red"><h3 id="VoCentering-Briefdescription">Brief description</h3></th></tr></tbody></table></div><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b>Savu Configurator command</b></div><div class="codeContent panelContent pdl">
    <pre class="syntaxhighlighter-pre" data-syntaxhighlighter-params="brush: java; gutter: false; theme: Confluence" data-theme="Confluence">&gt;&gt;&gt; disp -avv

    -------------------------------------------------------------------------------------
     1) VoCentering(savu.plugins.centering.vo_centering)
      A plugin to find the center of rotation per frame
        1)                preview : []
        A slice list of required frames (sinograms) to use in the calulation of the
        centre of rotation (this will not reduce the data size for subsequent plugins).
        2)            start_pixel : None
        The approximate centre. If value is None, take the value from .nxs file else set
        to image centre.
        3)            search_area : (-50, 50)
        Search area from horizontal approximate centre of the image.
        4)            in_datasets : []
        Create a list of the dataset(s) to process.
        5)          search_radius : 6
        Use for fine searching.
        6)                  ratio : 0.5
        The ratio between the size of object and FOV of the camera.
        7)           out_datasets : [&#39;cor_raw&#39;, &#39;cor_fit&#39;]
        The default names.
        8)   datasets_to_populate : []
        A list of datasets which require this information.
        9)               row_drop : 20
        Drop lines around vertical center of the mask.
       10)                   step : 0.5
        Step of fine searching.
    -------------------------------------------------------------------------------------

    &gt;&gt;&gt; </pre>
    </div></div><div class="table-wrap"><table class="wrapped confluenceTable"><tbody><tr><th class="highlight-red confluenceTh" data-highlight-colour="red"><h3 id="VoCentering-Additionalnotes">Additional notes</h3></th></tr></tbody></table></div><p>For basic information on this process, please use the <em><strong>disp -av </strong></em>(or <em><strong>disp -avv </strong></em>or <em><strong>disp</strong></em><strong> </strong><strong>-v</strong>[<strong>v</strong>] <strong>&lt;</strong><em>process index</em><strong>&gt;</strong>) command in <strong>Savu Configurator </strong>(see above). The table below is intended to provide some additional notes on a number of selected topics:</p><div class="table-wrap"><table class="relative-table wrapped confluenceTable" style="width: 99.9366%;"><colgroup><col style="width: 3.13956%;"/><col style="width: 12.7637%;"/><col style="width: 17.3846%;"/><col style="width: 9.96612%;"/><col style="width: 19.2207%;"/><col style="width: 37.4936%;"/></colgroup><tbody><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" rowspan="2" style="text-align: center;">Item</th><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" rowspan="2" style="text-align: center;">Parameter name</th><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" rowspan="2" style="text-align: center;">Parameter format</th><th class="highlight-yellow confluenceTh" colspan="2" data-highlight-colour="yellow" style="text-align: center;">Example(s)</th><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" rowspan="2" style="text-align: center;">Comment(s)</th></tr><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" style="text-align: center;">Parameter value</th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow" style="text-align: center;">Effect</th></tr><tr><td colspan="1" class="confluenceTd">1</td><td colspan="1" class="confluenceTd"><p><em><em>preview</em><br/></em></p></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><ol><li>Note that the <strong><em>preview</em></strong> parameter has a nested-cumulative behaviour, i. e. if one specifies <strong>VoCentering</strong>'s <strong><em>preview</em></strong> parameter together with <strong>NxtomoLoader</strong>'s <strong><em>preview</em></strong> parameter, then <strong>VoCentering</strong> will effectively be selecting a subset from <strong>NxtomoLoader</strong>'s own subset (rather than the entire dataset). Note also that <strong>VoCentering</strong>'s subset needs to be specified by indices referring to <strong>NxtomoLoader</strong>'s own subset (rather than the entire dataset). For instance, one must set<strong> VoCentering</strong>'s <strong><em>preview</em></strong> parameter to [:, <span style="color: rgb(128,0,0);">0</span>, :] in order to select the initial slice of any dataset previously loaded by <strong>NxtomoLoader</strong>, which may, for example, be the [:, <span style="color: rgb(128,0,0);">123</span>:<span style="color: rgb(128,0,0);">456</span>, :] subset of (<span style="color: rgb(128,0,0);">456</span>-<span style="color: rgb(128,0,0);">123</span>=<span style="color: rgb(128,0,0);">333</span> slices of) the entire dataset<strong><em>.</em></strong></li><li>If you use any parameter tuning in one (or more) process(es) preceding <strong>VoCentering</strong>, then the latter will automatically receive (from the immediately preceding process) a dataset of order higher than 3. In this case, if you leave <strong>VoCentering</strong>'s <strong><em>preview</em></strong> parameter at its default value (i.e. [ ]), then <strong>VoCentering</strong> will have too process the entire rank-N (N&gt;3) dataset, which is hardly ever desired. To avoid this waste of resources, you should specify <strong>VoCentering</strong>'s <strong><em>preview</em></strong> parameter to be a desired, reasonably-sized rank-3 slice of the incoming rank-N dataset. For instance, if you have generated a dataset of shape (<span style="color: rgb(255,102,0);"><em>D</em></span>, <span style="color: rgb(255,102,0);"><em>img_W</em></span>, <em><span style="color: rgb(255,102,0);">img_</span><span style="color: rgb(255,102,0);">L</span></em>,<em><span style="color: rgb(255,102,0);"> T</span>)</em> by subjecting the original (<span style="color: rgb(255,102,0);"><em>D</em></span>, <span style="color: rgb(255,102,0);"><em>img_W</em></span>, <em><span style="color: rgb(255,102,0);">img_</span><span style="color: rgb(255,102,0);">L</span></em>) data to a single parameter-tuning operation, then your new, parameter-tuned rank-4 dataset needs to be sliced in the <span style="color: rgb(0,0,0);">last </span>dimension (corresponding to<em> <span style="color: rgb(255,102,0);">T</span></em>), e. g. one can use the [:, <em>mid,</em> :, <span style="color: rgb(128,0,0);">0</span>] slice of this rank-4 dataset to select its rank-3 subset containing the middle <em>sinogram</em> that was created with the <span style="color: rgb(0,0,0);">initial value of the tuning parameter.    </span></li></ol></td></tr><tr><td colspan="1" class="confluenceTd">2</td><td colspan="1" class="confluenceTd"><p><em>start_pixel<br/></em></p></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd">An initial estimate for the pixel coordinate of an optimal <em>CoR.</em></td></tr><tr><td colspan="1" class="confluenceTd">3</td><td colspan="1" class="confluenceTd"><p><em><em>search_area<br/></em></em></p></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd">If the value of the <strong><em><em>search_area</em></em></strong> parameter is set to the default interval of (-<span style="color: rgb(128,0,0);">50</span>, <span style="color: rgb(128,0,0);">50</span>), then <strong>VoCentering</strong> attempts to search for an optimal value of <em>CoR</em> in the (<strong><em>start_pixel</em></strong> - <span style="color: rgb(128,0,0);">50</span>, <strong><em>start_pixel</em></strong> + <span style="color: rgb(128,0,0);">50</span>) interval (if the user-specified value of <strong><em>start_pixel</em></strong> is None, then <span style="color: rgb(255,102,0);"><em>img_W</em></span>/2 (or a value found in <span style="color: rgb(128,0,0);">/entry1/<strong>tomo_entry</strong>/instrument/detector/x_rotation_axis_pixel_position</span>) is used instead). For some datasets, this default, <span style="color: rgb(128,0,0);">100</span>-pixel-wide range of search may not be sufficiently large to include an optimal value of <em>CoR</em>. Therefore, if the value of <em>CoR</em> determined by <strong>VoCentering</strong> is found to coincide with one of the search-interval limits (i. e. either<strong><em> start_pixel</em></strong> - <span style="color: rgb(128,0,0);">50</span> or <strong><em>start_pixel</em></strong> + <span style="color: rgb(128,0,0);">50</span>), then this value of <em>CoR</em> may not necessarily be optimal, and one should re-run <strong>VoCentering</strong> with a larger value of the <strong><em><em>search_area</em></em></strong> parameter to confirm this result.   </td></tr><tr><td colspan="1" class="confluenceTd">4</td><td colspan="1" class="confluenceTd"><p><em><em>in_datasets</em></em></p></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">5</td><td colspan="1" class="confluenceTd"><em><em>search_radius</em></em></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">6</td><td colspan="1" class="confluenceTd"><em><em>ratio</em></em></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">7</td><td colspan="1" class="confluenceTd"><em><em>out_datasets</em></em></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">8</td><td colspan="1" class="confluenceTd"><p><em><em><em><em>datasets</em></em><em>_to_</em>populate</em><br/></em></p></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">9</td><td colspan="1" class="confluenceTd"><em><em>row_drop</em></em></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">10</td><td colspan="1" class="confluenceTd"><em><em>step</em></em></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd">Floating-point or integer value in pixel units.</td></tr></tbody></table></div><p><br/></p><p><br/></p><h2 id="VoCentering-Usage"><strong>Usage<br/></strong></h2><p>TBC.</p><p><br/></p><p><strong><br/></strong></p><p><strong><br/></strong></p>
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
