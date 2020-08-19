.. _extraction_tiff_images:


Extraction of TIFF images from image data in the HDF format (with optional bit-depth reduction) and related matters
--------------------------------------------------------------------------------------------------------------------


.. raw:: html

    <!DOCTYPE html>
    <html>


        <body class="theme-default aui-theme-default">
            <div id="page">
                <div id="main" class="aui-page-panel">
                    <div id="main-header">
                        <div id="breadcrumb-section">

                        </div>

                    </div>

                    <div id="content" class="view">
                        <div class="page-metadata">

                Created by <span class='author'> Kaz Wanelik</span>
                            </div>
                        <div id="main-content" class="wiki-content group">
                        <p><br/></p><p><style type='text/css'>/*<![CDATA[*/
    div.rbtoc1592231712607 {padding: 0px;}
    div.rbtoc1592231712607 ul {list-style: disc;margin-left: 0px;}
    div.rbtoc1592231712607 li {margin-left: 0px;padding-left: 0px;}
    .syntaxhighlighter-pre {font-size: small;}
    table {font-size: small;}

    /*]]>*/</style><div class='toc-macro rbtoc1592231712607'>
    <ul class='toc-indentation'>
    <li><a href='#ExtractionofTIFFimagesfromimagedataintheHDFformat(withoptionalbit-depthreduction)andrelatedmatters-Introduction'>Introduction</a></li>
    <li><a href='#ExtractionofTIFFimagesfromimagedataintheHDFformat(withoptionalbit-depthreduction)andrelatedmatters-Context1:HDF5datasetofreconstructionvolume(3d)'>Context 1: HDF5 dataset of reconstruction volume (3d)</a>
    <ul class='toc-indentation'>
    <li><a href='#ExtractionofTIFFimagesfromimagedataintheHDFformat(withoptionalbit-depthreduction)andrelatedmatters-nxs2tiff'>nxs2tiff</a></li>
    <li><a href='#ExtractionofTIFFimagesfromimagedataintheHDFformat(withoptionalbit-depthreduction)andrelatedmatters-nxs2tiffux'>nxs2tiffux</a></li>
    </ul>
    </li>
    <li><a href='#ExtractionofTIFFimagesfromimagedataintheHDFformat(withoptionalbit-depthreduction)andrelatedmatters-Context2:HDF5datasetofrawdata(3d)'>Context 2: HDF5 dataset of raw data (3d)</a>
    <ul class='toc-indentation'>
    <li><a href='#ExtractionofTIFFimagesfromimagedataintheHDFformat(withoptionalbit-depthreduction)andrelatedmatters-nxs2tiff.1'>nxs2tiff</a></li>
    <li><a href='#ExtractionofTIFFimagesfromimagedataintheHDFformat(withoptionalbit-depthreduction)andrelatedmatters-nxs2tiffux.1'>nxs2tiffux</a></li>
    </ul>
    </li>
    <li><a href='#ExtractionofTIFFimagesfromimagedataintheHDFformat(withoptionalbit-depthreduction)andrelatedmatters-Context3:DirectoryofreconstructedslicesintheTIFFformat(2d)'>Context 3: Directory of reconstructed slices in the TIFF format (2d)</a>
    <ul class='toc-indentation'>
    <li><a href='#ExtractionofTIFFimagesfromimagedataintheHDFformat(withoptionalbit-depthreduction)andrelatedmatters-tiff2tiffux'>tiff2tiffux</a></li>
    </ul>
    </li>
    <li><a href='#ExtractionofTIFFimagesfromimagedataintheHDFformat(withoptionalbit-depthreduction)andrelatedmatters-Context4:Directoryofraw-datafilesintheTIFFformat(2d)'>Context 4: Directory of raw-data files in the TIFF format (2d)</a></li>
    </ul>
    </div></p><h2 id="ExtractionofTIFFimagesfromimagedataintheHDFformat(withoptionalbit-depthreduction)andrelatedmatters-Introduction"><strong>Introduction</strong></h2><p>It may sometimes be desirable to extract individual TIFF images from an HDF5 dataset and, optionally, reduce their bit-depth at the same time. Similarly, it may sometimes be useful to reduce the bit depth of any given set of TIFF images. The table below provides a summary of the most-frequently encountered contexts: </p><p><br/></p><div class="table-wrap"><table class="wrapped confluenceTable"><colgroup><col/><col/><col/><col/><col/><col/><col/><col/></colgroup><tbody><tr><th class="highlight-blue confluenceTh" data-highlight-colour="blue" style="text-align: center;">Context</th><th class="highlight-blue confluenceTh" data-highlight-colour="blue" style="text-align: center;">Dataset provenance</th><th class="highlight-blue confluenceTh" colspan="1" data-highlight-colour="blue" style="text-align: center;">Brief description of dataset</th><th class="highlight-blue confluenceTh" colspan="1" data-highlight-colour="blue" style="text-align: center;">Numeric data type of generic dataset</th><th class="highlight-blue confluenceTh" colspan="1" data-highlight-colour="blue" style="text-align: center;">Rank (R) of generic dataset</th><th class="highlight-blue confluenceTh" colspan="1" data-highlight-colour="blue"><p style="text-align: center;">Command to extract individual TIFF images<em>, </em></p><p style="text-align: center;"><em>preserving the original numeric data type and bit depth</em></p></th><th class="highlight-blue confluenceTh" colspan="1" data-highlight-colour="blue" style="text-align: left;">
    <p style="text-align: center;">Command to extract individual TIFF<em> </em>images,</p><p style="text-align: center;"><em> </em><em style="text-align: center;">capable of modifying the original numeric data type and bit depth</em></p></th><th class="highlight-blue confluenceTh" data-highlight-colour="blue" style="text-align: center;">Comment(s)</th></tr><tr><td colspan="1" class="confluenceTd">1</td><td colspan="1" class="confluenceTd">HDF5 dataset of reconstruction volume</td><td colspan="1" class="confluenceTd">Single 3d dataset containing reconstruction volume generated by <em>Savu Tomography Reconstruction Pipeline</em>.</td><td colspan="1" class="confluenceTd">32-bit floating point</td><td colspan="1" class="confluenceTd">3 (or R&gt;3 for datasets with R-3 singleton dimensions, i.e. dimensions of unit length) </td><td colspan="1" class="confluenceTd">nxs2tiff</td><td colspan="1" class="confluenceTd">nxs2tiffux</td><td colspan="1" class="confluenceTd"><span>Can be applied to extract (bit-reduced) TIFF images from any 3d-dataset generated by any plug-in in <em>Savu</em>.</span></td></tr><tr><td class="confluenceTd">2</td><td class="confluenceTd">HDF5 dataset of raw data</td><td colspan="1" class="confluenceTd">Single 3d dataset containing sample projections and, possibly, dark- and flat-field images.</td><td colspan="1" class="confluenceTd">16-bit unsigned integer</td><td colspan="1" class="confluenceTd">3</td><td colspan="1" class="confluenceTd">nxs2tiff</td><td colspan="1" class="confluenceTd">nxs2tiffux</td><td class="confluenceTd"><span>Can be applied to extract (bit-reduced) TIFF images from any 3d-dataset created by any HDF5 File Writer in GDA or EPICS.</span></td></tr><tr><th class="highlight-grey confluenceTh" colspan="1" data-highlight-colour="grey"><br/></th><th class="highlight-grey confluenceTh" colspan="1" data-highlight-colour="grey"><br/></th><th class="highlight-grey confluenceTh" colspan="1" data-highlight-colour="grey"><br/></th><th class="highlight-grey confluenceTh" colspan="1" data-highlight-colour="grey"><br/></th><th class="highlight-grey confluenceTh" colspan="1" data-highlight-colour="grey"><br/></th><th class="highlight-grey confluenceTh" colspan="1" data-highlight-colour="grey"><br/></th><th class="highlight-grey confluenceTh" colspan="1" data-highlight-colour="grey"><br/></th><th class="highlight-grey confluenceTh" colspan="1" data-highlight-colour="grey"><br/></th></tr><tr><td colspan="1" class="confluenceTd">3</td><td colspan="1" class="confluenceTd">Directory of reconstructed slices in the TIFF format</td><td colspan="1" class="confluenceTd">Sequence of reconstructed slices, stored as individual TIFF files in a single directory.</td><td colspan="1" class="confluenceTd">32-bit floating point</td><td colspan="1" class="confluenceTd">2</td><td colspan="1" class="confluenceTd">n/a</td><td colspan="1" class="confluenceTd">tiff2tiffux</td><td colspan="1" class="confluenceTd">Can be applied to reduce the bit depth of TIFF images generated by the <em>tomo-recon</em> command (the predecessor of <em>Savu</em>).</td></tr><tr><td colspan="1" class="confluenceTd">4</td><td colspan="1" class="confluenceTd">Directory of raw-data files in the TIFF format</td><td colspan="1" class="confluenceTd">Sequence of raw images (including sample projections and, possibly, dark- and flat-field images), stored as individual TIFF files in a single directory.</td><td colspan="1" class="confluenceTd">16-bit unsigned integer</td><td colspan="1" class="confluenceTd">2</td><td colspan="1" class="confluenceTd">n/a</td><td colspan="1" class="confluenceTd">tiff2tiffux</td><td colspan="1" class="confluenceTd"><span>Can be applied to reduce the bit depth of TIFF images created by any TIFF File Writer in GDA or EPICS.</span></td></tr></tbody></table></div><p><br/></p><p>All commands mentioned above become available after executing:</p><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b></b></div><div class="codeContent panelContent pdl">
    <pre class="syntaxhighlighter-pre" data-syntaxhighlighter-params="brush: java; gutter: false; theme: Confluence" data-theme="Confluence">module add tomography</pre>
    </div></div><p><br/></p><p>For a brief description of all available options and arguments for any of these commands, please execute:</p><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b></b></div><div class="codeContent panelContent pdl">

    <pre class="syntaxhighlighter-pre" data-syntaxhighlighter-params="brush: java; gutter: false; theme: Confluence" data-theme="Confluence">
    &lt;command-name&gt; -h
    </pre>

    </div></div><p></p><h2 id="ExtractionofTIFFimagesfromimagedataintheHDFformat(withoptionalbit-depthreduction)andrelatedmatters-Context1:HDF5datasetofreconstructionvolume(3d)"><strong>Context 1: <strong>HDF5 dataset of reconstruction volume (3d)</strong> </strong></h2><h3 id="ExtractionofTIFFimagesfromimagedataintheHDFformat(withoptionalbit-depthreduction)andrelatedmatters-nxs2tiff"><strong>nxs2tiff</strong></h3><p>Example 1: extraction of TIFFs with the original 32-bit floating-point data type being <strong>preserved</strong> <strong></strong></p><div class="container" title="Hint: double-click to select code"><div class="line number1 index0 alt2"><p></p><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b></b></div><div class="codeContent panelContent pdl">

