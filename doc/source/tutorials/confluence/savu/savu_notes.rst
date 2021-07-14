:orphan:

.. _savu_notes:

Savu - notes on basic use
-----------------------------

**Note**: The following tutorial for I13 users is out-of-date. 

.. raw:: html

    <!DOCTYPE html>
    <html>
        <head>
            <title>Tomography Reconstruction : Reconstruction from image data in the HDF format: Savu - notes on standard use</title>
            <link rel="stylesheet" href="styles/site.css" type="text/css" />
            <META http-equiv="Content-Type" content="text/html; charset=UTF-8">
        </head>

        <body class="theme-default aui-theme-default">
            <div id="page">
                <div id="main" class="aui-page-panel">


                    <div id="content" class="view">
                        <div class="page-metadata">







                Created by <span class='author'> Kaz Wanelik</span>, last modified on Jun 10, 2020
                            </div>
                        <div id="main-content" class="wiki-content group">
                        <p><br/></p><p><style type='text/css'>/*<![CDATA[*/
    div.rbtoc1592231713184 {padding: 0px;}
    div.rbtoc1592231713184 ul {list-style: disc;margin-left: 0px;}
    div.rbtoc1592231713184 li {margin-left: 0px;padding-left: 0px;}
    .syntaxhighlighter-pre {font-size: small;}
    table {font-size: small;}

    /*]]>*/</style><div class='toc-macro rbtoc1592231713184'>
    <ul class='toc-indentation'>
    <li><a href='#ReconstructionfromimagedataintheHDFformat:Savu-notesonstandarduse-Generaladvice'>General advice</a></li>
    <li><a href='#ReconstructionfromimagedataintheHDFformat:Savu-notesonstandarduse-Suggestedprocessestoincludeinaprocesslistfortomographyreconstruction'>Suggested processes to include in a process list for tomography reconstruction</a></li>
    <li><a href='#ReconstructionfromimagedataintheHDFformat:Savu-notesonstandarduse-Examples'>Examples</a>
    <ul class='toc-indentation'>
    <li><a href='#ReconstructionfromimagedataintheHDFformat:Savu-notesonstandarduse-Example1:SimpleprocesslistincludingVoCentering'>Example 1: Simple process list including VoCentering</a>
    <ul class='toc-indentation'>
    <li><a href='#ReconstructionfromimagedataintheHDFformat:Savu-notesonstandarduse-WheretolookfortheoptimalvalueofCoRdeterminedbyVoCentering?'>Where to look for the optimal value of CoR determined by VoCentering?</a></li>
    </ul>
    </li>
    <li><a href='#ReconstructionfromimagedataintheHDFformat:Savu-notesonstandarduse-Example2:MoreadvancedprocesslistincludingVoCentering'>Example 2: More advanced process list including VoCentering</a></li>
    <li><a href='#ReconstructionfromimagedataintheHDFformat:Savu-notesonstandarduse-Example3:Simpleprocesslistforgeneratingsinograms'>Example 3: Simple process list for generating sinograms</a></li>
    <li><a href='#ReconstructionfromimagedataintheHDFformat:Savu-notesonstandarduse-Example4a:Simpleprocesslistforgeneratingdark-and-flat-field-correctedradiographyimages'>Example 4a: Simple process list for generating dark-and-flat-field-corrected radiography images</a></li>
    <li><a href='#ReconstructionfromimagedataintheHDFformat:Savu-notesonstandarduse-Example4b:Simpleprocesslistforgeneratingdark-and-flat-field-correctedtomographyrawimages'>Example 4b: Simple process list for generating dark-and-flat-field-corrected tomography raw images</a></li>
    <li><a href='#ReconstructionfromimagedataintheHDFformat:Savu-notesonstandarduse-Example5:Processlistforoverridinginternalflat-anddark-fieldimageswithexternalones'>Example 5: Process list for overriding internal flat- and dark-field images with external ones</a></li>
    <li><a href='#ReconstructionfromimagedataintheHDFformat:Savu-notesonstandarduse-Example6:Simpleprocesslistforapplyinglens-distortioncorrectiontograting-interferometryTIFFimages'>Example 6: Simple process list for applying lens-distortion correction to grating-interferometry TIFF images</a></li>
    <li><a href='#ReconstructionfromimagedataintheHDFformat:Savu-notesonstandarduse-Example7:Processlistforreconstructingaseriesofidenticaltomographyscans(storedsequentiallyinasingle3ddataset)'>Example 7: Process list for reconstructing a series of identical tomography scans (stored sequentially in a single 3d dataset)</a></li>
    <li><a href='#ReconstructionfromimagedataintheHDFformat:Savu-notesonstandarduse-Example8:Simpleprocesslistforreconstructingaflat-and-dark-field-correcteddatasetthatwaspreviouslygeneratedinSavu'>Example 8: Simple process list for reconstructing a flat-and-dark-field-corrected dataset that was previously generated in Savu</a></li>
    <li><a href='#ReconstructionfromimagedataintheHDFformat:Savu-notesonstandarduse-Example9:Simpleprocesslistforreconstructinganoff-centrescantakenovertherangeof360deg'>Example 9: Simple process list for reconstructing an off-centre scan taken over the range of 360 deg</a></li>
    </ul>
    </li>
    <li><a href='#ReconstructionfromimagedataintheHDFformat:Savu-notesonstandarduse-Appendices'>Appendices</a>
    <ul class='toc-indentation'>
    <li><a href='#ReconstructionfromimagedataintheHDFformat:Savu-notesonstandarduse-AppendixA:Interoperabilityoftheparameter-tuningandpreviewingoperations'>Appendix A: Interoperability of the parameter-tuning and previewing operations</a></li>
    <li><a href='#ReconstructionfromimagedataintheHDFformat:Savu-notesonstandarduse-AppendixB:Briefreferenceguidetospecifyingvaluesfortheparameter-tuningoperations'>Appendix B: Brief reference guide to specifying values for the parameter-tuning operations</a></li>
    <li><a href='#ReconstructionfromimagedataintheHDFformat:Savu-notesonstandarduse-AppendixC:Batchprocessing'>Appendix C: Batch processing</a></li>
    </ul>
    </li>
    </ul>
    </div></p><div class="table-wrap"><table class="wrapped confluenceTable"><colgroup><col/></colgroup><tbody><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow"><h2 id="ReconstructionfromimagedataintheHDFformat:Savu-notesonstandarduse-Generaladvice"><strong>General advice<br/></strong></h2></th></tr></tbody></table></div><p>To make Savu available in a Linux session, execute:</p><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b>Linux command</div><div class="codeContent panelContent pdl">
    <pre class="syntaxhighlighter-pre" data-syntaxhighlighter-params="brush: java; gutter: false; theme: Confluence" data-theme="Confluence">module load savu</pre>
    </div></div><p></p><p>To make Savu Configurator available in a Linux session, execute:</p><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b>Linux command</b></div><div class="codeContent panelContent pdl">
    <pre class="syntaxhighlighter-pre" data-syntaxhighlighter-params="brush: java; gutter: false; theme: Confluence" data-theme="Confluence">module load savu
    savu_config</pre>
    </div></div><p></p><p>Any savu_mpi jobs are run on the new compute cluster, named hamilton (after <a class="external-link" href="https://en.wikipedia.org/wiki/Margaret_Hamilton_(software_engineer)" rel="nofollow">Margaret Hamilton</a>), and can be monitored by executing:</p><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b>Linux command</b></div><div class="codeContent panelContent pdl">
    <pre class="syntaxhighlighter-pre" data-syntaxhighlighter-params="brush: java; gutter: false; theme: Confluence" data-theme="Confluence">module load hamilton
    qstat</pre>
    </div></div><p>(note lower-case hamilton).</p><p></p><p></p><div class="table-wrap"><table class="wrapped confluenceTable"><colgroup><col/></colgroup><tbody><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow"><h2 id="ReconstructionfromimagedataintheHDFformat:Savu-notesonstandarduse-Suggestedprocessestoincludeinaprocesslistfortomographyreconstruction"><strong>Suggested processes to include in a process list for tomography reconstruction</strong></h2></th></tr></tbody></table></div><p></p><p>A typical <strong>Savu process list</strong> in DLS may contain all or most of the following processes in its linear chain of operations (ordered in a similar way to that indicated below):</p><p><br/></p><div class="table-wrap"><table class="wrapped relative-table confluenceTable" style="width: 98.7261%;"><colgroup><col style="width: 5.04695%;"/><col style="width: 12.5%;"/><col style="width: 6.8662%;"/><col style="width: 14.3691%;"/><col style="width: 48.8938%;"/><col style="width: 12.3239%;"/></colgroup><tbody><tr><th style="text-align: center;" class="confluenceTh">Process position</th><th style="text-align: center;" class="confluenceTh">Process name</th><th colspan="1" style="text-align: center;" class="confluenceTh">Process category</th><th style="text-align: center;" class="confluenceTh">Brief description of process</th><th colspan="1" style="text-align: center;" class="confluenceTh">Comment(s)</th><th colspan="1" style="text-align: center;" class="confluenceTh">Common alternative or more suitable process(es)<span style="color: rgb(255,0,0);"><sup>*</sup></span></th></tr><tr><td class="confluenceTd">1</td><td class="confluenceTd"><strong><a href="NxtomoLoader_76391471.html">NxtomoLoader</a></strong></td><td colspan="1" class="confluenceTd">loader</td><td class="confluenceTd">To specify the location of raw dataset(s) to be used as input.</td><td colspan="1" class="confluenceTd"><ol><li>Enables one to specify the location of <em>dark</em>- and <em>flat-field</em> datasets for use by any subsequent process that requires this information (e. g. <strong>DarkFlatFieldCorrection</strong> or <strong>Dezinger</strong>).</li><li>Capable of handling the case of <em>dark</em>- and <em>flat-field</em> images being supplied in individual NeXus datasets.</li><li>Expects its image-data input to be integer-valued.</li></ol></td><td colspan="1" class="confluenceTd"><ol><li><strong>ImageLoader</strong></li><li><strong>Hdf5TemplateLoader</strong></li><li><strong>SavuNexusLoader</strong></li></ol></td></tr><tr><td class="confluenceTd">2</td><td class="confluenceTd"><strong><a href="Dezinger_76392334.html">Dezinger</a></strong></td><td colspan="1" class="confluenceTd">filter</td><td class="confluenceTd">To remove <em>zingers</em> from raw data.</td><td colspan="1" class="confluenceTd"><ol><li>Current implementation of <strong>Dezinger</strong> expects its image-data input to be integer-valued.</li><li>Outputs data in the floating-point format.</li></ol></td><td colspan="1" class="confluenceTd"><ol><li><strong><a href="DezingerSinogram_83739364.html">DezingerSinogram</a></strong></li><li><strong>DezingerSimple</strong></li></ol></td></tr><tr><td colspan="1" class="confluenceTd">3</td><td colspan="1" class="confluenceTd"><strong><a href="DarkFlatFieldCorrection_76392109.html">DarkFlatFieldCorrection</a></strong></td><td colspan="1" class="confluenceTd">corrector</td><td colspan="1" class="confluenceTd">To apply the standard <em>dark</em>-and-<em>flat-field</em> normalisation to sample projections.</td><td colspan="1" class="confluenceTd"><ol><li>Applies: (<em>projection</em> - <em>dark</em>) / (<em>flat</em> - <em>dark</em>), where <em>dark</em> and <em>flat</em> stand for the averaged <em>dark</em>- and <em>flat</em>-<em>field</em> images, respectively.</li><li>Outputs data in the floating-point format.</li><li>Needs to be explicitly included in every process list that seeks this correction (specifying the location of <em>dark</em>- and <em>flat-field</em> data in a loader, e. g. <strong>NxtomoLoader</strong>, is insufficient in this respect). </li></ol></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">4</td><td colspan="1" class="confluenceTd"><strong><a href="DistortionCorrection_76391482.html">DistortionCorrection</a></strong></td><td colspan="1" class="confluenceTd">corrector</td><td colspan="1" class="confluenceTd">To correct data for lens distortion.</td><td colspan="1" class="confluenceTd"><ol><li>Requires information about the centre and coefficients of distortion, which need to be measured beforehand.</li><li>Expects its image-data input to be in the floating-point format (generated, for example, by <strong>Dezinger</strong> or <strong>DarkFlatFieldCorrection</strong>).</li><li>As this correction involves some intensity interpolation, it can result in some smoothing effects which can improve many undesirable artefacts, including ring artefacts.</li></ol></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">5</td><td colspan="1" class="confluenceTd"><strong><a href="CcpiRingArtefactFilter_76392246.html">CcpiRingArtefactFilter</a></strong></td><td colspan="1" class="confluenceTd">filter</td><td colspan="1" class="confluenceTd">To suppress ring artefacts.</td><td colspan="1" class="confluenceTd"><strong>CcpiRingArtefactFilter</strong> is positioned before <strong>PaganinFilter</strong> as it tends to be efficient at suppressing ring artefacts found in typical datasets, but appears to be somewhat less successful on diffused images (which can occasionally be produced by<strong> PaganinFilter</strong>).</td><td colspan="1" class="confluenceTd"><ol><li><strong>RemoveAllRings</strong></li><li><strong><a href="RingRemovalWaveletfft_76392751.html">RingRemovalWaveletfft</a></strong></li></ol></td></tr><tr><td colspan="1" class="confluenceTd">6</td><td colspan="1" class="confluenceTd"><strong><a href="VoCentering_76392254.html">VoCentering</a></strong></td><td colspan="1" class="confluenceTd">filter</td><td colspan="1" class="confluenceTd">To find an optimal value of <em>CoR</em> automatically.</td><td colspan="1" class="confluenceTd">It may be prudent to test the outcome of <span><strong>VoCentering</strong></span> on a small, representative subset of data (use the <strong><em>preview</em></strong> parameter) before embarking on the reconstruction of the entire dataset, using the automatically-determined value of <em>CoR</em>.</td><td colspan="1" class="confluenceTd"><strong>VoCenteringIterative</strong></td></tr><tr><td colspan="1" class="confluenceTd">7</td><td colspan="1" class="confluenceTd"><strong><a href="PaganinFilter_76392338.html">PaganinFilter</a></strong></td><td colspan="1" class="confluenceTd">filter</td><td colspan="1" class="confluenceTd">To retrieve the phase-contrast information.</td><td colspan="1" class="confluenceTd"><ol><li>If the output images from <strong>PaganinFilter</strong> are reasonably free from <span>the halo and shade-off artefacts, then it may be preferable to apply <strong>VoCentering </strong>immediately after this filter (rather than before it).  </span></li><li><span>Since <strong>PaganinFilter</strong> is essentially a special low-pass filter, its application results in some smoothing effects which can improve many undesirable artefacts, including ring artefacts. In view of this, it may be preferable to apply this filter before applying any dedicated ring-suppression process(es).     <br/></span></li></ol></td><td colspan="1" class="confluenceTd"><strong>FresnelFilter</strong></td></tr><tr><td colspan="1" class="confluenceTd">8</td><td colspan="1" class="confluenceTd"><strong><a href="RavenFilter_76392306.html">RavenFilter</a></strong></td><td colspan="1" class="confluenceTd">filter</td><td colspan="1" class="confluenceTd">To suppress ring artefacts.</td><td colspan="1" class="confluenceTd"><strong>RavenFilter</strong> may complementarily be used after<strong> <strong>PaganinFilter</strong></strong> as it can lead to an additional reduction of ring artefacts in somewhat diffused images that can occasionally be produced by <strong>PaganinFilter</strong>.</td><td colspan="1" class="confluenceTd"><strong><a href="RingRemovalWaveletfft_76392751.html">RingRemovalWaveletfft</a></strong></td></tr><tr><td colspan="1" class="confluenceTd">9</td><td colspan="1" class="confluenceTd"><strong><a href="AstraReconGpu_76392313.html">AstraReconGpu</a></strong></td><td colspan="1" class="confluenceTd">reconstructor</td><td colspan="1" class="confluenceTd">To reconstruct normalised and conditioned data.</td><td colspan="1" class="confluenceTd"><br/></td><td colspan="1" class="confluenceTd"><ol><li><strong><a href="AstraReconCpu_76392346.html">AstraReconCpu</a></strong></li><li><strong><a href="TomopyRecon_76392350.html">TomopyRecon</a></strong></li><li><strong><span class="plugin_pagetree_children_span"><a href="https://confluence.diamond.ac.uk/display/TOMTE/TomobarRecon?src=contextnavpagetreemode" rel="nofollow">TomobarRecon</a></span></strong></li></ol></td></tr><tr><td colspan="1" class="confluenceTd">10</td><td colspan="1" class="confluenceTd"><strong><a href="Hdf5saver_76391477.html">Hdf5saver</a></strong></td><td colspan="1" class="confluenceTd">saver</td><td colspan="1" class="confluenceTd">To save reconstruction(s) to output file(s).</td><td colspan="1" class="confluenceTd">By default, <strong>Hdf5saver</strong> is the final process in every process list (hence there is normally no need to add it explicitly).</td><td colspan="1" class="confluenceTd"><strong>TiffSaver</strong></td></tr></tbody></table></div><p><span style="color: rgb(255,0,0);">*</span> Note that, when a process is replaced in a given process list by an alternative process, the latter may need to be included at a different position to that of the original process. For example, <strong><a href="DezingerSinogram_83739364.html">DezingerSinogram</a></strong> needs be included after <strong><a href="DarkFlatFieldCorrection_76392109.html">DarkFlatFieldCorrection</a></strong> while <strong><a href="Dezinger_76392334.html">Dezinger</a> </strong>needs to be included before it.        </p><p><br/></p><div class="table-wrap"><table class="wrapped confluenceTable"><colgroup><col/></colgroup><tbody><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow"><h2 id="ReconstructionfromimagedataintheHDFformat:Savu-notesonstandarduse-Examples"><strong>Examples</strong></h2></th></tr></tbody></table></div><p></p><p></p><div class="confluence-information-macro has-no-icon confluence-information-macro-tip"><div class="confluence-information-macro-body"><div class="table-wrap"><table class="wrapped confluenceTable"><colgroup><col/></colgroup><tbody><tr><th class="highlight-red confluenceTh" data-highlight-colour="red"><h3 id="ReconstructionfromimagedataintheHDFformat:Savu-notesonstandarduse-Example1:SimpleprocesslistincludingVoCentering"><strong>Example 1: Simple process list including <strong>VoCentering</strong><br/></strong></h3></th></tr></tbody></table></div><div id="expander-595148637" class="expand-container"><div id="expander-control-595148637" class="expand-control"><span class="expand-icon aui-icon aui-icon-small aui-iconfont-chevron-down"></span><span class="expand-control-text">Example 1: Process-list description (click to expand)...</span></div><div id="expander-content-595148637" class="expand-content"><div class="table-wrap"><table class="relative-table wrapped confluenceTable" style="width: 99.4075%;"><colgroup><col style="width: 2.29358%;"/><col style="width: 8.11927%;"/><col style="width: 12.7018%;"/><col style="width: 36.1774%;"/><col style="width: 9.35474%;"/><col style="width: 10.1797%;"/><col style="width: 21.1842%;"/></colgroup><tbody><tr><th style="text-align: center;" class="confluenceTh">Process position</th><th style="text-align: center;" class="confluenceTh">Process name</th><th style="text-align: center;" class="confluenceTh">Process parameters</th><th colspan="1" style="text-align: center;" class="confluenceTh">Desired outcome</th><th colspan="1" style="text-align: center;" class="confluenceTh">Shape of input image dataset</th><th colspan="1" style="text-align: center;" class="confluenceTh">Shape of output image dataset</th><th colspan="1" style="text-align: center;" class="confluenceTh">Comment(s)</th></tr><tr><td class="confluenceTd">1</td><td class="confluenceTd"><strong>NxtomoLoader</strong></td><td class="confluenceTd"><ol><li>with non-default setting for the <strong><em>preview</em></strong> parameter;</li><li>all other parameters at default settings</li></ol></td><td colspan="1" class="confluenceTd">To load a particular <span style="color: rgb(128,0,0);">5</span>-slice subset of the entire source dataset (found at the default location in the input NeXus scan file), representing <span style="color: rgb(128,0,0);">5</span> consecutive <em>sinograms</em> corresponding to tomography slices with indices from <span style="color: rgb(128,0,0);">1093</span> to <span style="color: rgb(128,0,0);">1097</span> (see 1.<em><strong>preview</strong></em>).</td><td colspan="1" class="confluenceTd">(Z, img_L, img_W)</td><td colspan="1" class="confluenceTd">(Z,<span style="color: rgb(128,0,0);"> 5</span>, img_W)</td><td colspan="1" class="confluenceTd">For example, (img_L, img_W) = (2160, 2560) for full-size images recorded by PCO Edge camera, hence the slice located at height <span style="color: rgb(128,0,0);">1093 </span>lies approximately in the middle. These images contain 16-bit unsigned-integer data.</td></tr><tr><td class="confluenceTd"> 2</td><td class="confluenceTd"><strong>Dezinger</strong></td><td class="confluenceTd">at default settings</td><td colspan="1" class="confluenceTd">To remove <em>zingers </em>from the <span style="color: rgb(128,0,0);">5</span><em>-sinogram</em> subset previously loaded in Process 1.</td><td colspan="1" class="confluenceTd">(Z, <span style="color: rgb(128,0,0);">5</span>, img_W)</td><td colspan="1" class="confluenceTd">(Z, <span style="color: rgb(128,0,0);">5</span>, img_W)</td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td class="confluenceTd">3</td><td class="confluenceTd"><strong>DarkFlatFieldCorrection</strong></td><td class="confluenceTd">at default settings</td><td colspan="1" class="confluenceTd">To apply the standard <em>dark</em>-and-<em>flat-field</em> normalisation to each of the <span style="color: rgb(128,0,0);">5</span> <em>sinograms</em> loaded in Process 1 (using the <em>dark-</em> and <em>flat-field</em> data found at the default locations in the input NeXus scan file).</td><td colspan="1" class="confluenceTd">(Z, <span style="color: rgb(128,0,0);">5</span>, img_W)</td><td colspan="1" class="confluenceTd">(Z, <span style="color: rgb(128,0,0);">5</span>, img_W)</td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">4</td><td colspan="1" class="confluenceTd"><strong>CcpiRingArtefactFilter</strong></td><td colspan="1" class="confluenceTd"><p>at default settings</p></td><td colspan="1" class="confluenceTd">To suppress ring artefacts in each of the <span style="color: rgb(128,0,0);">5</span> <em>sinograms</em> loaded by Process 1.</td><td colspan="1" class="confluenceTd">(Z, <span style="color: rgb(128,0,0);">5</span>, img_W)</td><td colspan="1" class="confluenceTd">(Z, <span style="color: rgb(128,0,0);">5</span>, img_W)</td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">5</td><td colspan="1" class="confluenceTd"><strong>VoCentering</strong></td><td colspan="1" class="confluenceTd"><p>at default settings</p></td><td colspan="1" class="confluenceTd"><ol><li>To find an optimal value of <em>CoR</em> for each of the first <span style="color: rgb(128,0,0);">3</span> <em>sinograms</em> from the <span style="color: rgb(128,0,0);">5</span>-<em>sinogram</em> subset loaded in Process 1;</li><li style="color: rgb(0,0,0);">To select a common optimal value of <em>CoR</em> from the above <span style="color: rgb(128,0,0);">3<span style="color: rgb(0,0,0);"> (potentially different) values of</span> <span style="color: rgb(0,0,0);"><em>CoR</em></span></span><em>,</em> with the view of applying it to reconstruct all, or any subset, of the <span style="color: rgb(128,0,0);">5<em>-</em></span><em>sinogram </em>subset loaded in Process 1.</li></ol></td><td colspan="1" class="confluenceTd">(Z, <span style="color: rgb(128,0,0);">5</span>, img_W)</td><td colspan="1" class="confluenceTd">n/a</td><td colspan="1" class="confluenceTd">Note that the <em><strong>preview</strong></em> parameter of this <strong>VoCentering</strong> process selects the first <span style="color: rgb(128,0,0);">3</span> array slices (indexed <span style="color: rgb(128,0,0);">0</span>, <span style="color: rgb(128,0,0);">1</span> and <span style="color: rgb(128,0,0);">2</span>) in the 2-nd dimension (axis=1), which correspond to the middle <span style="color: rgb(128,0,0);">3</span> array slices (in the same dimension) with indices <span style="color: rgb(128,0,0);">1093</span><span style="color: rgb(0,0,0);">,</span> <span style="color: rgb(128,0,0);">1094<span style="color: rgb(0,0,0);">,</span></span> <span style="color: rgb(128,0,0);">1095<span style="color: rgb(0,0,0);"> in the</span> </span>entire source dataset.</td></tr><tr><td colspan="1" class="confluenceTd">6</td><td colspan="1" class="confluenceTd"><strong>AstraReconGpu</strong></td><td colspan="1" class="confluenceTd">at default settings</td><td colspan="1" style="color: rgb(0,0,0);" class="confluenceTd">To reconstruct the <span style="color: rgb(128,0,0);">5 </span><em>sinograms</em> loaded in Process 1 with the common optimal value of <em>CoR</em> determined by Process 5 (part 2).</td><td colspan="1" class="confluenceTd">(Z, <span style="color: rgb(128,0,0);">5</span>, img_W)</td><td colspan="1" class="confluenceTd">(img_W, <span style="color: rgb(128,0,0);">5</span><span style="color: rgb(0,51,102);">,</span> img_W)</td><td colspan="1" class="confluenceTd">Note that this <strong>AstraReconGpu</strong> will automatically receive the value of <em>CoR</em> determined by the <strong>VoCentering</strong> in Process 5, so it is harmless to leave the <em><strong>centre_of_rotation</strong></em> parameter of this <strong>AstraReconGpu</strong> at its default value of 0.0.</td></tr><tr><td colspan="1" class="confluenceTd">7</td><td colspan="1" class="confluenceTd"><strong>Hdf5saver</strong></td><td colspan="1" class="confluenceTd">at default settings</td><td colspan="1" class="confluenceTd">To save the <span style="color: rgb(128,0,0);">5</span> reconstructed tomography slices as a single 3d dataset in the output HDF5 file.</td><td colspan="1" class="confluenceTd">(img_W, <span style="color: rgb(128,0,0);">5</span>, img_W)</td><td colspan="1" class="confluenceTd">(img_W, <span style="color: rgb(128,0,0);">5</span>, img_W)</td><td colspan="1" class="confluenceTd">This process is <strong>implicit</strong>.</td></tr></tbody></table></div></div></div><div class="code panel pdl" style="border-width: 1px;">
     <div class="codeHeader panelHeader pdl hide-border-bottom" style="border-bottom-width: 1px;">
      <b class="code-title"></b>
      <span class="collapse-source expand-control" style="display:none;"><span class="expand-control-icon icon">&nbsp;</span><span class="expand-control-text">Expand source</span></span>
      <span class="collapse-spinner-wrapper"></span>
     </div>
     <div class="codeContent panelContent pdl hide-toolbar">

