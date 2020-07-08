HDF5 Saver
-----------------

.. raw:: html

    <!DOCTYPE html>
    <html>
        <head>
            <title>Tomography Reconstruction : Hdf5saver</title>
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
    div.rbtoc1592231715195 {padding: 0px;}
    div.rbtoc1592231715195 ul {list-style: disc;margin-left: 0px;}
    div.rbtoc1592231715195 li {margin-left: 0px;padding-left: 0px;}
    .syntaxhighlighter-pre {font-size: small;}
    table {font-size: small;}
    /*]]>*/</style><div class='toc-macro rbtoc1592231715195'>
    <ul class='toc-indentation'>
    <li><a href='#Hdf5saver-Summary'>Summary</a></li>
    <li><a href='#Hdf5saver-Parameters'>Parameters</a>
    <ul class='toc-indentation'>
    <li><a href='#Hdf5saver-Briefdescription'>Brief description</a></li>
    <li><a href='#Hdf5saver-Additionalnotes'>Additional notes</a></li>
    </ul>
    </li>
    <li><a href='#Hdf5saver-Usage'>Usage</a></li>
    </ul>
    </div></p><h2 id="Hdf5saver-Summary"><strong>Summary</strong></h2><p><strong><br/></strong></p><div class="table-wrap"><table class="wrapped relative-table confluenceTable" style="width: 99.9519%;"><colgroup><col style="width: 5.72701%;"/><col style="width: 13.615%;"/><col style="width: 10.6339%;"/><col style="width: 35.2488%;"/><col style="width: 24.3837%;"/><col style="width: 10.3916%;"/></colgroup><tbody><tr><td class="highlight-blue confluenceTd" colspan="6" data-highlight-colour="blue" style="text-align: center;"><strong>Hdf5saver</strong></td></tr><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" style="text-align: center;">Process category</th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow" style="text-align: center;">Brief description</th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow"><p style="text-align: center;">Computational demand</p><p style="text-align: center;">for typical tomography data</p><p style="text-align: center;">(low, medium, high)</p></th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow" style="text-align: center;">Comment(s)</th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow" style="text-align: center;">Reference(s)</th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow" style="text-align: center;">Common alternative process(es)</th></tr><tr><td class="confluenceTd">saver</td><td colspan="1" class="confluenceTd">To save reconstruction(s) to output file(s).</td><td colspan="1" class="confluenceTd"><span style="color: rgb(0,128,0);">Low</span></td><td colspan="1" class="confluenceTd">By default, <strong>Hdf5saver</strong> is the final process in every process list (hence there is normally no need to add it explicitly). It should only be explicitly added to a process list if one wishes to overwrite its default parameters, which must be done individually for each dataset (advanced<em><em> </em></em>use).</td><td colspan="1" class="confluenceTd"><a class="external-link" href="https://support.hdfgroup.org/HDF5/" rel="nofollow">HDF5 data model &amp; file format </a></td><td colspan="1" class="confluenceTd"><strong>TiffSaver</strong></td></tr></tbody></table></div><p><br/></p><h2 id="Hdf5saver-Parameters"><strong>Parameters</strong></h2><p><strong><br/></strong></p><div class="table-wrap"><table class="wrapped confluenceTable"><colgroup><col/></colgroup><tbody><tr><th class="highlight-blue confluenceTh" data-highlight-colour="blue"><h3 id="Hdf5saver-Briefdescription">Brief description</h3></th></tr></tbody></table></div><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b>Savu Configurator command</b></div><div class="codeContent panelContent pdl">
    <pre class="syntaxhighlighter-pre" data-syntaxhighlighter-params="brush: java; gutter: false; theme: Confluence" data-theme="Confluence">&gt;&gt;&gt; disp 1 -avv

    -------------------------------------------------------------------------------------
     5) Hdf5Saver(savu.plugins.savers.hdf5_saver)
      A class to save data to a hdf5 output file
        1)            in_datasets : []
        The name of the dataset to save.
        2)                pattern : optimum
        Optimise data storage to this access pattern: &#39;optimum&#39; will automate this
        process by choosing the output pattern from the previous plugin, if it exists,
        else the first pattern.
    -------------------------------------------------------------------------------------

    &gt;&gt;&gt;</pre>
    </div></div><div class="table-wrap"><table class="wrapped confluenceTable"><colgroup><col/></colgroup><tbody><tr><th class="highlight-blue confluenceTh" data-highlight-colour="blue"><h3 id="Hdf5saver-Additionalnotes">Additional notes</h3></th></tr></tbody></table></div><p>For basic information on this process, please use the <em><strong>disp -av </strong></em>(or <em><strong>disp -avv </strong></em>or <em><strong>disp</strong></em><strong> </strong><strong>-v</strong>[<strong>v</strong>] <strong>&lt;</strong><em>process index</em><strong>&gt;</strong>) command in <strong>Savu Configurator </strong>(see above). The table below is intended to provide some additional notes on a number of selected topics:</p><div class="table-wrap"><table class="relative-table wrapped confluenceTable" style="width: 99.9385%;"><colgroup><col style="width: 3.14039%;"/><col style="width: 8.49035%;"/><col style="width: 13.3415%;"/><col style="width: 25.3171%;"/><col style="width: 34.5248%;"/><col style="width: 15.1858%;"/></colgroup><tbody><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" rowspan="2" style="text-align: center;">Item</th><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" rowspan="2" style="text-align: center;">Parameter name</th><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" rowspan="2" style="text-align: center;">Parameter format</th><th class="highlight-yellow confluenceTh" colspan="2" data-highlight-colour="yellow" style="text-align: center;">Example(s)</th><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" rowspan="2" style="text-align: center;">Comment(s)</th></tr><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow" style="text-align: center;">Parameter value</th><th class="highlight-yellow confluenceTh" colspan="1" data-highlight-colour="yellow" style="text-align: center;">Effect</th></tr><tr><td class="confluenceTd">1</td><td class="confluenceTd"><p><em>in_datasets</em></p></td><td class="confluenceTd"><br/></td><td class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">2</td><td colspan="1" class="confluenceTd"><p><em>pattern</em></p></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><br/></td></tr></tbody></table></div><p><br/></p><p><br/></p><h2 id="Hdf5saver-Usage"><strong>Usage<br/></strong></h2><p>TBC.</p><p><br/></p><p><strong><br/></strong></p><p><strong><br/></strong></p>
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
