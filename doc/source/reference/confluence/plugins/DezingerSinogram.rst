DezingerSinogram
-----------------------------

.. raw:: html

    <!DOCTYPE html>
    <html>
        <head>
            <title>Tomography Reconstruction : DezingerSinogram</title>
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
    div.rbtoc1592231715106 {padding: 0px;}
    div.rbtoc1592231715106 ul {list-style: disc;margin-left: 0px;}
    div.rbtoc1592231715106 li {margin-left: 0px;padding-left: 0px;}
    .syntaxhighlighter-pre {font-size: small;}
    table {font-size: small;}
    /*]]>*/</style><div class='toc-macro rbtoc1592231715106'>
    <ul class='toc-indentation'>
    <li><a href='#DezingerSinogram-Summary'>Summary</a></li>
    <li><a href='#DezingerSinogram-Parameters'>Parameters</a>
    <ul class='toc-indentation'>
    <li><a href='#DezingerSinogram-Briefdescription'>Brief description</a></li>
    <li><a href='#DezingerSinogram-Additionalnotes'>Additional notes</a></li>
    </ul>
    </li>
    <li><a href='#DezingerSinogram-Usage'>Usage</a></li>
    </ul>
    </div></p><h2 id="DezingerSinogram-Summary"><strong>Summary</strong></h2><p><strong><br/></strong></p><div class="table-wrap"><table class="wrapped relative-table confluenceTable" style="width: 99.9519%;"><colgroup><col style="width: 6.35211%;"/><col style="width: 13.9978%;"/><col style="width: 9.91253%;"/><col style="width: 23.6142%;"/><col style="width: 34.5282%;"/><col style="width: 11.5952%;"/></colgroup><tbody><tr><td class="highlight-red confluenceTd" colspan="6" data-highlight-colour="red" style="text-align: center;"><strong>DezingerSinogram</strong></td></tr><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" style="text-align: center;">Process category</th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow" style="text-align: center;">Brief description</th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow"><p style="text-align: center;">Computational demand</p><p style="text-align: center;">for typical tomography data</p><p style="text-align: center;">(low, medium, high)</p></th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow" style="text-align: center;">Comment(s)</th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow" style="text-align: center;">Reference(s)</th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow" style="text-align: center;">Common alternative process(es)</th></tr><tr><td class="confluenceTd">filter</td><td colspan="1" class="confluenceTd"><p>To remove <em>zingers</em> from data.</p></td><td colspan="1" class="confluenceTd"><span style="color: rgb(0,128,0);">Low</span></td><td colspan="1" class="confluenceTd"><ol><li>Capable of handling image data in the floating-point format.</li><li>Needs to be included after <a href="DarkFlatFieldCorrection_76392109.html"><strong>DarkFlatFieldCorrection</strong></a>.</li></ol></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><ol><li><strong><a href="Dezinger_76392334.html">Dezinger</a></strong></li><li><strong>DezingerSimple</strong></li></ol></td></tr></tbody></table></div><p><br/></p><h2 id="DezingerSinogram-Parameters"><strong>Parameters</strong></h2><p><strong><br/></strong></p><div class="table-wrap"><table class="wrapped confluenceTable"><tbody><tr><th class="highlight-red confluenceTh" data-highlight-colour="red"><h3 id="DezingerSinogram-Briefdescription">Brief description</h3></th></tr></tbody></table></div><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b>Savu Configurator command</b></div><div class="codeContent panelContent pdl">
    <pre class="syntaxhighlighter-pre" data-syntaxhighlighter-params="brush: java; gutter: false; theme: Confluence" data-theme="Confluence">&gt;&gt;&gt; disp -avv

    -------------------------------------------------------------------------------------
     1) DezingerSinogram(savu.plugins.filters.dezinger_sinogram)
      A plugin working in sinogram space to removes zingers.
        1)              tolerance : 0.08
        Threshold for detecting zingers, greater is less sensitive.
        2)            in_datasets : []
        Create a list of the dataset(s) to process.
        3)           out_datasets : []
        Create a list of the dataset(s) to create.
    -------------------------------------------------------------------------------------

    &gt;&gt;&gt; </pre>
    </div></div><div class="table-wrap"><table class="wrapped confluenceTable"><colgroup><col/></colgroup><tbody><tr><th class="highlight-red confluenceTh" data-highlight-colour="red"><h3 id="DezingerSinogram-Additionalnotes">Additional notes</h3></th></tr></tbody></table></div><p>For basic information on this process, please use the <em><strong>disp -av </strong></em>(or <em><strong>disp -avv </strong></em>or <em><strong>disp</strong></em><strong> </strong><strong>-v</strong>[<strong>v</strong>] <strong>&lt;</strong><em>process index</em><strong>&gt;</strong>) command in <strong>Savu Configurator </strong>(see above). The table below is intended to provide some additional notes on a number of selected topics:</p><div class="table-wrap"><table class="relative-table wrapped confluenceTable" style="width: 99.5558%;"><colgroup><col style="width: 3.15157%;"/><col style="width: 8.73618%;"/><col style="width: 13.2515%;"/><col style="width: 10.7047%;"/><col style="width: 19.9968%;"/><col style="width: 44.1273%;"/></colgroup><tbody><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" rowspan="2" style="text-align: center;">Item</th><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" rowspan="2" style="text-align: center;">Parameter name</th><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" rowspan="2" style="text-align: center;">Parameter format</th><th class="highlight-yellow confluenceTh" colspan="2" data-highlight-colour="yellow" style="text-align: center;">Example(s)</th><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" rowspan="2" style="text-align: center;">Comment(s)</th></tr><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" style="text-align: center;">Parameter value</th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow" style="text-align: center;">Effect</th></tr><tr><td colspan="1" class="confluenceTd">1</td><td colspan="1" class="confluenceTd"><p><em><em>tolerance<br/></em></em></p></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">2</td><td colspan="1" class="confluenceTd"><em><em>in_datasets</em></em></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">3</td><td colspan="1" class="confluenceTd"><p><em><em>out_datasets</em></em></p></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr></tbody></table></div><p><br/></p><p><br/></p><h2 id="DezingerSinogram-Usage"><strong>Usage<br/></strong></h2><p>TBC.</p><p><br/></p><p><strong><br/></strong></p><p><strong><br/></strong></p>
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