Example 1: Process list in Savu Configurator

.. code-block:: none

    >>> disp -a

    -------------------------------------------------------------------------------------
     1) NxtomoLoader
        1)                preview : [:, 1093:1098, :]
        2)         image_key_path : entry1/tomo_entry/instrument/detector/image_key
        3)                   name : tomo
        4)               3d_to_4d : False
        5)                   flat : [None, None, 1]
        6)              data_path : entry1/tomo_entry/data/data
        7)                   dark : [None, None, 1]
        8)                 angles : None
        9)           ignore_flats : None
    -------------------------------------------------------------------------------------
     2) Dezinger
        1)            in_datasets : []
        2)           out_datasets : []
        3)                   mode : 0
        4)            kernel_size : 5
        5)             outlier_mu : 10.0
    -------------------------------------------------------------------------------------
     3) DarkFlatFieldCorrection
        1)            in_datasets : []
        2)            upper_bound : None
        3)           out_datasets : []
        4)            lower_bound : None
        5)                pattern : PROJECTION
        6)        warn_proportion : 0.05
    -------------------------------------------------------------------------------------
     4) CcpiRingArtefactFilter
        1)             num_series : 1
        2)                param_r : 0.005
        3)            in_datasets : []To load a particular 5-slice subset of the entire source dataset (found at the default location in the input NeXus scan file), representing 5 consecutive sinograms corresponding to tomography slices with indices from 1093 to 1097 (see 1.preview).
        4)           out_datasets : []
        5)                param_n : 0
    -------------------------------------------------------------------------------------
     5) VoCentering
        1)                preview : [:, 0:3, :]
        2)            start_pixel : None
        3)            search_area : [-50, 50]
        4)            in_datasets : []
        5)          search_radius : 6
        6)                  ratio : 0.5
        7)           out_datasets : ['cor_raw', 'cor_fit']
        8)   datasets_to_populate : []
        9)               row_drop : 20
       10)                   step : 0.5
    -------------------------------------------------------------------------------------
     6) AstraReconGpu
        1)               init_vol : None
        2)                preview : []
        3)                    log : True
        4)              algorithm : FBP_CUDA
        5)           n_iterations : 1
        6)               res_norm : False
        7)     centre_of_rotation : 0.0
        8)             FBP_filter : ram-lak
        9)            in_datasets : []
       10)                  ratio : 0.95
       11)           out_datasets : []
       12)             centre_pad : False
       13)              outer_pad : False
       14)             force_zero : [None, None]
    -------------------------------------------------------------------------------------