Linux Command
    >>> nxs2tiff -d /entry/final_result_tomo/data -b 0 -s 50 -i 1 --fp /dls/i13/data/2017/cm16786-1/processing/savu/vxu94780/13429/20170301171639_13429/13429_processed.nxs /dls/i13/data/2017/cm16786-1/processing/savu/vxu94780/13429/tiffs/

.. raw:: html

    </div></div><p>Note the essential <em>--fp</em> option being specified above. Note also that the shape of the dataset in this particular example is (2560, 2160, 2560), with the layout being (image_height, image_index, image_width).</p><p></p><p>Example 2: extraction of TIFFs with the original 32-bit floating-point data type being <strong>preserved </strong></p><div class="code panel pdl" style="border-width: 1px;"><div class="codeContent panelContent pdl">

Linux Command
    >>> python /dls_sw/apps/tomopy/tomopy/src/nxs2tiff.py -b 0 -s 130 -d 2-AstraReconGpu-tomo/data -i 3 --fp /dls/i13/data/2019/cm22976-1/processing/test/mt21081-1/recon/20190303220500_108393/tomo_p2_astra_recon_gpu.h5 ./Tiffs

.. raw:: html

    </div></div><p>Note that the shape of the dataset in this particular example is (2560, 1, 2560, 130), with the layout being (image_height, singleton_index, image_width, image_index). Incidentally, the above example also shows how to run nxs2tiff on a local workstation rather than on the compute cluster. </p></div></div><h3 id="ExtractionofTIFFimagesfromimagedataintheHDFformat(withoptionalbit-depthreduction)andrelatedmatters-nxs2tiffux"><strong>nxs2tiffux</strong></h3><p>Example: extraction of TIFFs accompanied by <strong>reduction</strong> of the original 32-bit floating-point data type to 8-bit unsigned integer, using <strong>explicitly</strong> specified input values for the min (<em>--lo</em>) and max (<em>--hi</em>) intensity values<strong><br/></strong></p><div class="code panel pdl" style="border-width: 1px;">
    <b></b></div><div class="codeContent panelContent pdl">

