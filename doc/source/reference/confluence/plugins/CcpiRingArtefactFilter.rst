CcpiRingArtefactFilter
-----------------------------

.. raw:: html

    <!DOCTYPE html>
    <html>
        <head>
            <title>Tomography Reconstruction : CcpiRingArtefactFilter</title>
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
    div.rbtoc1592231714970 {padding: 0px;}
    div.rbtoc1592231714970 ul {list-style: disc;margin-left: 0px;}
    div.rbtoc1592231714970 li {margin-left: 0px;padding-left: 0px;}
    .syntaxhighlighter-pre {font-size: small;}
    table {font-size: small;}

    /*]]>*/</style><div class='toc-macro rbtoc1592231714970'>
    <ul class='toc-indentation'>
    <li><a href='#CcpiRingArtefactFilter-Summary'>Summary</a></li>
    <li><a href='#CcpiRingArtefactFilter-Parameters'>Parameters</a>
    <ul class='toc-indentation'>
    <li><a href='#CcpiRingArtefactFilter-Briefdescription'>Brief description</a></li>
    <li><a href='#CcpiRingArtefactFilter-Additionalnotes'>Additional notes</a></li>
    </ul>
    </li>
    <li><a href='#CcpiRingArtefactFilter-Usage'>Usage</a></li>
    </ul>
    </div></p><h2 id="CcpiRingArtefactFilter-Summary"><strong>Summary</strong></h2><p><strong><br/></strong></p><div class="table-wrap"><table class="wrapped relative-table confluenceTable" style="width: 99.9519%;"><colgroup><col style="width: 6.48371%;"/><col style="width: 8.68721%;"/><col style="width: 14.5169%;"/><col style="width: 31.2855%;"/><col style="width: 27.5189%;"/><col style="width: 11.5078%;"/></colgroup><tbody><tr><td class="highlight-red confluenceTd" colspan="6" data-highlight-colour="red" style="text-align: center;"><strong>CcpiRingArtefactFilter</strong></td></tr><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" style="text-align: center;">Process category</th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow" style="text-align: center;">Brief description</th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow"><p style="text-align: center;">Computational demand</p><p style="text-align: center;">for typical tomography data</p><p style="text-align: center;">(low, medium, high)</p></th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow" style="text-align: center;">Comment(s)</th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow" style="text-align: center;">Reference(s)</th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow" style="text-align: center;">Common alternative process(es)</th></tr><tr><td class="confluenceTd">corrector</td><td colspan="1" class="confluenceTd"><p>To suppress ring artefacts.</p></td><td colspan="1" class="confluenceTd"><span style="color: rgb(0,128,0);">Low</span></td><td colspan="1" class="confluenceTd"><ol><li>Implements the same ring-suppression algorithm as that used by the <em>tomo-centre</em> &amp; <em>tomo-recon</em> commands.</li><li>Over-aggressive application<strong> </strong>can lead to new artefacts in the form of dark rings ('shadows').</li></ol></td><td colspan="1" class="confluenceTd"><a class="external-link" href="https://www.sciencedirect.com/science/article/pii/S089396591000282X" rel="nofollow">An analytical formula for ring artefact suppression in X-ray tomography</a> and references therein.</td><td colspan="1" class="confluenceTd"><ol><li><strong><a href="RingRemovalWaveletfft_76392751.html">RingRemovalWaveletfft</a></strong></li><li><strong><a href="RavenFilter_76392306.html">RavenFilter</a></strong></li></ol></td></tr></tbody></table></div><p><br/></p><h2 id="CcpiRingArtefactFilter-Parameters"><strong>Parameters</strong></h2><p><strong><br/></strong></p><div class="table-wrap"><table class="wrapped confluenceTable"><colgroup><col/></colgroup><tbody><tr><th class="highlight-red confluenceTh" data-highlight-colour="red"><h3 id="CcpiRingArtefactFilter-Briefdescription">Brief description</h3></th></tr></tbody></table></div><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b>Savu Configurator command</b></div><div class="codeContent panelContent pdl">
    <pre class="syntaxhighlighter-pre" data-syntaxhighlighter-params="brush: java; gutter: false; theme: Confluence" data-theme="Confluence">&gt;&gt;&gt; disp -avv

    -------------------------------------------------------------------------------------
     1) CcpiRingArtefactFilter(savu.plugins.ring_removal.ccpi_ring_artefact_filter)
      A plugin to perform ring artefact removal
        1)             num_series : 1
        High aspect ration compensation (for plate-like objects only) .
        2)                param_r : 0.005
        The correction strength - decrease (typically in order of magnitude steps) to
        increase ring supression, or increase to reduce ring supression.
        3)            in_datasets : []
        Create a list of the dataset(s) to process.
        4)           out_datasets : []
        Create a list of the dataset(s) to create.
        5)                param_n : 0
        Unknown description (for plate-like objects only).
    -------------------------------------------------------------------------------------

    &gt;&gt;&gt;</pre>
    </div></div><div class="table-wrap"><table class="wrapped confluenceTable"><tbody><tr><th class="highlight-red confluenceTh" data-highlight-colour="red"><h3 id="CcpiRingArtefactFilter-Additionalnotes">Additional notes</h3></th></tr></tbody></table></div><p>For basic information on this process, please use the <em><strong>disp -av </strong></em>(or <em><strong>disp -avv </strong></em>or <em><strong>disp</strong></em><strong> </strong><strong>-v</strong>[<strong>v</strong>] <strong>&lt;</strong><em>process index</em><strong>&gt;</strong>) command in <strong>Savu Configurator </strong>(see above). The table below is intended to provide some additional notes on a number of selected topics:</p><div class="table-wrap"><table class="relative-table wrapped confluenceTable" style="width: 99.5558%;"><colgroup><col style="width: 3.15157%;"/><col style="width: 8.73618%;"/><col style="width: 13.2515%;"/><col style="width: 10.7047%;"/><col style="width: 19.9968%;"/><col style="width: 44.1273%;"/></colgroup><tbody><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" rowspan="2" style="text-align: center;">Item</th><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" rowspan="2" style="text-align: center;">Parameter name</th><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" rowspan="2" style="text-align: center;">Parameter format</th><th class="highlight-yellow confluenceTh" colspan="2" data-highlight-colour="yellow" style="text-align: center;">Example(s)</th><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" rowspan="2" style="text-align: center;">Comment(s)</th></tr><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" style="text-align: center;">Parameter value</th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow" style="text-align: center;">Effect</th></tr><tr><td colspan="1" class="confluenceTd">1</td><td colspan="1" class="confluenceTd"><p><em><em>num_series</em><br/></em></p></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">2</td><td colspan="1" class="confluenceTd"><p><em>param_r<br/></em></p></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">3</td><td colspan="1" class="confluenceTd"><p><em><em>in_datasets</em></em></p></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">4</td><td colspan="1" class="confluenceTd"><p><em><em>out_datasets</em></em></p></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">5</td><td colspan="1" class="confluenceTd"><p><em><em>param_n</em><br/></em></p></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr></tbody></table></div><p><br/></p><p><br/></p><h2 id="CcpiRingArtefactFilter-Usage"><strong>Usage<br/></strong></h2><p>TBC.</p><p><br/></p><p><strong><br/></strong></p><p><strong><br/></strong></p>
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