.. raw:: html

     </div>
    </div><p><br/></p><h4 id="ReconstructionfromimagedataintheHDFformat:Savu-notesonstandarduse-WheretolookfortheoptimalvalueofCoRdeterminedbyVoCentering?"><strong>Where to look for the optimal value of CoR determined by VoCentering?<br/></strong></h4><ul><li>To find out which pixel coordinate was actually selected by <strong>VoCentering</strong> for setting the <strong><em>centre_of_rotation</em></strong> parameter of a subsequent reconstruction process, inspect a dataset located at <strong>/entry/final_result_tomo/meta_data/centre_of_rotation/centre_of_rotation</strong> in the primary output file, named <strong>&lt;<em><span style="color: rgb(255,102,0);">scan-number</span></em>&gt;_processed.nxs</strong>. Alternatively, see a dataset located at <strong>/&lt;<em><span style="color: rgb(255,102,0);">position-in-process-list</span></em>&gt;-VoCentering-cor_broadcast/data</strong> in the intermediate output file named <strong>cor_broadcast_p&lt;<em><span style="color: rgb(255,102,0);">position-in-process-list</span></em>&gt;_vo_centering.h5</strong>.</li><li>Incidentally, a dataset located at <strong>/entry/final_result_tomo/meta_data/cor_preview/cor_preview </strong>in the primary output file contains all (not-necessarily identical) values of <em>CoR</em> determined by <strong>VoCentering</strong> individually for each <em>sinogram</em> specified by the <em><strong>preview</strong></em> parameter of this process. Alternatively, a dataset located at <strong>/&lt;<em><span style="color: rgb(255,102,0);">position-in-process-list</span></em>&gt;-VoCentering-cor_preview/data</strong> in the intermediate output file <strong>cor_preview_p&lt;<em><span style="color: rgb(255,102,0);">position-in-process-list</span></em>&gt;_vo_centering.h5</strong> contains the same information.</li></ul></div></div><p><br/></p><p><br/></p><div class="confluence-information-macro has-no-icon confluence-information-macro-tip"><div class="confluence-information-macro-body"><div class="table-wrap"><table class="wrapped confluenceTable"><colgroup><col/></colgroup><tbody><tr><th class="highlight-red confluenceTh" data-highlight-colour="red"><h3 id="ReconstructionfromimagedataintheHDFformat:Savu-notesonstandarduse-Example2:MoreadvancedprocesslistincludingVoCentering"><strong>Example 2: More advanced process list including <strong>VoCentering</strong></strong></h3></th></tr></tbody></table></div><div id="expander-81129995" class="expand-container"><div id="expander-control-81129995" class="expand-control"><span class="expand-icon aui-icon aui-icon-small aui-iconfont-chevron-down"></span><span class="expand-control-text">Example 2: Process-list description (click to expand)...</span></div><div id="expander-content-81129995" class="expand-content"><p><strong><br/></strong></p><div class="table-wrap"><table class="relative-table wrapped confluenceTable" style="width: 99.4075%;"><colgroup><col style="width: 2.29358%;"/><col style="width: 8.11927%;"/><col style="width: 12.7018%;"/><col style="width: 36.1774%;"/><col style="width: 9.35474%;"/><col style="width: 10.1797%;"/><col style="width: 21.1842%;"/></colgroup><tbody><tr><th style="text-align: center;" class="confluenceTh">Process position</th><th style="text-align: center;" class="confluenceTh">Process name</th><th style="text-align: center;" class="confluenceTh">Process parameters</th><th colspan="1" style="text-align: center;" class="confluenceTh">Desired outcome</th><th colspan="1" style="text-align: center;" class="confluenceTh">Shape of input image dataset</th><th colspan="1" style="text-align: center;" class="confluenceTh">Shape of output image dataset</th><th colspan="1" style="text-align: center;" class="confluenceTh">Comment(s)</th></tr><tr><td class="confluenceTd">1</td><td class="confluenceTd"><strong>NxtomoLoader</strong></td><td class="confluenceTd"><ol><li>with non-default setting for the <strong><em>preview</em></strong> parameter;</li><li>all other parameters at default settings</li></ol></td><td colspan="1" class="confluenceTd"><p>To load a particular <span style="color: rgb(128,0,0);">5</span>-slice subset of the entire source dataset (found at the default location in the input NeXus scan file), representing <span style="color: rgb(128,0,0);">5</span> consecutive <em>sinograms</em> corresponding to tomography slices with indices from <span style="color: rgb(128,0,0);">1093</span> to <span style="color: rgb(128,0,0);">1097</span> (see 1.<em><strong>preview</strong></em>).</p></td><td colspan="1" class="confluenceTd">(Z, img_L, img_W)</td><td colspan="1" class="confluenceTd">(Z,<span style="color: rgb(128,0,0);"> 5</span>, img_W)</td><td colspan="1" class="confluenceTd">For example, (img_L, img_W) = (2160, 2560) for full-size images recorded by PCO Edge camera, hence the slice located at height <span style="color: rgb(128,0,0);">1093 </span>lies approximately in the middle. These images contain 16-bit unsigned-integer data.</td></tr><tr><td class="confluenceTd">2</td><td class="confluenceTd"><strong>Dezinger</strong></td><td class="confluenceTd">at default settings</td><td colspan="1" class="confluenceTd">To remove <em>zingers </em>from the <span style="color: rgb(128,0,0);">5</span><em>-sinogram</em> subset previously loaded in Process 1.</td><td colspan="1" class="confluenceTd">(Z, <span style="color: rgb(128,0,0);">5</span>, img_W)</td><td colspan="1" class="confluenceTd">(Z, <span style="color: rgb(128,0,0);">5</span>, img_W)</td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td class="confluenceTd">3</td><td class="confluenceTd"><strong>DarkFlatFieldCorrection</strong></td><td class="confluenceTd">at default settings</td><td colspan="1" class="confluenceTd">To apply the standard <em>dark</em>-and-<em>flat-field</em> normalisation to each of the <span style="color: rgb(128,0,0);">5</span> <em>sinograms</em> loaded in Process 1 (using the <em>dark-</em> and <em>flat-field</em> data found at the default locations in the input NeXus scan file).</td><td colspan="1" class="confluenceTd">(Z, <span style="color: rgb(128,0,0);">5</span>, img_W)</td><td colspan="1" class="confluenceTd">(Z, <span style="color: rgb(128,0,0);">5</span>, img_W)</td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">4</td><td colspan="1" class="confluenceTd"><strong>CcpiRingArtefactFilter</strong></td><td colspan="1" class="confluenceTd"><ol><li>with <strong>parameter tuning</strong> being applied on the <em><strong>param_r</strong></em> parameter;</li><li>all other parameters at default settings</li></ol></td><td colspan="1" class="confluenceTd">To suppress ring artefacts in each of the <span style="color: rgb(128,0,0);">5</span> <em>sinograms</em> loaded in Process 1, using the following <span style="color: rgb(128,0,0);">7</span> tuning values for <em><strong>param_r</strong></em>: <span style="color: rgb(128,0,0);">0.5</span>, <span style="color: rgb(128,0,0);">0.05</span>, 0.005 (default), <span style="color: rgb(128,0,0);">0.0005, <span style="color: rgb(128,0,0);">0.0001, <span style="color: rgb(128,0,0);">0.01<span style="color: rgb(0,0,0);">, and</span> <span style="color: rgb(128,0,0);">0.001</span></span></span></span>.from the <span style="color: rgb(128,0,0);">5</span>-<em>sinogram</em> subset loaded in Process 1;</td><td colspan="1" class="confluenceTd">(Z, <span style="color: rgb(128,0,0);">5</span>, img_W)</td><td colspan="1" class="confluenceTd">(Z, <span style="color: rgb(128,0,0);">5</span>, img_W, <span style="color: rgb(128,0,0);">7</span>)</td><td colspan="1" class="confluenceTd">Note that the parameter tuning performed on the <em><strong>param_r</strong></em> of this <strong>CcpiRingArtefactFilter</strong> adds an extra (<span style="color: rgb(128,0,0);">4</span>-th) dimension to the original image dataset.</td></tr><tr><td colspan="1" class="confluenceTd">5</td><td colspan="1" class="confluenceTd"><strong>VoCentering</strong></td><td colspan="1" class="confluenceTd"><ol><li>with non-default setting for the <strong><em>preview</em></strong> parameter;</li><li>all other parameters at default settings</li></ol></td><td colspan="1" class="confluenceTd"><ol><li>To find an optimal value of <em>CoR</em> for each of the first <span style="color: rgb(128,0,0);">3</span> <em>sinograms</em> (of the <span style="color: rgb(128,0,0);">5</span>-<em>sinogram</em> subset loaded in Process 1) that were subsequently processed by Process 4 using the <span style="color: rgb(128,0,0);">2</span>nd (index <span style="color: rgb(128,0,0);">1</span>) value of <em><strong>param_r</strong></em>, i. e. <em><strong>param_r</strong></em> = <span style="color: rgb(128,0,0);">0.05 <span style="color: rgb(0,0,0);">(see 5.<em><strong>preview</strong></em>)</span></span>;</li><li>To select a common optimal value of <em>CoR</em> from the above <span style="color: rgb(128,0,0);">3<span style="color: rgb(0,0,0);"> (potentially different) values of</span> <span style="color: rgb(0,0,0);"><em>CoR</em></span></span><em>,</em> with the view of applying it to reconstruct all, or any subset, of the <span style="color: rgb(128,0,0);">35 <span style="color: rgb(0,0,0);">(=</span><span style="color: rgb(128,0,0);">5*7</span><span style="color: rgb(0,0,0);">)</span></span> parameter–tuned<em> sinograms</em> that are currently available for reconstruction in the pipeline.</li></ol></td><td colspan="1" class="confluenceTd">(Z, <span style="color: rgb(128,0,0);">5</span>, img_W, <span style="color: rgb(128,0,0);">1</span>)</td><td colspan="1" class="confluenceTd">n/a</td><td colspan="1" class="confluenceTd">Note that the <em><strong>preview</strong></em> parameter of this <strong>VoCentering</strong> process selects the first <span style="color: rgb(128,0,0);">3</span> array slices (indexed <span style="color: rgb(128,0,0);">0</span>, <span style="color: rgb(128,0,0);">1</span> and <span style="color: rgb(128,0,0);">2</span>) in the 2-nd dimension (axis=1), which correspond to the middle <span style="color: rgb(128,0,0);">3</span> array slices (in the same dimension) with indices <span style="color: rgb(128,0,0);">1093</span><span style="color: rgb(0,0,0);">,</span> <span style="color: rgb(128,0,0);">1094<span style="color: rgb(0,0,0);">,</span></span> <span style="color: rgb(128,0,0);">1095<span style="color: rgb(0,0,0);"> in the</span> </span>entire source dataset.</td></tr><tr><td colspan="1" class="confluenceTd">6</td><td colspan="1" class="confluenceTd"><strong>AstraReconGpu</strong></td><td colspan="1" class="confluenceTd">at default settings</td><td colspan="1" class="confluenceTd">To reconstruct all the <span style="color: rgb(128,0,0);">35 <span style="color: rgb(0,0,0);">(=</span><span style="color: rgb(128,0,0);">5*7</span><span style="color: rgb(0,0,0);">)</span></span> parameter–tuned <em>sinograms</em> with the common optimal value of <em>CoR</em> determined by Process 5 (part 2).</td><td colspan="1" class="confluenceTd">(Z, <span style="color: rgb(128,0,0);">5</span>, img_W, <span style="color: rgb(128,0,0);">7</span>)</td><td colspan="1" class="confluenceTd">(img_W, <span style="color: rgb(128,0,0);">5</span>, img_W, <span style="color: rgb(128,0,0);">7</span>)</td><td colspan="1" class="confluenceTd">Note that this <strong>AstraReconGpu</strong> will automatically receive the value of <em>CoR</em> determined by the <strong>VoCentering</strong> in Process 5, so it is harmless to leave the <em><strong>centre_of_rotation</strong></em> parameter of this <strong>AstraReconGpu</strong> at its default value of 0.0.</td></tr><tr><td colspan="1" class="confluenceTd">7</td><td colspan="1" class="confluenceTd"><strong>Hdf5saver</strong></td><td colspan="1" class="confluenceTd">at default settings</td><td colspan="1" class="confluenceTd">To save all the <span style="color: rgb(128,0,0);">35</span> (=<span style="color: rgb(128,0,0);">5*7</span>) reconstructed tomography slices as a single 4d dataset in the output HDF5 file.</td><td colspan="1" class="confluenceTd">(img_W, <span style="color: rgb(128,0,0);">5</span>, img_W, <span style="color: rgb(128,0,0);">7</span>)</td><td colspan="1" class="confluenceTd">(img_W, <span style="color: rgb(128,0,0);">5</span>, img_W, <span style="color: rgb(128,0,0);">7</span>)</td><td colspan="1" class="confluenceTd">This process is <strong>implicit</strong>.</td></tr></tbody></table></div></div></div><div class="code panel pdl" style="border-width: 1px;">
     <div class="codeHeader panelHeader pdl hide-border-bottom" style="border-bottom-width: 1px;">
      <b class="code-title"></b>
      <span class="collapse-source expand-control" style="display:none;"><span class="expand-control-icon icon">&nbsp;</span><span class="expand-control-text">Expand source</span></span>
      <span class="collapse-spinner-wrapper"></span>
     </div>
     <div class="codeContent panelContent pdl hide-toolbar">