Linux Command
    >>> nxs2tiffux -d /entry/final_result_tomo/data -b 0 -s 50 -i 1 -u 8 --lo -0.0016974231 --hi 0.0016586095 /dls/i13/data/2017/cm16786-1/processing/savu/vxu94780/13429/20170301171639_13429/13429_processed.nxs /dls/i13/data/2017/cm16786-1/processing/savu/vxu94780/13429/tiffs/u8/

.. raw:: html

    </div><p>Note the <em>-u 8</em> option being specified above.</p><p><br/></p><h2 id="ExtractionofTIFFimagesfromimagedataintheHDFformat(withoptionalbit-depthreduction)andrelatedmatters-Context2:HDF5datasetofrawdata(3d)"><strong>Context 2: HDF5 dataset of raw data (3d)</strong></h2><h3 id="ExtractionofTIFFimagesfromimagedataintheHDFformat(withoptionalbit-depthreduction)andrelatedmatters-nxs2tiff.1"><strong>nxs2tiff</strong></h3><p>Example: extraction of TIFFs with the original 16-bit unsigned-integer data type being <strong>preserved</strong></p><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b></b></div><div class="codeContent panelContent pdl">

Linux Command
    >>> nxs2tiff -d /entry1/instrument/pco1_hw_hdf/data -b 0 -s 2159 /dls/i13/data/2013/cm5937-3/raw/23912.nxs /dls/i13/data/2013/cm5937-3/processing/raw/23912/projections/

