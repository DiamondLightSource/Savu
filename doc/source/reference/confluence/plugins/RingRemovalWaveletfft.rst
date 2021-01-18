RingRemovalWaveletfft
-----------------------------

.. raw:: html

    <!DOCTYPE html>
    <html>
        <head>
            <title>Tomography Reconstruction : RingRemovalWaveletfft</title>
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
    div.rbtoc1592231715480 {padding: 0px;}
    div.rbtoc1592231715480 ul {list-style: disc;margin-left: 0px;}
    div.rbtoc1592231715480 li {margin-left: 0px;padding-left: 0px;}
    .syntaxhighlighter-pre {font-size: small;}
    table {font-size: small;}
    /*]]>*/</style><div class='toc-macro rbtoc1592231715480'>
    <ul class='toc-indentation'>
    <li><a href='#RingRemovalWaveletfft-Summary'>Summary</a></li>
    <li><a href='#RingRemovalWaveletfft-Parameters'>Parameters</a>
    <ul class='toc-indentation'>
    <li><a href='#RingRemovalWaveletfft-Briefdescription'>Brief description</a></li>
    <li><a href='#RingRemovalWaveletfft-Additionalnotes'>Additional notes</a></li>
    </ul>
    </li>
    <li><a href='#RingRemovalWaveletfft-Usage'>Usage</a></li>
    </ul>
    </div></p><h2 id="RingRemovalWaveletfft-Summary"><strong>Summary</strong></h2><p><strong><br/></strong></p><div class="table-wrap"><table class="wrapped relative-table confluenceTable" style="width: 99.9519%;"><colgroup><col style="width: 6.68833%;"/><col style="width: 28.6631%;"/><col style="width: 9.6718%;"/><col style="width: 10.6805%;"/><col style="width: 34.3845%;"/><col style="width: 9.91173%;"/></colgroup><tbody><tr><td class="highlight-red confluenceTd" colspan="6" data-highlight-colour="red" style="text-align: center;"><strong>RingRemovalWaveletfft</strong></td></tr><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" style="text-align: center;">Process category</th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow" style="text-align: center;">Brief description</th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow"><p style="text-align: center;">Computational demand</p><p style="text-align: center;">for typical tomography data</p><p style="text-align: center;"><span style="color: rgb(0,0,0);">(low, medium, high)</span></p></th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow" style="text-align: center;">Comment(s)</th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow" style="text-align: center;">Reference(s)</th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow" style="text-align: center;">Common alternative process(es)</th></tr><tr><td class="confluenceTd">corrector</td><td colspan="1" class="confluenceTd"><p>To suppress ring artefacts.</p></td><td colspan="1" class="confluenceTd"><span style="color: rgb(255,0,0);">High</span></td><td colspan="1" class="confluenceTd"><ol><li>Computationally demanding as it relies on applying Fourier Transform.</li><li>Over-aggressive application<strong> </strong>can lead to new artefacts.</li></ol></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><ol><li><strong><a href="CcpiRingArtefactFilter_76392246.html">CcpiRingArtefactFilter</a></strong></li><li><strong><a href="RavenFilter_76392306.html">RavenFilter</a></strong></li></ol></td></tr></tbody></table></div><p><br/></p><h2 id="RingRemovalWaveletfft-Parameters"><strong>Parameters</strong></h2><p><strong><br/></strong></p><div class="table-wrap"><table class="wrapped confluenceTable"><colgroup><col/></colgroup><tbody><tr><th class="highlight-red confluenceTh" data-highlight-colour="red"><h3 id="RingRemovalWaveletfft-Briefdescription">Brief description</h3></th></tr></tbody></table></div><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b>Savu Configurator command</b></div><div class="codeContent panelContent pdl">
    <pre class="syntaxhighlighter-pre" data-syntaxhighlighter-params="brush: java; gutter: false; theme: Confluence" data-theme="Confluence">&gt;&gt;&gt; disp -avv

    -------------------------------------------------------------------------------------
     1) RingRemovalWaveletfft(savu.plugins.ring_removal.ring_removal_waveletfft)
      A plugin removes ring artefacts
        1)            in_datasets : []
        Create a list of the dataset(s) to process.
        2)                  level : 3
        Wavelet decomposition level.
        3)           out_datasets : []
        Create a list of the dataset(s) to create.
        4)                 nvalue : 5
        Order of the the Daubechies (DB) wavelets.
        5)                  padFT : 20
        Padding for Fourier transform.
        6)                  sigma : 1
        Damping parameter. Larger is stronger.
    -------------------------------------------------------------------------------------

    &gt;&gt;&gt; </pre>
    </div></div><div class="table-wrap"><table class="wrapped confluenceTable"><tbody><tr><th class="highlight-red confluenceTh" data-highlight-colour="red"><h3 id="RingRemovalWaveletfft-Additionalnotes">Additional notes</h3></th></tr></tbody></table></div><p>For basic information on this process, please use the <em><strong>disp -av </strong></em>(or <em><strong>disp -avv </strong></em>or <em><strong>disp</strong></em><strong> </strong><strong>-v</strong>[<strong>v</strong>] <strong>&lt;</strong><em>process index</em><strong>&gt;</strong>) command in <strong>Savu Configurator </strong>(see above). The table below is intended to provide some additional notes on a number of selected topics:</p><div class="table-wrap"><table class="relative-table wrapped confluenceTable" style="width: 99.5558%;"><colgroup><col style="width: 3.15157%;"/><col style="width: 8.73618%;"/><col style="width: 13.2515%;"/><col style="width: 10.7047%;"/><col style="width: 19.9968%;"/><col style="width: 44.1273%;"/></colgroup><tbody><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" rowspan="2" style="text-align: center;">Item</th><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" rowspan="2" style="text-align: center;">Parameter name</th><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" rowspan="2" style="text-align: center;">Parameter format</th><th class="highlight-yellow confluenceTh" colspan="2" data-highlight-colour="yellow" style="text-align: center;">Example(s)</th><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" rowspan="2" style="text-align: center;">Comment(s)</th></tr><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" style="text-align: center;">Parameter value</th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow" style="text-align: center;">Effect</th></tr><tr><td colspan="1" class="confluenceTd">1</td><td colspan="1" class="confluenceTd"><p><em><em>in_datasets</em><br/></em></p></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">2</td><td colspan="1" class="confluenceTd"><p><em>level<br/></em></p></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">3</td><td colspan="1" class="confluenceTd"><p><em><em>out_datasets</em></em></p></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">4</td><td colspan="1" class="confluenceTd"><p><em><em>nvalue</em><br/></em></p></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">5</td><td colspan="1" class="confluenceTd"><p><em>padFT<br/></em></p></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">6</td><td colspan="1" class="confluenceTd"><em>sigma</em></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr></tbody></table></div><p><br/></p><p><br/></p><h2 id="RingRemovalWaveletfft-Usage"><strong>Usage<br/></strong></h2><p>TBC.</p><p><br/></p><p><strong><br/></strong></p><p><strong><br/></strong></p>
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