Example 2: Process list in Savu Configurator

.. code-block:: none

    >>> disp -a

    -------------------------------------------------------------------------------------
     1) NxtomoLoader
        1)                preview : [:, 1093:1098, :]
        2)         image_key_path : entry1/tomo_entry/instrument/detector/image_key
        3)                   name : tomo
        4)               3d_to_4d : False
        5)                   flat : [None, None, 1]
        6)              data_path : entry1/tomo_entry/data/data
        7)                   dark : [None, None, 1]
        8)                 angles : None
        9)           ignore_flats : None
    -------------------------------------------------------------------------------------
     2) Dezinger
        1)            in_datasets : []
        2)           out_datasets : []
        3)                   mode : 0
        4)            kernel_size : 5
        5)             outlier_mu : 10.0
    -------------------------------------------------------------------------------------
     3) DarkFlatFieldCorrection
        1)            in_datasets : []
        2)            upper_bound : None
        3)           out_datasets : []
        4)            lower_bound : None
        5)                pattern : PROJECTION
        6)        warn_proportion : 0.05
    -------------------------------------------------------------------------------------
     4) CcpiRingArtefactFilter
        1)             num_series : 1
        2)                param_r : 0.5;0.05;0.005;0.0005;0.0001;0.01;0.001
        3)            in_datasets : []
        4)           out_datasets : []
        5)                param_n : 0
    -------------------------------------------------------------------------------------
     5) VoCentering
        1)                preview : [:, 0:3, :, 1]
        2)            start_pixel : None
        3)            search_area : [-50, 50]
        4)            in_datasets : []
        5)          search_radius : 6
        6)                  ratio : 0.5
        7)           out_datasets : ['cor_raw', 'cor_fit']
        8)   datasets_to_populate : []
        9)               row_drop : 20
       10)                   step : 0.5
    -------------------------------------------------------------------------------------
     6) AstraReconGpu
        1)               init_vol : None
        2)                preview : []
        3)                    log : True
        4)              algorithm : FBP_CUDA
        5)           n_iterations : 1
        6)               res_norm : False
        7)     centre_of_rotation : 0
        8)             FBP_filter : ram-lak
        9)            in_datasets : []
       10)                  ratio : 0.95
       11)           out_datasets : []
       12)             centre_pad : False
       13)              outer_pad : False
       14)             force_zero : [None, None]
    -------------------------------------------------------------------------------------