.. raw:: html

    </div></div><p><br/></p><h3 id="ExtractionofTIFFimagesfromimagedataintheHDFformat(withoptionalbit-depthreduction)andrelatedmatters-nxs2tiffux.1"><strong>nxs2tiffux</strong></h3><p>Example: extraction of TIFFs accompanied by <strong>reduction </strong>of the original 16-bit unsigned-integer data type to 8-bit unsigned integer, using <strong>explicitly</strong> specified input values for the min (<em>--lo</em>) and max (<em>--hi</em>) intensity values</p><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b></b></div><div class="codeContent panelContent pdl">


Linux Command
    >>> nxs2tiffux -d /entry1/instrument/pco1_hw_hdf/data -i 1 -u 8 --lo -0.0016974231 --hi 0.0016586095 /dls/i13/data/2013/cm5937-3/raw/23912.nxs /dls/i13/data/2013/cm5937-3/processing/raw/23912/projections/u8/

.. raw:: html

    </div></div><p>Note the <em>-u 8</em> option being specified above.</p><p><br/></p><h2 id="ExtractionofTIFFimagesfromimagedataintheHDFformat(withoptionalbit-depthreduction)andrelatedmatters-Context3:DirectoryofreconstructedslicesintheTIFFformat(2d)"><strong>Context 3: Directory of reconstructed slices in the TIFF format (2d)</strong></h2><h3 id="ExtractionofTIFFimagesfromimagedataintheHDFformat(withoptionalbit-depthreduction)andrelatedmatters-tiff2tiffux"><strong>tiff2tiffux</strong></h3><p>Example 1: <strong>reduction</strong> of the bit-depth of TIFFs from the original 32-bit floating-point data type to 8-bit unsigned integer, using a <strong>reference</strong> slice for <strong>implicit</strong> specification of the min and max intensity values<strong><br/></strong></p><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b></b></div><div class="codeContent panelContent pdl">

