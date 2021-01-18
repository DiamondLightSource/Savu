RavenFilter
-----------------------------

.. raw:: html

    <!DOCTYPE html>
    <html>
        <head>
            <title>Tomography Reconstruction : RavenFilter</title>
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
    div.rbtoc1592231715442 {padding: 0px;}
    div.rbtoc1592231715442 ul {list-style: disc;margin-left: 0px;}
    div.rbtoc1592231715442 li {margin-left: 0px;padding-left: 0px;}
    .syntaxhighlighter-pre {font-size: small;}
    table {font-size: small;}
    /*]]>*/</style><div class='toc-macro rbtoc1592231715442'>
    <ul class='toc-indentation'>
    <li><a href='#RavenFilter-Summary'>Summary</a></li>
    <li><a href='#RavenFilter-Parameters'>Parameters</a>
    <ul class='toc-indentation'>
    <li><a href='#RavenFilter-Briefdescription'>Brief description</a></li>
    <li><a href='#RavenFilter-Additionalnotes'>Additional notes</a></li>
    </ul>
    </li>
    <li><a href='#RavenFilter-Usage'>Usage</a></li>
    </ul>
    </div></p><h2 id="RavenFilter-Summary"><strong>Summary</strong></h2><p><strong><br/></strong></p><div class="table-wrap"><table class="wrapped relative-table confluenceTable" style="width: 99.9519%;"><colgroup><col style="width: 6.64179%;"/><col style="width: 8.95201%;"/><col style="width: 12.1762%;"/><col style="width: 13.5227%;"/><col style="width: 48.9336%;"/><col style="width: 9.77371%;"/></colgroup><tbody><tr><td class="highlight-red confluenceTd" colspan="6" data-highlight-colour="red" style="text-align: center;"><strong>RavenFilter</strong></td></tr><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" style="text-align: center;">Process category</th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow" style="text-align: center;">Brief description</th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow"><p style="text-align: center;">Computational demand</p><p style="text-align: center;">for typical tomography data</p><p style="text-align: center;">(low, medium, high)</p></th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow" style="text-align: center;">Comment(s)</th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow" style="text-align: center;">Reference(s)</th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow" style="text-align: center;">Common alternative process(es)</th></tr><tr><td class="confluenceTd">filter</td><td colspan="1" class="confluenceTd"><p>To suppress ring artefacts.</p></td><td colspan="1" class="confluenceTd">Medium</td><td colspan="1" class="confluenceTd"><ol><li>Operates on sinograms.</li><li>Over-aggressive application<strong> </strong>can lead to new artefacts.</li></ol></td><td colspan="1" class="confluenceTd"><a class="external-link" href="http://aip.scitation.org/doi/abs/10.1063/1.1149043" rel="nofollow">Numerical removal of ring artifacts in microtomography</a></td><td colspan="1" class="confluenceTd"><ol><li><strong><a href="RingRemovalWaveletfft_76392751.html">RingRemovalWaveletfft</a></strong></li><li><strong><a href="CcpiRingArtefactFilter_76392246.html">CcpiRingArtefactFilter</a></strong></li></ol></td></tr></tbody></table></div><p><br/></p><h2 id="RavenFilter-Parameters"><strong>Parameters</strong></h2><p><strong><br/></strong></p><div class="table-wrap"><table class="wrapped confluenceTable"><tbody><tr><th class="highlight-red confluenceTh" data-highlight-colour="red"><h3 id="RavenFilter-Briefdescription">Brief description</h3></th></tr></tbody></table></div><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b>Savu Configurator command</b></div><div class="codeContent panelContent pdl">
    <pre class="syntaxhighlighter-pre" data-syntaxhighlighter-params="brush: java; gutter: false; theme: Confluence" data-theme="Confluence">&gt;&gt;&gt; disp -avv

    -------------------------------------------------------------------------------------
     1) RavenFilter(savu.plugins.ring_removal.raven_filter)
      A plugin to remove ring artefacts
        1)                 uvalue : 20
        To define the shape of filter, e.g. bad=10, moderate=20, minor=50.
        2)            in_datasets : []
        Create a list of the dataset(s) to process.
        3)                 nvalue : 4
        To define the shape of filter.
        4)           out_datasets : []
        Create a list of the dataset(s) to create.
        5)                 vvalue : 2
        How many rows to be applied the filter.
        6)                  padFT : 20
        Padding for Fourier transform.
    -------------------------------------------------------------------------------------

    &gt;&gt;&gt; </pre>
    </div></div><div class="table-wrap"><table class="wrapped confluenceTable"><tbody><tr><th class="highlight-red confluenceTh" data-highlight-colour="red"><h3 id="RavenFilter-Additionalnotes">Additional notes</h3></th></tr></tbody></table></div><p>For basic information on this process, please use the <em><strong>disp -av </strong></em>(or <em><strong>disp -avv </strong></em>or <em><strong>disp</strong></em><strong> </strong><strong>-v</strong>[<strong>v</strong>] <strong>&lt;</strong><em>process index</em><strong>&gt;</strong>) command in <strong>Savu Configurator </strong>(see above). The table below is intended to provide some additional notes on a number of selected topics:</p><div class="table-wrap"><table class="relative-table wrapped confluenceTable" style="width: 99.4465%;"><colgroup><col style="width: 3.15594%;"/><col style="width: 8.72318%;"/><col style="width: 13.2354%;"/><col style="width: 10.7013%;"/><col style="width: 20.0361%;"/><col style="width: 44.1481%;"/></colgroup><tbody><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" rowspan="2" style="text-align: center;">Item</th><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" rowspan="2" style="text-align: center;">Parameter name</th><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" rowspan="2" style="text-align: center;">Parameter format</th><th class="highlight-yellow confluenceTh" colspan="2" data-highlight-colour="yellow" style="text-align: center;">Example(s)</th><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" rowspan="2" style="text-align: center;">Comment(s)</th></tr><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" style="text-align: center;">Parameter value</th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow" style="text-align: center;">Effect</th></tr><tr><td rowspan="3" class="confluenceTd">1</td><td rowspan="3" class="confluenceTd"><p><em><em>uvalue</em><br/></em></p></td><td rowspan="3" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><span style="color: rgb(128,0,0);">10</span></td><td colspan="1" class="confluenceTd">To suppress prominent ring artefacts.</td><td rowspan="3" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd"><span style="color: rgb(128,0,0);">20</span></td><td colspan="1" class="confluenceTd">To suppress moderate ring artefacts.</td></tr><tr><td colspan="1" class="confluenceTd"><span style="color: rgb(128,0,0);">50</span></td><td colspan="1" class="confluenceTd">To suppress minor ring artefacts.</td></tr><tr><td colspan="1" class="confluenceTd">2</td><td colspan="1" class="confluenceTd"><p><em><em>in_datasets</em></em></p></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">3</td><td colspan="1" class="confluenceTd"><em><em>nvalue</em></em></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">4</td><td colspan="1" class="confluenceTd"><p><em><em>out_datasets</em></em></p></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">5</td><td colspan="1" class="confluenceTd"><p><em><em>vvalue</em><br/></em></p></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">6</td><td colspan="1" class="confluenceTd"><em>padFT</em></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr></tbody></table></div><p><br/></p><p><br/></p><h2 id="RavenFilter-Usage"><strong>Usage<br/></strong></h2><p>TBC.</p><p><br/></p><p><strong><br/></strong></p><p><strong><br/></strong></p>
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