.. raw:: html

     </div>
    </div></div></div><p><br/></p><p><br/></p><div class="confluence-information-macro has-no-icon confluence-information-macro-tip"><div class="confluence-information-macro-body"><div class="table-wrap"><table class="wrapped confluenceTable"><colgroup><col/></colgroup><tbody><tr><th class="highlight-red confluenceTh" data-highlight-colour="red"><h3 id="ReconstructionfromimagedataintheHDFformat:Savu-notesonstandarduse-Example3:Simpleprocesslistforgeneratingsinograms"><strong>Example 3: Simple process list for generating sinograms</strong></h3></th></tr></tbody></table></div><p><br/></p><p>The process list below provides an example of how to generate 3 sinograms corresponding to 3 middle tomographic cross-sections:</p><div class="code panel pdl" style="border-width: 1px;">
     <div class="codeHeader panelHeader pdl hide-border-bottom" style="border-bottom-width: 1px;">
      <b class="code-title"></b>
      <span class="collapse-source expand-control" style="display:none;"><span class="expand-control-icon icon">&nbsp;</span><span class="expand-control-text">Expand source</span></span>
      <span class="collapse-spinner-wrapper"></span>
     </div>
     <div class="codeContent panelContent pdl hide-toolbar">

Example 3: Process list in Savu Configurator

.. code-block:: none

    >>> disp -a

    -------------------------------------------------------------------------------------
     1) NxtomoLoader
        1)                preview : [:, mid-1:mid+1, :]
        2)         image_key_path : entry1/tomo_entry/instrument/detector/image_key
        3)                   name : sino
        4)               3d_to_4d : False
        5)                   flat : [None, None, 1]
        6)              data_path : entry1/tomo_entry/data/data
        7)                   dark : [None, None, 1]
        8)                 angles : None
        9)           ignore_flats : None
    -------------------------------------------------------------------------------------
     2) DarkFlatFieldCorrection
        1)            in_datasets : []
        2)            upper_bound : None
        3)           out_datasets : []
        4)            lower_bound : None
        5)                pattern : PROJECTION
        6)        warn_proportion : 0.05
    -------------------------------------------------------------------------------------
     3) TiffSaver
        1)            in_datasets : []
        2)                 prefix : None
        3)                pattern : SINOGRAM
    -------------------------------------------------------------------------------------

.. raw:: html

     </div>
    </div></div></div><p><br/></p><p><br/></p><div class="confluence-information-macro has-no-icon confluence-information-macro-tip"><div class="confluence-information-macro-body"><div class="table-wrap"><table class="wrapped confluenceTable"><colgroup><col/></colgroup><tbody><tr><th class="highlight-red confluenceTh" data-highlight-colour="red"><h3 id="ReconstructionfromimagedataintheHDFformat:Savu-notesonstandarduse-Example4a:Simpleprocesslistforgeneratingdark-and-flat-field-correctedradiographyimages"><strong>Example 4a: Simple process list for generating dark-and-flat-field-corrected radiography images<br/></strong></h3></th></tr></tbody></table></div><p><br/></p><p>Note that in the case of radiography the information about image keys or sampling angles is usually not required (and therefore typically absent), and dark- and flat-field images are usually provided in two separate scan or data files, respectively. This scenario is reflected in the example below in which the <em><strong>image_key_path</strong></em> and <em><strong>angles</strong></em> parameters are set to <em>None</em>, and the flat- and dark-field datasets are provided in two separate data files, miro_projections_84122.hdf and miro_projections_84123.hdf, respectively.</p><div class="code panel pdl" style="border-width: 1px;">
     <div class="codeHeader panelHeader pdl hide-border-bottom" style="border-bottom-width: 1px;">
      <b class="code-title"></b>
      <span class="collapse-source expand-control" style="display:none;"><span class="expand-control-icon icon">&nbsp;</span><span class="expand-control-text">Expand source</span></span>
      <span class="collapse-spinner-wrapper"></span>
     </div>
     <div class="codeContent panelContent pdl hide-toolbar">

Example 4a: Process list in Savu Configurator

.. code-block:: none

    >>> disp -a

    -------------------------------------------------------------------------------------
     1) NxtomoLoader
        1)                preview : []
        2)         image_key_path : None
        3)                   name : radiography
        4)               3d_to_4d : False
        5)                   flat : [/dls/i12/data/2019/ee20903-1/rawdata/miro_projections_84122.hdf, entry/data/data, 1]
        6)              data_path : entry/data/data
        7)                   dark : [/dls/i12/data/2019/ee20903-1/rawdata/miro_projections_84123.hdf, entry/data/data, 1]
        8)                 angles : None
        9)           ignore_flats : None
    -------------------------------------------------------------------------------------
     2) DarkFlatFieldCorrection
        1)            in_datasets : []
        2)            upper_bound : None
        3)           out_datasets : []
        4)            lower_bound : None
        5)                pattern : PROJECTION
        6)        warn_proportion : 0.05
    -------------------------------------------------------------------------------------

.. raw:: html

     </div>
    </div><p><br/></p><p><strong><br/></strong></p><div class="table-wrap"><table class="wrapped confluenceTable"><colgroup><col/></colgroup><tbody><tr><th class="highlight-red confluenceTh" data-highlight-colour="red"><h3 id="ReconstructionfromimagedataintheHDFformat:Savu-notesonstandarduse-Example4b:Simpleprocesslistforgeneratingdark-and-flat-field-correctedtomographyrawimages"><strong>Example 4b: Simple process list for generating dark-and-flat-field-corrected tomography raw images<br/></strong></h3></th></tr></tbody></table></div><p><br/></p><p>The process list below provides an example of how to select 3 raw images from the middle of a dataset to generate the correspondong 3 dark-and-flat-field-corrected raw images:</p><div class="code panel pdl" style="border-width: 1px;">
     <div class="codeHeader panelHeader pdl hide-border-bottom" style="border-bottom-width: 1px;">
      <b class="code-title"></b>
      <span class="collapse-source expand-control" style="display:none;"><span class="expand-control-icon icon">&nbsp;</span><span class="expand-control-text">Expand source</span></span>
      <span class="collapse-spinner-wrapper"></span>
     </div>
     <div class="codeContent panelContent pdl hide-toolbar">

Example 4b: Process list in Savu Configurator

.. code-block:: none

    >>> disp -a

    -------------------------------------------------------------------------------------
     1) NxtomoLoader
        1)                preview : [mid:mid+3, :, :]
        2)         image_key_path : entry1/tomo_entry/instrument/detector/image_key
        3)                   name : tomo
        4)               3d_to_4d : False
        5)                   flat : [None, None, 1]
        6)              data_path : entry1/tomo_entry/data/data
        7)                   dark : [None, None, 1]
        8)                 angles : None
        9)           ignore_flats : None
    -------------------------------------------------------------------------------------
     2) DarkFlatFieldCorrection
        1)            in_datasets : []
        2)            upper_bound : None
        3)           out_datasets : []
        4)            lower_bound : None
        5)                pattern : PROJECTION
        6)        warn_proportion : 0.05
    -------------------------------------------------------------------------------------

.. raw:: html

     </div>
    </div></div></div><p><br/></p><p><br/></p><div class="confluence-information-macro has-no-icon confluence-information-macro-tip"><div class="confluence-information-macro-body"><div class="table-wrap"><table class="wrapped confluenceTable"><colgroup><col/></colgroup><tbody><tr><th class="highlight-red confluenceTh" data-highlight-colour="red"><h3 id="ReconstructionfromimagedataintheHDFformat:Savu-notesonstandarduse-Example5:Processlistforoverridinginternalflat-anddark-fieldimageswithexternalones"><strong>Example 5: Process list for overriding internal flat- and dark-field images with external ones<br/></strong></h3></th></tr></tbody></table></div><p><br/></p><p>Similarly to the process list in Example 4a, the flat- and dark-field datasets in this example are provided in two separate scan files, 122639.nxs and 122640.nxs, respectively. Note that the <em><strong>angles</strong></em> parameter is now set to np.linspace(0.0,180.0,1801), which is appropriate for reconstructing a tomography dataset containing exactly 1801 sample projections (taken over the range of 180 deg) and any number of internal flat- and dark-field images. Savu identifies, and then ignores, these internal flat- and dark-field images using the information provided by the <em><strong>image_key_path</strong></em> parameter, which therefore needs to be specified. This type of process list is useful if the internal flat- or dark-field images are in some way defective.</p><div class="code panel pdl" style="border-width: 1px;">
     <div class="codeHeader panelHeader pdl hide-border-bottom" style="border-bottom-width: 1px;">
      <b class="code-title"></b>
      <span class="collapse-source expand-control" style="display:none;"><span class="expand-control-icon icon">&nbsp;</span><span class="expand-control-text">Expand source</span></span>
      <span class="collapse-spinner-wrapper"></span>
     </div>
     <div class="codeContent panelContent pdl hide-toolbar">

Example 5: Process list in Savu Configurator

.. code-block:: none

    >>> disp -a

    -------------------------------------------------------------------------------------
     1) NxtomoLoader
        1)                preview : []
        2)         image_key_path : entry1/tomo_entry/instrument/detector/image_key
        3)                   name : tomo
        4)               3d_to_4d : False
        5)                   flat : [/dls/i13/data/2019/mg23980-1/raw/122639.nxs, /entry1/pco1_hw_hdf_nochunking/data, 2]
        6)              data_path : entry1/tomo_entry/data/data
        7)                   dark : [/dls/i13/data/2019/mg23980-1/raw/122640.nxs, /entry1/pco1_hw_hdf_nochunking/data, 2]
        8)                 angles : np.linspace(0.0,180.0,1801)
        9)           ignore_flats : None
    -------------------------------------------------------------------------------------
     2) DarkFlatFieldCorrection
        1)            in_datasets : []
        2)            upper_bound : None
        3)           out_datasets : []
        4)            lower_bound : None
        5)                pattern : PROJECTION
        6)        warn_proportion : 0.05
    -------------------------------------------------------------------------------------
     3) DistortionCorrection
        1)        center_from_top : 1342.27794492
        2)      polynomial_coeffs : [0.9998625936864155, 5.356359274168777e-07, 2.074129717987741e-09, -2.7810309488306555e-13, 5.571390974300683e-17]
        3)       center_from_left : 1072.19611109
        4)              file_path : None
        5)            in_datasets : []
        6)             crop_edges : 20
        7)           out_datasets : []
    -------------------------------------------------------------------------------------
     4) RemoveAllRings
        1)            in_datasets : []
        2)           out_datasets : []
        3)                la_size : 71
        4)                    snr : 3.0
        5)                sm_size : 31
    -------------------------------------------------------------------------------------
     5) AstraReconGpu
        1)               init_vol : None
        2)                preview : []
        3)                    log : True
        4)              algorithm : FBP_CUDA
        5)           n_iterations : 1
        6)               res_norm : False
        7)     centre_of_rotation : 1262
        8)             FBP_filter : ram-lak
        9)            in_datasets : []
       10)                  ratio : 0.95
       11)           out_datasets : []
       12)             centre_pad : True
       13)              outer_pad : True
       14)               log_func : np.nan_to_num(-np.log(sino))
       15)             force_zero : [None, None]
       16)              vol_shape : fixed
    -------------------------------------------------------------------------------------
     6) TiffSaver
        1)            in_datasets : []
        2)                 prefix : None
        3)                pattern : VOLUME_XZ
    -------------------------------------------------------------------------------------