Linux Command
    >>> tiff2tiffux -b 0 -s 2159 -i recon_129200_%05d.tif -o recon_129200_%05d.tif -u 8 --use_ref -r 1080 -p 0.1 /dls/i13/data/2017/mt16557-1/processing/reconstruction/87637/ /dls/i13/data/2017/mt16557-1/processing/reconstruction/bit_reduced/u8/87637/

.. raw:: html

    </div></div><p>Note the <em>-u 8</em> option being specified above. The input and the output filename formats do not have to be the same, but need to follow the standard Python syntax for formatting strings. In the above example, <em>%05d</em> is used to indicate a 5-character long string representation of integer decimal that is padded with leading zeros as required. In other words, <em>-b 0 -s 2159 -i recon_129200_%05d.tif</em> generates the following series of 2159 input filenames: <em>recon_129200_00000.tif</em>, <em>recon_129200_00001.tif</em>, <em>recon_129200_00002.tif
    </em>,... <em>recon_129200_02157.tif</em>, <em>recon_129200_02158.tif</em> (and, as is the case for this particular example, an identical series of the output filenames, but one could use the <em>-o</em> option to add, for example, the scan number information (which, in this case, happens to be 87637) to the output filenames by specifying <em>-o recon_87637_129200_%05d.tif</em>). For more info on Python string formatting, see for example <a class="external-link" href="https://python-reference.readthedocs.io/en/latest/docs/str/formatting.html" rel="nofollow">https://python-reference.readthedocs.io/en/latest/docs/str/formatting.html</a>. Note also the presence of <em>--use_ref -r 1080</em> for instructing <em>tiff2tiffux </em>to automatically determine the min (<em>--lo</em>) and max (<em>--hi</em>) intensity values from a single reference image, named <em>recon_129200_01080.tif</em> (the index of 1080 is used in this example to select a reasonably-representative reference image from the middle of the series of these 2159 input images).   </p><p><br/></p><p>Example 2: <strong>reduction </strong>of the bit-depth of TIFFs from the original 32-bit floating-point data type to 8-bit unsigned integer, using <strong>explicitly</strong> specified input values for the min (<em>--lo</em>) and max (<em>--hi</em>) intensity values</p><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b></b></div><div class="codeContent panelContent pdl">

Linux Command
    >>> tiff2tiffux -b 0 -s 2159 -i recon_129200_%05d.tif -o recon_129200_%05d.tif -u 8 --lo -0.0016974231 --hi 0.0016586095 /dls/i13/data/2017/mt16557-1/processing/reconstruction/87637/ /dls/i13/data/2017/mt16557-1/processing/reconstruction/bit_reduced/u8/87637/

.. raw:: html

    </div></div><p>Note the <em>-u 8</em> option being specified above.</p><p><br/></p><h2 id="ExtractionofTIFFimagesfromimagedataintheHDFformat(withoptionalbit-depthreduction)andrelatedmatters-Context4:Directoryofraw-datafilesintheTIFFformat(2d)"><strong>Context 4: Directory of raw-data files in the TIFF format (2d)</strong></h2><p>See <strong>Context 3.</strong></p>
                        </div>



                    </div>             </div>

            </div>     </body>
    </html>
