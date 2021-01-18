DarkFlatFieldCorrection
-----------------------------

.. raw:: html

    <!DOCTYPE html>
    <html>
        <head>
            <title>Tomography Reconstruction : DarkFlatFieldCorrection</title>
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
    div.rbtoc1592231715026 {padding: 0px;}
    div.rbtoc1592231715026 ul {list-style: disc;margin-left: 0px;}
    div.rbtoc1592231715026 li {margin-left: 0px;padding-left: 0px;}
    .syntaxhighlighter-pre {font-size: small;}
    table {font-size: small;}

    /*]]>*/</style><div class='toc-macro rbtoc1592231715026'>
    <ul class='toc-indentation'>
    <li><a href='#DarkFlatFieldCorrection-Summary'>Summary</a></li>
    <li><a href='#DarkFlatFieldCorrection-Parameters'>Parameters</a>
    <ul class='toc-indentation'>
    <li><a href='#DarkFlatFieldCorrection-Briefdescription'>Brief description</a></li>
    <li><a href='#DarkFlatFieldCorrection-Additionalnotes'>Additional notes</a></li>
    </ul>
    </li>
    <li><a href='#DarkFlatFieldCorrection-Usage'>Usage</a></li>
    </ul>
    </div></p><h2 id="DarkFlatFieldCorrection-Summary"><strong>Summary</strong></h2><p><strong><br/></strong></p><div class="table-wrap"><table class="wrapped relative-table confluenceTable"><colgroup><col style="width: 111.0px;"/><col style="width: 472.0px;"/><col style="width: 160.0px;"/><col style="width: 283.0px;"/><col style="width: 465.0px;"/><col style="width: 164.0px;"/></colgroup><tbody><tr><td class="highlight-red confluenceTd" colspan="6" data-highlight-colour="red" style="text-align: center;"><strong>DarkFlatFieldCorrection</strong></td></tr><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" style="text-align: center;">Process category</th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow" style="text-align: center;">Brief description</th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow"><p style="text-align: center;">Computational demand</p><p style="text-align: center;">for typical tomography data</p><p style="text-align: center;">(low, medium, high)</p></th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow" style="text-align: center;">Comment(s)</th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow" style="text-align: center;">Reference(s)</th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow" style="text-align: center;">Common alternative process(es)</th></tr><tr><td class="confluenceTd">corrector</td><td colspan="1" class="confluenceTd"><p>To apply the standard dark-and-flat-field normalisation to sample projections.</p></td><td colspan="1" class="confluenceTd"><span style="color: rgb(0,128,0);">Low</span></td><td colspan="1" class="confluenceTd"><ol><li>(<em>projection</em> - <em>dark</em>)/(<em>flat</em> - <em>dark</em>), where <em>dark</em> and <em>flat</em> are computed by <strong>averaging</strong> all the supplied <em>dark</em>- and <em>flat</em>-<em>field</em> images, respectively.</li><li>Needs to be explicitly included in every process list that seeks this correction (specifying the location of <em>dark</em>- and <em>flat-field</em> data in a loader, e.g. <a href="NxtomoLoader_76391471.html"><strong>NxtomoLoader</strong></a>, is insufficient in this respect).</li></ol></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr></tbody></table></div><p><br/></p><h2 id="DarkFlatFieldCorrection-Parameters"><strong>Parameters</strong></h2><p><strong><br/></strong></p><div class="table-wrap"><table class="wrapped confluenceTable"><tbody><tr><th class="highlight-red confluenceTh" data-highlight-colour="red"><h3 id="DarkFlatFieldCorrection-Briefdescription">Brief description</h3></th></tr></tbody></table></div><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b>Savu Configurator command</b></div><div class="codeContent panelContent pdl">
    <pre class="syntaxhighlighter-pre" data-syntaxhighlighter-params="brush: java; gutter: false; theme: Confluence" data-theme="Confluence">&gt;&gt;&gt; disp -avv

    -------------------------------------------------------------------------------------
     3) DarkFlatFieldCorrection(savu.plugins.corrections.dark_flat_field_correction)
      A Plugin to apply a simple dark and flatfield correction to raw timeseries data.
        1)            in_datasets : []
        Create a list of the dataset(s) to process.
        2)            upper_bound : None
        Set all values above the upper bound to this value.
        3)           out_datasets : []
        Create a list of the dataset(s) to create.
        4)            lower_bound : None
        Set all values below the lower_bound to this value.
        5)                pattern : PROJECTION
        Data processing pattern is &#39;PROJECTION&#39; or &#39;SINOGRAM&#39;.
        6)        warn_proportion : 0.05
        Output a warning if this proportion of values, or greater, are below and/or above
        the lower/upper bounds, e.g enter 0.05 for 5%.
    -------------------------------------------------------------------------------------

    &gt;&gt;&gt; </pre>
    </div></div><div class="table-wrap"><table class="wrapped confluenceTable"><tbody><tr><th class="highlight-red confluenceTh" data-highlight-colour="red"><h3 id="DarkFlatFieldCorrection-Additionalnotes">Additional notes</h3></th></tr></tbody></table></div><p>For basic information on this process, please use the <em><strong>disp -av </strong></em>(or <em><strong>disp -avv </strong></em>or <em><strong>disp</strong></em><strong> </strong><strong>-v</strong>[<strong>v</strong>] <strong>&lt;</strong><em>process index</em><strong>&gt;</strong>) command in <strong>Savu Configurator </strong>(see above). The table below is intended to provide some additional notes on a number of selected topics:</p><div class="table-wrap"><table class="relative-table wrapped confluenceTable" style="width: 99.5558%;"><colgroup><col style="width: 3.15157%;"/><col style="width: 8.73618%;"/><col style="width: 13.2515%;"/><col style="width: 10.7047%;"/><col style="width: 19.9968%;"/><col style="width: 44.1273%;"/></colgroup><tbody><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" rowspan="2" style="text-align: center;">Item</th><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" rowspan="2" style="text-align: center;">Parameter name</th><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" rowspan="2" style="text-align: center;">Parameter format</th><th class="highlight-yellow confluenceTh" colspan="2" data-highlight-colour="yellow" style="text-align: center;">Example(s)</th><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" rowspan="2" style="text-align: center;">Comment(s)</th></tr><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" style="text-align: center;">Parameter value</th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow" style="text-align: center;">Effect</th></tr><tr><td colspan="1" class="confluenceTd">1</td><td colspan="1" class="confluenceTd"><p><em><em>in_datasets</em><br/></em></p></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">2</td><td colspan="1" class="confluenceTd"><p><em>upper_bound<br/></em></p></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">3</td><td colspan="1" class="confluenceTd"><p><em><em>out_datasets</em></em></p></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">4</td><td colspan="1" class="confluenceTd"><p><em><em>lower_bound</em><br/></em></p></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">5</td><td colspan="1" class="confluenceTd"><p><em>pattern<br/></em></p></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">6</td><td colspan="1" class="confluenceTd"><em>warn_proportion</em></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr></tbody></table></div><p><br/></p><p><br/></p><h2 id="DarkFlatFieldCorrection-Usage"><strong>Usage<br/></strong></h2><p>TBC.</p><p><br/></p><p><strong><br/></strong></p><p><strong><br/></strong></p>
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