.. raw::html

     </div>
    </div></div></div><p><br/></p><p><br/></p><div class="confluence-information-macro has-no-icon confluence-information-macro-tip"><div class="confluence-information-macro-body"><div class="table-wrap"><table class="wrapped confluenceTable"><colgroup><col/></colgroup><tbody><tr><th class="highlight-red confluenceTh" data-highlight-colour="red"><h3 id="ReconstructionfromimagedataintheHDFformat:Savu-notesonstandarduse-Example6:Simpleprocesslistforapplyinglens-distortioncorrectiontograting-interferometryTIFFimages"><strong>Example 6: Simple process list for applying lens-distortion correction to grating-interferometry TIFF images<br/></strong></h3></th></tr></tbody></table></div><p><br/></p><p>The process list below provides an example of how to apply lens-distortion correction to the entire raw dataset of TIFF images, stored in a single directory (note that in this case one needs to supply a path to the input directory (rather than a path to some NeXus scan file) as the first argument for running the savu_mpi or savu commands):</p><div class="code panel pdl" style="border-width: 1px;">
     <div class="codeHeader panelHeader pdl hide-border-bottom" style="border-bottom-width: 1px;">
      <b class="code-title"></b>
      <span class="collapse-source expand-control" style="display:none;"><span class="expand-control-icon icon">&nbsp;</span><span class="expand-control-text">Expand source</span></span>
      <span class="collapse-spinner-wrapper"></span>
     </div>
     <div class="codeContent panelContent pdl hide-toolbar">

Example 6: Process list in Savu Configurator

.. code-block:: none

    >>> disp -a

    -------------------------------------------------------------------------------------
     1) ImageLoader
        1)                preview : []
        2)            data_prefix : None
        3)            flat_prefix : None
        4)            dark_prefix : None
        5)                 angles : None
        6)              frame_dim : 0
        7)           dataset_name : grating
    -------------------------------------------------------------------------------------
     2) DistortionCorrection
        1)        center_from_top : 1501.65022718
        2)      polynomial_coeffs : [1.0046313220318024, -1.4178700554417107e-05, 2.1224019269640804e-08, -8.779934725830327e-12, 1.4068158454435102e-15]
        3)       center_from_left : 1739.36341759
        4)              file_path : None
        5)            in_datasets : []
        6)             crop_edges : 45
        7)           out_datasets : []
    -------------------------------------------------------------------------------------
     3) TiffSaver
        1)            in_datasets : []
        2)                 prefix : None
        3)                pattern : PROJECTION
    -------------------------------------------------------------------------------------

.. raw:: html

     </div>
    </div></div></div><p><br/></p><p><br/></p><div class="confluence-information-macro has-no-icon confluence-information-macro-tip"><div class="confluence-information-macro-body"><div class="table-wrap"><table class="wrapped confluenceTable"><colgroup><col/></colgroup><tbody><tr><th class="highlight-red confluenceTh" data-highlight-colour="red"><h3 id="ReconstructionfromimagedataintheHDFformat:Savu-notesonstandarduse-Example7:Processlistforreconstructingaseriesofidenticaltomographyscans(storedsequentiallyinasingle3ddataset)"><strong>Example 7: Process list for reconstructing a series of identical tomography scans (stored sequentially in a single 3d dataset)<br/></strong></h3></th></tr></tbody></table></div><p><br/></p><p>An example process list for reconstructing middle 500 slices (c.f. mid-250:mid+250 in [:, mid-250:mid+250, :, 1] of 1.preview) of the first two scans (c.f. 1 in [:, mid-250:mid+250, :, 1] in 1.preview) in a series of N ≥ 2 tomography scans, each containing 901 images (c.f. 901 in 1.3d_to_4d), with <strong>VoCentering </strong>being used on every 25-th slice (c.f. 0:end:25 in [:, 0:end:25, :, 0] in 3.preview) of the first scan only (c.f. the rightmost 0 in [:, 0:end:25, :, 0] in 3.preview):</p><div class="code panel pdl" style="border-width: 1px;">
     <div class="codeHeader panelHeader pdl hide-border-bottom" style="border-bottom-width: 1px;">
      <b class="code-title"></b>
      <span class="collapse-source expand-control" style="display:none;"><span class="expand-control-icon icon">&nbsp;</span><span class="expand-control-text">Expand source</span></span>
      <span class="collapse-spinner-wrapper"></span>
     </div>
     <div class="codeContent panelContent pdl hide-toolbar">

Example 7: Process list in Savu Configurator

.. code-block:: none

    >>> disp - a

    -------------------------------------------------------------------------------------
     1) NxtomoLoader
        1)                preview : [:, mid-250:mid+250, :, 1]
        2)         image_key_path : entry1/tomo_entry/instrument/detector/image_key
        3)                   name : tomo
        4)               3d_to_4d : 901
        5)                   flat : [/dls/b16/data/2020/mm24130-1/tmp/SOTomo/342919.nxs, entry1/pco1_sw_hdf/data, 1]
        6)              data_path : entry1/tomo_entry/data/data
        7)                   dark : [/dls/b16/data/2020/mm24130-1/tmp/SOTomo/342918.nxs, entry1/pco1_sw_hdf/data, 1]
        8)                 angles : None
        9)           ignore_flats : None
    -------------------------------------------------------------------------------------
     2) DarkFlatFieldCorrection
        1)            in_datasets : []
        2)            upper_bound : None
        3)           out_datasets : []
        4)            lower_bound : None
        5)                pattern : PROJECTION
        6)        warn_proportion : 0.05
    -------------------------------------------------------------------------------------
     3) VoCentering
        1)                preview : [:, 0:end:25, :, 0]
        2)            start_pixel : None
        3)            search_area : [-500, 500]
        4)                  ratio : 0.5
        5)            in_datasets : []
        6)               row_drop : 20
        7)       broadcast_method : median
        8)           out_datasets : [cor_raw, cor_fit]
        9)   datasets_to_populate : []
       10)          search_radius : 6
       11)                   step : 0.5
       12)         average_radius : 0
    -------------------------------------------------------------------------------------
     4) RemoveAllRings
        1)            in_datasets : []
        2)           out_datasets : []
        3)                la_size : 71
        4)                    snr : 3.0
        5)                sm_size : 31
    -------------------------------------------------------------------------------------
     5) AstraReconGpu
        1)               init_vol : None
        2)                preview : []
        3)                    log : True
        4)              algorithm : FBP_CUDA
        5)           n_iterations : 1
        6)               res_norm : False
        7)     centre_of_rotation : 1280
        8)             FBP_filter : ram-lak
        9)            in_datasets : []
       10)                  ratio : 0.95
       11)           out_datasets : []
       12)             centre_pad : False
       13)              outer_pad : False
       14)               log_func : np.nan_to_num(-np.log(sino))
       15)             force_zero : [None, None]
       16)              vol_shape : fixed
    -------------------------------------------------------------------------------------
     6) TiffSaver
        1)            in_datasets : []
        2)                 prefix : None
        3)                pattern : VOLUME_XZ
    -------------------------------------------------------------------------------------

.. raw:: html


     </div>
    </div></div></div><p><br/></p><p><br/></p><div class="confluence-information-macro has-no-icon confluence-information-macro-tip"><div class="confluence-information-macro-body"><div class="table-wrap"><table class="wrapped confluenceTable"><colgroup><col/></colgroup><tbody><tr><th class="highlight-red confluenceTh" data-highlight-colour="red"><h3 id="ReconstructionfromimagedataintheHDFformat:Savu-notesonstandarduse-Example8:Simpleprocesslistforreconstructingaflat-and-dark-field-correcteddatasetthatwaspreviouslygeneratedinSavu"><strong>Example 8: Simple process list for reconstructing a flat-and-dark-field-corrected dataset that was previously generated in Savu<br/></strong></h3></th></tr></tbody></table></div><p><br/></p><p>The process list below provides an example of how to load a flat-and-dark-field-corrected dataset from a Savu Nexus file (the latter having been previously generated using a process list similar to that described in Example 4b) to reconstruct the 100 middle slices:</p><div class="code panel pdl" style="border-width: 1px;">
     <div class="codeHeader panelHeader pdl hide-border-bottom" style="border-bottom-width: 1px;">
      <b class="code-title"></b>
      <span class="collapse-source expand-control" style="display:none;"><span class="expand-control-icon icon">&nbsp;</span><span class="expand-control-text">Expand source</span></span>
      <span class="collapse-spinner-wrapper"></span>
     </div>
     <div class="codeContent panelContent pdl hide-toolbar">


Example 6: Process list in Savu Configurator

.. code-block:: none

    >>> disp -a
    -------------------------------------------------------------------------------------
     1) SavuNexusLoader
        1)                preview : {data: [:, mid-50:mid+50, :]}
        2)               datasets : [entry/final_result_tomo]
        3)                  names : [data]
    -------------------------------------------------------------------------------------
     2) RemoveAllRings
        1)            in_datasets : []
        2)           out_datasets : []
        3)                la_size : 71
        4)                    snr : 3.0
        5)                sm_size : 31
    -------------------------------------------------------------------------------------
     3) AstraReconGpu
        1)               init_vol : None
        2)                preview : []
        3)                    log : True
        4)              algorithm : FBP_CUDA
        5)           n_iterations : 1
        6)               res_norm : False
        7)     centre_of_rotation : 1114
        8)             FBP_filter : ram-lak
        9)            in_datasets : []
       10)                  ratio : 0.95
       11)           out_datasets : []
       12)             centre_pad : True
       13)              outer_pad : True
       14)               log_func : np.nan_to_num(-np.log(sino))
       15)             force_zero : [None, None]
       16)              vol_shape : fixed
    -------------------------------------------------------------------------------------
     4) TiffSaver
        1)            in_datasets : []
        2)                 prefix : None
        3)                pattern : VOLUME_XZ
    -------------------------------------------------------------------------------------

.. raw:: html

     </div>
    </div></div></div><p><br/></p><p><br/></p><div class="confluence-information-macro has-no-icon confluence-information-macro-tip"><div class="confluence-information-macro-body"><div class="table-wrap"><table class="wrapped confluenceTable"><colgroup><col/></colgroup><tbody><tr><th class="highlight-red confluenceTh" data-highlight-colour="red"><h3 id="ReconstructionfromimagedataintheHDFformat:Savu-notesonstandarduse-Example9:Simpleprocesslistforreconstructinganoff-centrescantakenovertherangeof360deg"><strong>Example 9: Simple process list for reconstructing an off-centre scan taken over the range of 360 deg<br/></strong></h3></th></tr></tbody></table></div><p><br/></p><p>The process list below provides an example of how to employ Convert360180Sinogram to process an off-centre (double-FOV) scan taken over the range of 360 deg. In this example, an optimisation of sinogram stitching is performed using a single (middle) slice (41 slices are loaded by NxtomoLoader, of which 40 slices are cropped out by DistortionCorrection):</p><div class="code panel pdl" style="border-width: 1px;">
     <div class="codeHeader panelHeader pdl hide-border-bottom" style="border-bottom-width: 1px;">
      <b class="code-title"></b>
      <span class="collapse-source expand-control" style="display:none;"><span class="expand-control-icon icon">&nbsp;</span><span class="expand-control-text">Expand source</span></span>
      <span class="collapse-spinner-wrapper"></span>
     </div>
     <div class="codeContent panelContent pdl hide-toolbar">

Example 6: Process list in Savu Configurator

.. code-block:: none

    >>> disp -a

    -------------------------------------------------------------------------------------
     1) NxtomoLoader
        1)                preview : [:, mid-20:mid+21:1, :]
        2)         image_key_path : entry1/tomo_entry/instrument/detector/image_key
        3)                   name : tomo
        4)               3d_to_4d : False
        5)                   flat : [None, None, 1]
        6)              data_path : entry1/tomo_entry/data/data
        7)                   dark : [None, None, 1]
        8)                 angles : None
        9)           ignore_flats : None
    -------------------------------------------------------------------------------------
     2) DarkFlatFieldCorrection
        1)            in_datasets : []
        2)            upper_bound : None
        3)           out_datasets : []
        4)            lower_bound : None
        5)                pattern : PROJECTION
        6)        warn_proportion : 0.05
    -------------------------------------------------------------------------------------
     3) DistortionCorrection
        1)        center_from_top : 1252.39204012
        2)      polynomial_coeffs : [0.9994616257658503, 1.969316697623304e-06, -8.765055925711061e-11, 2.101099317181636e-12, -5.6298542416383075e-16]
        3)       center_from_left : 1200.19325348
        4)              file_path : None
        5)            in_datasets : []
        6)             crop_edges : 20
        7)           out_datasets : []
    -------------------------------------------------------------------------------------
     4) Convert360180Sinogram
        1)            in_datasets : []
        2)           out_datasets : [in_datasets[0], cor]
        3)                 center : 2500:2520:1;
    -------------------------------------------------------------------------------------
     5) AstraReconGpu
        1)               init_vol : None
        2)                preview : []
        3)                    log : True
        4)              algorithm : FBP_CUDA
        5)           n_iterations : 1
        6)               res_norm : False
        7)     centre_of_rotation : cor
        8)             FBP_filter : ram-lak
        9)            in_datasets : [tomo]
       10)                  ratio : 0.95
       11)           out_datasets : [tomo]
       12)             centre_pad : True
       13)              outer_pad : True
       14)               log_func : np.nan_to_num(-np.log(sino))
       15)             force_zero : [None, None]
       16)              vol_shape : fixed
    -------------------------------------------------------------------------------------

.. raw:: html

     </div>
    </div></div></div><p><br/></p><p><br/></p><p><br/></p><div class="table-wrap"><table class="wrapped confluenceTable"><colgroup><col/></colgroup><tbody><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow"><h2 id="ReconstructionfromimagedataintheHDFformat:Savu-notesonstandarduse-Appendices"><strong>Appendices</strong></h2></th></tr></tbody></table></div><p><strong><br/></strong></p><div class="table-wrap"><table class="wrapped confluenceTable"><colgroup><col/></colgroup><tbody><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow"><h3 id="ReconstructionfromimagedataintheHDFformat:Savu-notesonstandarduse-AppendixA:Interoperabilityoftheparameter-tuningandpreviewingoperations"><strong>Appendix A: Interoperability of the parameter-tuning and previewing operations<br/></strong></h3></th></tr></tbody></table></div><p>Since each instance of <em>parameter tuning</em> in <strong>Savu</strong> adds an extra dimension to the input dataset, it is often desirable to use the <em>previewing</em> (subset-selection) mechanism to reduce the workload of any subsequent resource-demanding processes, e. g. <strong>VoCentering</strong> or <strong>AstraReconGpu</strong>. This can be accomplished by setting the <strong><em>preview</em></strong> parameter of <strong>VoCentering </strong>or, respectively, that of <strong>AstraReconGpu</strong> to a desirable rank-3 slice of the incoming higher-order dataset, generated by one or more <em>parameter-tuning</em> operations invoked by the preceding processes (see, e.g., Example 2).     </p><p><br/></p><div class="table-wrap"><table class="wrapped confluenceTable"><colgroup><col/></colgroup><tbody><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow"><h3 id="ReconstructionfromimagedataintheHDFformat:Savu-notesonstandarduse-AppendixB:Briefreferenceguidetospecifyingvaluesfortheparameter-tuningoperations"><strong>Appendix B: Brief reference guide to specifying values for the parameter-tuning operations<br/></strong></h3></th></tr></tbody></table></div><p>Note that not every parameter in <strong>Savu</strong> is <em>tunable</em>. For any <em>tunable</em> parameter, one can input its <em>tuning</em> values using the methods described below:   </p><div class="table-wrap"><table class="wrapped relative-table confluenceTable" style="width: 99.9399%;"><colgroup><col style="width: 17.1473%;"/><col style="width: 11.2001%;"/><col style="width: 27.6871%;"/><col style="width: 43.9404%;"/></colgroup><tbody><tr><th style="text-align: center;" class="confluenceTh">Task</th><th style="text-align: center;" class="confluenceTh">Syntax</th><th colspan="1" style="text-align: center;" class="confluenceTh">Comment(s)</th><th colspan="1" style="text-align: center;" class="confluenceTh">Example(s)</th></tr><tr><td class="confluenceTd">To input an ordered list of <span style="color: rgb(255,102,0);"><em>n</em></span> individual values.</td><td class="confluenceTd"><em><span style="color: rgb(255,102,0);">val_1</span>; <span style="color: rgb(255,102,0);">val_2</span>;...</em> <span style="color: rgb(255,102,0);"><em>val_n</em></span></td><td colspan="1" class="confluenceTd"><ol><li>Input values need to be semi-colon separated.</li><li>Note the absence of the trailing semi-colon.</li><li>Input values can be non-numeric.</li></ol></td><td colspan="1" class="confluenceTd"><p>mod <span style="color: rgb(128,0,0);">6</span>.7 <span style="color: rgb(128,0,0);">1000.8</span>;<span style="color: rgb(128,0,0);">1010.8</span>;<span style="color: rgb(128,0,0);">1020.8</span>;<span style="color: rgb(128,0,0);">1030.8</span>;<span style="color: rgb(128,0,0);">1040.8</span></p><p>mod <span style="color: rgb(128,0,0);">6</span>.centre_of_rotation <span style="color: rgb(128,0,0);">1000.8</span>;<span style="color: rgb(128,0,0);">1010.8</span>;<span style="color: rgb(128,0,0);">1020.8</span>;<span style="color: rgb(128,0,0);">1030.8</span>;<span style="color: rgb(128,0,0);">1040.8</span></p><p>mod <span style="color: rgb(128,0,0);">6</span>.4 <span style="color: rgb(128,0,0);">FBP_CUDA</span>;<span style="color: rgb(128,0,0);">CGLS_CUDA</span></p><p>mod <span style="color: rgb(128,0,0);">6</span>.algorithm <span style="color: rgb(128,0,0);">FBP_CUDA</span>;<span style="color: rgb(128,0,0);">CGLS_CUDA</span></p></td></tr><tr><td class="confluenceTd"><p>To input an arithmetic sequence of all numbers starting from <span style="color: rgb(255,102,0);"><em>val_from</em></span> and not exceeding <em><span style="color: rgb(255,102,0);">val_to</span>,</em> calculated using the common difference of <em><span style="color: rgb(255,102,0);">cmn_diff</span>.</em></p></td><td class="confluenceTd"><p><em><span style="color: rgb(255,102,0);">val_from</span>:<span style="color: rgb(255,102,0);">val_to</span>:<span style="color: rgb(255,102,0);">cmn_diff</span>;</em></p></td><td colspan="1" class="confluenceTd"><div class="content-wrapper"><ol><li>The three defining numeric arguments need to be colon separated.</li><li>Note the presence of the trailing semi-colon.</li><li>The <em><span style="color: rgb(255,102,0);">val_to</span></em> limit will not be included in the output values unless it is one of the elements in the specified arithmetic sequence.</li><li><p>It is sometimes useful to expand this <strong>Savu</strong> expression in Unix shell using the sequence-of-numbers (<em>seq)</em> command (note a different syntax), followed by the number-lines (<em>nl</em>) command, e.g.</p><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b>Linux command: seq &lt;FIRST&gt; &lt;INCREMENT&gt; &lt;LAST&gt;</b></div><div class="codeContent panelContent pdl">
    <pre class="syntaxhighlighter-pre" data-syntaxhighlighter-params="brush: bash; gutter: false; theme: Confluence" data-theme="Confluence">~&gt;seq 1000.8 10.0 1040.8 | nl
         1    1000.8
         2    1010.8
         3    1020.8
         4    1030.8
         5    1040.8
    ~&gt;seq 1000.8 10.0 1040.8 | nl -v 0
         0    1000.8
         1    1010.8
         2    1020.8
         3    1030.8
         4    1040.8
    ~&gt;</pre>
    </div></div><p>(note that the indexing scheme of ImageJ is one-based, whereas that of <a class="external-link" href="https://dawnsci.org/downloads/" rel="nofollow">DAWN</a>, <a class="external-link" href="https://www.hdfgroup.org/downloads/hdfview/" rel="nofollow">hdfview </a>and <strong>TiffSaver</strong>'s file output is zero-based). Alternatively, one can use:</p><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b>n = 1, 2, 3,...</b></div><div class="codeContent panelContent pdl">
    <pre class="syntaxhighlighter-pre" data-syntaxhighlighter-params="brush: java; gutter: false; theme: Confluence" data-theme="Confluence">1-based seq(n) = FIRST_VAL + (n-1) * INCREMENT</pre>
    </div></div><p>or</p><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b>n = 0, 1, 2,...</b></div><div class="codeContent panelContent pdl">
    <pre class="syntaxhighlighter-pre" data-syntaxhighlighter-params="brush: java; gutter: false; theme: Confluence" data-theme="Confluence">0-based seq(n) = FIRST_VAL + n * INCREMENT</pre>
    </div></div></li></ol></div></td><td colspan="1" class="confluenceTd"><p>mod <span style="color: rgb(128,0,0);">6</span>.7 <span style="color: rgb(128,0,0);">1000.8</span>:<span style="color: rgb(128,0,0);">1040.8</span>:<span style="color: rgb(128,0,0);">10.0</span>;</p><p>mod <span style="color: rgb(128,0,0);">6</span>.centre_of_rotation <span style="color: rgb(128,0,0);">1000.8</span>:<span style="color: rgb(128,0,0);">1040.8</span>:<span style="color: rgb(128,0,0);">10.0</span>;</p><p>mod <span style="color: rgb(128,0,0);">6</span>.centre_of_rotation <span style="color: rgb(128,0,0);">1020.8</span>-2*<span style="color: rgb(128,0,0);">10.0</span>:<span style="color: rgb(128,0,0);">1020.8</span>+2*<span style="color: rgb(128,0,0);">10.0</span>:<span style="color: rgb(128,0,0);">10.0</span>;</p></td></tr></tbody></table></div><p><br/></p><p><br/></p><div class="table-wrap"><table class="wrapped confluenceTable"><colgroup><col/></colgroup><tbody><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow"><h3 id="ReconstructionfromimagedataintheHDFformat:Savu-notesonstandarduse-AppendixC:Batchprocessing"><strong>Appendix C: Batch processing<br/></strong></h3></th></tr></tbody></table></div><p>Batch processing in <strong>Savu</strong> can be done with the help of the <em>savu-batch</em> command, whose arguments are ordered in a logically identical way to that employed by the <em>savu_mpi</em> command, the only difference being the first argument, which is used to supply a path to a user-prepared batch file:</p><div class="code panel pdl" style="border-width: 1px;"><div class="codeContent panelContent pdl">
    <pre class="syntaxhighlighter-pre" data-syntaxhighlighter-params="brush: java; gutter: false; theme: Confluence" data-theme="Confluence">savu_mpi                      &lt;SCAN_DATA_FILE&gt; &lt;SAVU_PROCESS_LIST_FILE&gt; &lt;OUT_DIR&gt;
    savu-batch &lt;BATCH_PARAM_FILE&gt; &lt;SCAN_DATA_DIR&gt;  &lt;SAVU_PROCESS_LIST_DIR&gt;  &lt;OUT_DIR&gt; </pre>
    </div></div><p><br/></p><p>To make the <em>savu-batch</em> command available in Linux terminal, execute 'module load python/ana' and 'module load tomography': </p><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b></b></div><div class="codeContent panelContent pdl">


Linux Command: Savu-batch

.. code-block:: none

    ~>module load python/ana
    ~>module load tomography
    ~>savu-batch
    Usage: savu-batch <BATCH_PARAM_FILE> <SCAN_DATA_DIR> <SAVU_PROCESS_LIST_DIR> <OUT_DIR> [-d <INTERMED_DIR>] [-e EMAIL_ADDRESS_1[;EMAIL_ADDRESS_2;... EMAIL_ADDRESS_N]] [-t <TIME_OUT_MINUTES>] [-v]
    Run a batch of reconstructions using Savu.
         -h                  display this help and exit.
         -d INTERMED_DIR     save all intermediate files in INTERMED_DIR directory.
         -e EMAILS           send e-mail notification(s) to (semicolon-separated) address(es) in EMAILS.
         -t TIMEOUT_MINUTES  monitor each cluster job no longer than TIMEOUT_MINUTES.
         -v                  be verbose: send e-mail notifications on completion of each cluster job (in addition to sending a summary notification on completion of the entire batch).
    ~>

.. raw:: html

    </div></div><p><br/></p><p>The first argument of <em>savu-batch</em>, &lt;<span style="color: rgb(255,102,0);">BATCH_PARAM_FILE</span>&gt;, is a path to comma-separated values (CSV) file, containing a table of desired batch parameters, e.g.</p><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b></b></div><div class="codeContent panelContent pdl">

batch.csv

.. code-block:: none

        #<scan number>,<proces list>[,[CoR(s)],[output dir]]                                            # commented-out lines are ignored (and so are any comments on the RHS of valid lines)
        102923,  4x/spl_f102921_d102922.nxs, 1197.75, 4x/%s
        102974,  4x/spl_f102921_d102922.nxs, 1255.50, 4x/%s                                                 # same process-list file as in line 2, used with different CoR to reconstruct a different scan
        102923,  4x/spl_f102921_d102922_pci.nxs, 1197.75, 4x/%s/pci                                 # same scan as in line 2, reconstructed with phase-contrast retrieval
        102990,  4x/spl_f102984_d102985.nxs, 1254.6:1255.9:0.1;, preview/4x/%s              # CoR tuning in dedicated sub-directory
        102986,  4x/spl_f102988_d102989.nxs, 1256.50, 4x/%s
        103038, 10x/spl_f103036_d103037.nxs,, 10x/%s                                                                # CoR intentionally NOT provided (CoR found in <SAVU_PROCESS_LIST_DIR>/10x/spl_f103036_d103037.nxs is used as is)
        103050, 10x/spl_f103048_d103049.nxs, 919.50, 10x/%s
        103050, 10x/spl_f103048_d103049_lensdistortcrop40.nxs, 919.50-40, 10x/%s    # Savu-interpretable mathematical expression for adjusting CoR by 40 pixels due to the 40-pixel cropping in DistortionCorrection
        104022, spl_f103048_d103049.nxs, 1110.25, tests                                                             # scan-numbered output sub-directory intentionally NOT provided (output goes to <OUT_DIR>/tests)
        103052, spl_f103048_d103049.nxs, 910.50,                                                                    # output sub-directory intentionally NOT provided (output goes to <OUT_DIR>)


.. raw:: html

    </div></div><p><br/></p><p><strong>Notes</strong>:</p><ol><li><em>savu-batch</em> reconstructs scans using the <em>savu_mpi</em> command (on the cluster).</li><li><em>savu-batch</em> reconstructs scans sequentially one-by-one, monitoring and waiting (for the duration of <span style="color: rgb(255,102,0);"><span style="color: rgb(0,0,0);">&lt;</span>TIMEOUT_MINUTES</span>&gt;) for each reconstruction job to complete (on the cluster) before launching the next one.</li><li><em>savu-batch</em> reconstructs scans in the same order as that specified in &lt;<span style="color: rgb(255,102,0);">BATCH_PARAM_FILE</span>&gt;.</li><li><em>savu-batch </em>makes its own, internal copies of all input process-list files, specified in &lt;<span style="color: rgb(255,102,0);">BATCH_PARAM_FILE</span>&gt;, at the time of executing the <em>savu-batch</em> command, and then, if required, each of these copies is appropriately edited just before the <em>savu_mpi</em> command is executed on each of them.      </li><li>The values of <em>CoR</em> specified in &lt;<span style="color: rgb(255,102,0);">BATCH_PARAM_FILE</span>&gt; are used as they are to set the <em><strong>centre_of_rotation</strong></em> parameter of any (active) reconstructor process found in the corresponding <strong>Savu</strong> process-list file (hence the user is responsible for making any adjustments needed to account for any additional cropping requested by, for example, the <em><strong>crop_edges</strong></em> parameter of <strong>DistortionCorrection</strong>, etc.). </li><li>If no value of <em>CoR </em>is specified for some item in &lt;<span style="color: rgb(255,102,0);">BATCH_PARAM_FILE</span>&gt;, then the value of the <em><strong>centre_of_rotation</strong></em> parameter found (at the time of launching <em>savu-batch</em>) in the corresponding <strong>Savu</strong> process-list file is used.</li><li><em>savu-batch</em> is able to handle process lists that don't include any processes requiring CoR (in which case an empty space, or any numerical value, can be provided as nothing depends on it).</li></ol><p><br/></p><p><strong>Example</strong>:</p><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b></b></div>

    <div class="codeContent panelContent pdl">

Linux command: savu-batch

    >>> savu-batch /dls/i13/data/2018/mt12345-6/processing/process_lists/batch/batch.csv /dls/i13/data/2018/mt12345-6/raw /dls/i13/data/2018/mt12345-6/processing/process_lists /dls/i13/data/2018/mt12345-6/processing/reconstruction -d /dls/i13/data/2018/mt12345-6/tmp -e &quot;whoever@wherever&quot;

.. raw:: html


    </div></div><p><br/></p><p>In the above <em>savu-batch</em> example, the arguments are as follows:</p><div class="table-wrap"><table class="relative-table wrapped confluenceTable" style="width: 99.958%;"><colgroup><col style="width: 8.60983%;"/><col style="width: 24.0655%;"/><col style="width: 67.3247%;"/></colgroup><tbody><tr><th class="highlight-blue confluenceTh" data-highlight-colour="blue" style="text-align: center;"><em>Argument</em></th><th class="highlight-blue confluenceTh" data-highlight-colour="blue" style="text-align: center;"><em>Argument Value</em></th><th class="highlight-blue confluenceTh" colspan="1" data-highlight-colour="blue" style="text-align: center;"><em>Comment(s)</em></th></tr><tr><td class="highlight-yellow confluenceTd" data-highlight-colour="yellow"><pre>&lt;BATCH_PARAM_FILE&gt;</pre></td><td class="confluenceTd"><pre>/dls/i13/data/2018/mt12345-6/processing/process_lists/batch/batch.csv</pre></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td class="highlight-yellow confluenceTd" data-highlight-colour="yellow"><pre>&lt;SCAN_DATA_DIR&gt;</pre></td><td class="confluenceTd"><pre>/dls/i13/data/2018/mt12345-6/raw</pre></td><td colspan="1" class="confluenceTd">Contains all Nexus scan files specified in &lt;<span style="color: rgb(255,102,0);">BATCH_PARAM_FILE</span>&gt;, e.g. /dls/i13/data/2018/mt12345-6/raw/<span style="color: rgb(128,0,0);">102923</span>.nxs, etc.</td></tr><tr><td class="highlight-yellow confluenceTd" data-highlight-colour="yellow"><pre>&lt;SAVU_PROCESS_LIST_DIR&gt;</pre></td><td class="confluenceTd"><pre>/dls/i13/data/2018/mt12345-6/processing/process_lists</pre></td><td colspan="1" class="confluenceTd"><ol><li>Contains all <strong>Savu</strong> process-list files specified in &lt;<span style="color: rgb(255,102,0);">BATCH_PARAM_FILE</span>&gt;, e.g. /dls/i13/data/2018/mt12345-6/processing/process_lists/4x/spl_f102921_d102922.nxs, etc.</li><li><p>If &lt;<span style="color: rgb(255,102,0);">BATCH_PARAM_FILE</span>&gt; contains an absolute path to some <strong>Savu</strong> process-list file (as opposed to a path specified relative to &lt;<span style="color: rgb(255,102,0);">SAVU_PROCESS_LIST_DIR</span>&gt;), then this absolute path is always respected (i.e. &lt;<span style="color: rgb(255,102,0);">SAVU_PROCESS_LIST_DIR</span>&gt; is overridden).</p></li></ol></td></tr><tr><td class="highlight-yellow confluenceTd" colspan="1" data-highlight-colour="yellow"><pre>&lt;OUT_DIR&gt;</pre></td><td colspan="1" class="confluenceTd"><pre>/dls/i13/data/2018/mt12345-6/processing/reconstruction</pre></td><td colspan="1" class="confluenceTd"><ol><li>Any intermediate output sub-directories are automatically created if they don't already exist on the file system (provided the user has sufficient file-access permisions).</li><li>For example, reconstruction of scan <span style="color: rgb(128,0,0);">102923</span>, specified in line 2 of &lt;<span style="color: rgb(255,102,0);">BATCH_PARAM_FILE</span>&gt;, will be saved by <strong>Savu</strong> in /dls/i13/data/2018/mt12345-6/processing/reconstruction/4x/<span style="color: rgb(128,0,0);">102923</span>/&lt;<span style="color: rgb(255,102,0);">YYYYMMDDhhmmss</span>&gt;_<span style="color: rgb(128,0,0);">102923</span>/, i.e. the 4x/%s output directory, specified in the same line of &lt;<span style="color: rgb(255,102,0);">BATCH_PARAM_FILE</span>&gt;, is expanded to 4x/<span style="color: rgb(128,0,0);">102923</span>/, whereas the last (innermost) sub-directory, &lt;<span style="color: rgb(255,102,0);">YYYYMMDDhhmmss</span>&gt;_<span style="color: rgb(128,0,0);">102923</span>/, is automatically generated by <strong>Savu</strong> itself.</li><li>If &lt;<span style="color: rgb(255,102,0);">BATCH_PARAM_FILE</span>&gt; contains an absolute path to some output directory (as opposed to a path specified relative to &lt;<span style="color: rgb(255,102,0);">OUT_DIR</span>&gt;), then this absolute path is always respected (i.e. &lt;<span style="color: rgb(255,102,0);">OUT_DIR</span>&gt; is overridden).  </li></ol></td></tr><tr><td class="highlight-yellow confluenceTd" colspan="1" data-highlight-colour="yellow"><pre>&lt;INTERMED_DIR&gt;</pre></td><td colspan="1" class="confluenceTd"><pre>/dls/i13/data/2018/mt12345-6/tmp</pre></td><td colspan="1" class="confluenceTd"><br/></td></tr></tbody></table></div><p><br/></p><p><strong>Additional notes</strong>:</p><ol><li>When preparing batch files, please use a Linux text editor as files created under Windows are not compatible.</li><li>If you intend to run multiple batches, please wait for each individual batch to finish before submitting another one. </li><li>When supplying an e-mail address, please bear in kind that some mail boxes may automatically block machine-generated e-mail notifications.</li></ol><p><br/></p><p><br/></p><p><br/></p><p><br/></p>
                        </div>



                    </div>             </div>

            </div>     </body>
    </html>
