.. _tomo_centre_tomo_recon:

Reconstruction from image data in the HDF format: the tomo-centre and tomo-recon commands
----------------------------------------------------------------------------------------------------------------------

.. raw:: html

    <!DOCTYPE html>
    <html>


        <body class="theme-default aui-theme-default">
            <div id="page">
                <div id="main" class="aui-page-panel">

                    <div id="content" class="view">
                        <div class="page-metadata">



                Created by <span class='author'> Kaz Wanelik</span>
                            </div>
                        <div id="main-content" class="wiki-content group">
                        <p><br/></p><p>

                        <style type='text/css'>/*<![CDATA[*/
    div.rbtoc1592231714796 {padding: 0px;}
    div.rbtoc1592231714796 ul {list-style: disc;margin-left: 0px;}
    div.rbtoc1592231714796 li {margin-left: 0px;padding-left: 0px;}
    .syntaxhighlighter-pre {font-size: small;}
    table {font-size: small;}

    /*]]>*/

    </style><div class='toc-macro rbtoc1592231714796'>
    <ul class='toc-indentation'>
    <li><a href='#ReconstructionfromimagedataintheHDFformat:thetomo-centreandtomo-reconcommands-Introduction'>Introduction</a>
    <ul class='toc-indentation'>
    <li><a href='#ReconstructionfromimagedataintheHDFformat:thetomo-centreandtomo-reconcommands-Logfiles'>Log files</a></li>
    </ul>
    </li>
    <li><a href='#ReconstructionfromimagedataintheHDFformat:thetomo-centreandtomo-reconcommands-tomo-centre'>tomo-centre</a>
    <ul class='toc-indentation'>
    <li><a href='#ReconstructionfromimagedataintheHDFformat:thetomo-centreandtomo-reconcommands-BASICEXAMPLE'>BASIC EXAMPLE</a></li>
    <li><a href='#ReconstructionfromimagedataintheHDFformat:thetomo-centreandtomo-reconcommands-MOSTEXTENSIVEEXAMPLE'>MOST EXTENSIVE EXAMPLE</a></li>
    </ul>
    </li>
    <li><a href='#ReconstructionfromimagedataintheHDFformat:thetomo-centreandtomo-reconcommands-tomo-recon'>tomo-recon</a>
    <ul class='toc-indentation'>
    <li><a href='#ReconstructionfromimagedataintheHDFformat:thetomo-centreandtomo-reconcommands-BASICEXAMPLE.1'>BASIC EXAMPLE</a></li>
    <li><a href='#ReconstructionfromimagedataintheHDFformat:thetomo-centreandtomo-reconcommands-MOSTEXTENSIVEEXAMPLE.1'>MOST EXTENSIVE EXAMPLE</a></li>
    </ul>
    </li>
    <li><a href='#ReconstructionfromimagedataintheHDFformat:thetomo-centreandtomo-reconcommands-tomo-fix'>tomo-fix</a>
    <ul class='toc-indentation'>

    <li><a href='#ReconstructionfromimagedataintheHDFformat:thetomo-centreandtomo-reconcommands-BASICEXAMPLE.2'>BASIC EXAMPLE</a></li>
    <li><a href='#ReconstructionfromimagedataintheHDFformat:thetomo-centreandtomo-reconcommands-MOSTEXTENSIVEEXAMPLE.2'>MOST EXTENSIVE EXAMPLE</a></li>
    </ul>
    </li>
    <li><a href='#ReconstructionfromimagedataintheHDFformat:thetomo-centreandtomo-reconcommands-AppendixA:Ring-artefactsuppression'>Appendix A: Ring-artefact suppression</a></li>
    <li><a href='#ReconstructionfromimagedataintheHDFformat:thetomo-centreandtomo-reconcommands-AppendixB:Optionalbit-depthreductionofoutputTIFFs'>Appendix B: Optional bit-depth reduction of output TIFFs</a></li>
    <li><a href='#ReconstructionfromimagedataintheHDFformat:thetomo-centreandtomo-reconcommands-AppendixC:Batchreconstruction'>Appendix C: Batch reconstruction</a></li>
    <li><a href='#ReconstructionfromimagedataintheHDFformat:thetomo-centreandtomo-reconcommands-AppendixD:Troubleshooting'>Appendix D: Troubleshooting</a></li>
    </ul>
    </div></p><h2 id="ReconstructionfromimagedataintheHDFformat:thetomo-centreandtomo-reconcommands-Introduction"><strong>Introduction</strong></h2><p>The functionality of the <strong>Tomo-Recon GUI</strong> (in Dawn) relies on a number of scripts which can also be executed directly from the Linux command line. This may be necessary if one aims at reconstructing a non-standard tomography dataset or if one would like to improve the quality of reconstructed slices. For example, it can be useful to execute these scripts from the Linux command line in the following situations:</p><ul><li>flat- or dark-field images are stored in separate Nexus datasets or files;</li><li>the information about tomography angles, normally stored in the Nexus scan file, is for some reason missing or inaccurate;</li><li>to optimise ring-artefact suppression (use your own copy of the default settings file, <strong>/dls_sw/apps/tomopy/tomopy/src/settings.xml</strong>, for this task - see <strong>Appendix A</strong>);</li><li>to use some more advanced tomography reconstruction options, specified via settings.xml, e.g. to reduce the bit-depth of output images (use your own copy of the default settings file, <strong>/dls_sw/apps/tomopy/tomopy/src/settings.xml</strong>, for this purpose - see <strong>Appendix B</strong>);</li><li>to run a batch reconstruction of similar scans (see <strong>Appendix C</strong>).</li></ul><p>The scripts form part of a dedicated module, called <em><strong>tomography</strong></em>. As with any other software-environment module in DLS, please execute:</p><p><br/></p><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b>Linux command</b></div><div class="codeContent panelContent pdl">

.. code-block:: console

    module load tomography

.. raw:: html

    </div></div><p>to make all these scripts available in your current Linux session; the scripts include the following items:</p><div class="table-wrap"><table class="wrapped confluenceTable"><colgroup><col/><col/><col/><col/><col/></colgroup><tbody><tr><th class="highlight-blue confluenceTh" data-highlight-colour="blue" style="text-align: center;"><em>Script Name</em></th><th class="highlight-blue confluenceTh" data-highlight-colour="blue" style="text-align: center;"><em>Script Type</em></th><th class="highlight-blue confluenceTh" data-highlight-colour="blue" style="text-align: center;"><em>Script Description</em></th><th class="highlight-blue confluenceTh" colspan="1" data-highlight-colour="blue" style="text-align: center;"><em>Script Usage<br/></em></th><th class="highlight-blue confluenceTh" colspan="1" data-highlight-colour="blue" style="text-align: center;"><em>Comment(s)</em></th></tr><tr><td class="confluenceTd">
    <em>tomo-centre</em></td><td class="confluenceTd">Bash</td><td class="confluenceTd">To find an optimal value of the centre of rotation (CoR).</td><td colspan="1" class="confluenceTd"><pre><em>tomo-centre</em> [options] &lt;nexus_file&gt; &lt;output_directory&gt;</pre></td><td colspan="1" class="confluenceTd"><p>Given a slice number and an initial trial value of CoR, this scripts reconstructs this slice with a series of different values of CoR which are smaller or larger than the input value of CoR. These trial reconstructions facilitate the task of finding an optimal value of CoR by visual inspection. </p><p>The functionality of this script is similar to that of <em>qcentrexml.py</em> for image data in the TIFF format.</p></td></tr><tr><td class="confluenceTd"><em>tomo-recon</em></td><td class="confluenceTd">Bash</td><td class="confluenceTd">To perform tomography reconstruction of data.</td><td colspan="1" class="confluenceTd"><pre><em>tomo-recon</em> [options] &lt;nexus_file&gt; &lt;output_directory&gt;</pre></td><td colspan="1" class="confluenceTd"><p>The functionality of this script is similar to that of <em>recon_arrayxml.py</em> for image data in the TIFF format.</p></td></tr><tr><td colspan="1" class="confluenceTd"><em>tomo-fix</em></td><td colspan="1" class="confluenceTd">Bash</td><td colspan="1" class="confluenceTd">To detect and, if necessary, generate any missing reconstructed images (this is required, for example, if a cluster node is down or in similar circumstances).</td><td colspan="1" class="confluenceTd"><pre><em>tomo-fix</em> [options] &lt;nexus_file&gt; &lt;directory_to_check&gt;</pre></td><td colspan="1" class="confluenceTd">This script is <strong>automatically</strong> executed whenever<em> tomo-recon</em> is run.</td></tr></tbody></table></div><p><br/></p><p>Please note that <strong>absolute paths</strong> need to be supplied for the &lt;nexus_file&gt;, &lt;output_directory&gt;, and &lt;directory_to_check&gt; arguments. Please also note that the input &lt;nexus_file&gt; must contain a well-formed <strong><em>tomo_entry</em></strong>, described in more detail on <a href="Image-data-in-the-HDF-format_17827236.html">Image data in the HDF format</a>.</p><p></p><p></p><div class="confluence-information-macro confluence-information-macro-warning"><p class="title">Important note</p><span class="aui-icon aui-icon-small aui-iconfont-error confluence-information-macro-icon"></span><div class="confluence-information-macro-body"><p>If you copy-and-paste any commands or code from this page, please make sure that all your input arguments are correct before executing anything. In particular, please make sure that the relevant input arguments match the size of your images and that all your input paths to files or directories point to some existing and accessible objects on the file system.</p></div></div><div class="confluence-information-macro confluence-information-macro-tip"><p class="title">Tip</p><span class="aui-icon aui-icon-small aui-iconfont-approve confluence-information-macro-icon"></span><div class="confluence-information-macro-body"><p>The easiest way to select (for copying) a long command displayed in a code-block is to <strong>double-click</strong> anywhere on this command's text.</p></div></div><p></p><h3 id="ReconstructionfromimagedataintheHDFformat:thetomo-centreandtomo-reconcommands-Logfiles"><strong>Log files<br/></strong></h3><p>Recent<strong> log files</strong> can be found in a relevant sub-directory of the <strong><em>/dls/tmp/tomopy</em></strong> directory:</p><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b>Linux command</b></div><div class="codeContent panelContent pdl">
    <pre class="syntaxhighlighter-pre" data-syntaxhighlighter-params="brush: java; gutter: false; theme: Confluence" data-theme="Confluence">~&gt;cd /dls/tmp/tomopy/
    ~&gt;ll
    total 27560
    drwxrwxrwx. 2 ssg37927 ssg37927  3313664 Jul  7 16:05 dt64
    ...
    drwxrwxrwx. 2 vxu94780 vxu94780  5787648 Jul  7 17:44 tomo-centre
    drwxrwxrwx. 2 vxu94780 vxu94780   118784 Jul  4 21:13 tomo-compress
    drwxrwxrwx. 2 fsy24678 fsy24678 18866176 Jul  7 13:08 tomo-recon
    ~&gt;</pre>
    </div></div><p></p><hr/><p></p><h2 id="ReconstructionfromimagedataintheHDFformat:thetomo-centreandtomo-reconcommands-tomo-centre"><strong>tomo-centre</strong></h2><p><br/>The <em>tomo-centre</em> script expects a certain number of arguments and provides some additional options to choose from. When executed, it first creates an appropriate Linux environment and then invokes a Python script called <em>selection_recon.py</em>. All the input arguments and options, supplied for running <em>tomo-centre,</em> are passed in to <em>selection_recon.py</em>. As usual, a more detailed description of all those arguments and options can be viewed by executing:</p><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b>Linux command</b></div><div class="codeContent panelContent pdl">
    <pre class="syntaxhighlighter-pre" data-syntaxhighlighter-params="brush: java; gutter: false; theme: Confluence" data-theme="Confluence">tomo-centre --help</pre>
    </div></div><p>or</p><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b>Linux command</b></div><div class="codeContent panelContent pdl">
    <pre class="syntaxhighlighter-pre" data-syntaxhighlighter-params="brush: java; gutter: false; theme: Confluence" data-theme="Confluence">tomo-centre -h</pre>
    </div></div><p><br/>At the time of writing this section (18 Sep 2017), either of the above two commands outputs the following description:</p><div class="preformatted panel" style="border-width: 1px;"><div class="preformattedContent panelContent">


.. code-block:: console

    tomo-centre -h

             Welcome to the DLS compute cluster

             For MPI jobs, please use 'module load openmpi'.

             If using a different OpenMPI installation,
             or manually specifying path to OpenMPI, option
             '-mca orte_forward_job_control'
             must be added to mpirun to ensure cluster functionality.

             Please report any issues to linux.manager@diamond.ac.uk

    Loading 64-bit Oracle instantclient, version 11.2
    Loading 64-bit python, version 2.7.2
    Loading 64-bit numpy, version 1.6.1
    Usage: selection_recon.py [options] data output_directory

    Options:
      -h, --help            show this help message and exit
      -m MACHINES, --machines=MACHINES
                            Number of machines to deploy to
      -s SLICE, --slice=SLICE
                            Slice selected for processing
      -t TEMPLATE, --template=TEMPLATE
                            Template XML file
      -w WSAMP, --width_sample=WSAMP
                            Set the subsampling of the sinograms width
      -l LSAMP, --length_sample=LSAMP
                            Set the subsampling of the sinograms length
      -c CSTART, --cstart=CSTART
                            Starting value for the centre of rotation
      --ctot=CTOT           Total number of different values for the centre of
                            rotation
      --cstep=CSTEP         The step between two consecutive values for the centre
                            of rotation
      -r RUN_SLICES, --run_slices_loc=RUN_SLICES
                            set the run_slices.sh location
      -n, --new_cluster     use the new cluster
      --dark_file=DARK_FILE
                            Path to the file containing dark images
      --dark_path=DARK_PATH
                            path in the dark file to the data
      --flat_file=FLAT_FILE
                            Path to the file containing flat images
      --flat_path=FLAT_PATH
                            path in the dark file to the data
      --recon_range=RECON_RANGE
                            range for the reconstruction to be done over
      --d0f1                If option included (True), use 0's for dark- and 1's
                            for flat-field images
      --scan_id             If option included (True), incorporate the ID of the
                            input Nexus scan file into output filenames

.. raw:: html

   </div><p><br/></p><p><br/></p><div class="table-wrap"><table class="wrapped fixed-table confluenceTable"><colgroup><col style="width: 125.0px;"/><col style="width: 424.0px;"/><col style="width: 1603.0px;"/></colgroup><tbody><tr><th class="highlight-blue confluenceTh" data-highlight-colour="blue" style="text-align: center;"><em>Option Switch</em></th><th class="highlight-blue confluenceTh" data-highlight-colour="blue" style="text-align: center;"><em>Option's Default Value</em></th><th class="highlight-blue confluenceTh" data-highlight-colour="blue" style="text-align: center;"><em>Comment(s)</em></th></tr><tr><td class="confluenceTd"><pre>-m</pre></td><td class="confluenceTd"><pre>2</pre></td><td class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd">-s</td><td colspan="1" class="confluenceTd">None (Python keyword)</td><td colspan="1" class="confluenceTd">Slice number must be less than the vertical size (in pixels) of the images. </td></tr><tr><td class="confluenceTd"><pre>-t</pre></td><td class="confluenceTd"><pre>/dls_sw/apps/tomopy/tomopy/src/settings.xml</pre></td><td class="confluenceTd"><pre>1. Absolute path needs to be supplied (if different from default).<br/>2. Equivalent to --template.</pre></td></tr><tr><td class="confluenceTd"><pre>-w</pre></td><td class="confluenceTd"><pre>1</pre></td><td class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd"><pre>-l</pre></td><td colspan="1" class="confluenceTd"><pre>1</pre></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd"><pre>-c</pre></td><td colspan="1" class="confluenceTd"><pre>2004</pre></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd"><pre>-r</pre></td><td colspan="1" class="confluenceTd"><pre>/dls_sw/apps/tomopy/tomopy/bin/run_slices.sh</pre></td><td colspan="1" class="confluenceTd"><pre>Path to a tomography reconstruction script to be used (advanced users only).</pre></td></tr><tr><td colspan="1" class="confluenceTd"><pre>-n</pre></td><td colspan="1" class="confluenceTd"><pre>False</pre></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd"><pre>--dark_file</pre></td><td colspan="1" class="confluenceTd"><pre>n/a</pre></td><td colspan="1" class="confluenceTd"><pre>1. Path to the Nexus file containing dark-field images.<br/>2. Do not specify this path if dark-field images are in the same Nexus file as projections.</pre></td></tr><tr><td colspan="1" class="confluenceTd"><pre>--dark_path</pre></td><td colspan="1" class="confluenceTd"><pre>/entry1/pco1_hw_hdf/data</pre></td><td colspan="1" class="confluenceTd"><pre>1. To be supplied only if --dark_file option is used (see --dark_file).<br/>2. Nexus path to dark-field data residing in the file specified by --dark_file, eg /entry1/instrument/pco1_hw_hdf_nochunking/data. If in doubt, use Dawn or hdfview to verify it.<br/>3. Data must contain only dark-field images (if image key is present, it is ignored). <br/>4. These external dark-field images override any internal dark-field images that may be stored alongside projections in &lt;nexus_file&gt;.</pre></td></tr><tr><td colspan="1" class="confluenceTd"><pre>--flat_file</pre></td><td colspan="1" class="confluenceTd"><pre>n/a</pre></td><td colspan="1" class="confluenceTd"><pre>1. Path to the Nexus file containing flat-field images.<br/>2. Do not specify this path if flat-field images are in the same Nexus file as projections.</pre></td></tr><tr><td colspan="1" class="confluenceTd"><pre>--flat_path</pre></td><td colspan="1" class="confluenceTd"><pre>/entry1/pco1_hw_hdf/data</pre></td><td colspan="1" class="confluenceTd"><pre>1. To be supplied only if --flat_file option is used (see --flat_file).<br/>2. Nexus path to flat-field data residing in the file specified by --flat_file, eg /entry1/instrument/pco1_hw_hdf_nochunking/data. If in doubt, use Dawn or hdfview to verify it.<br/>3. Data must contain only flat-field images (if image key is present, it is ignored). <br/>4. These external flat-field images override any internal flat-field images that may be stored alongside projections in &lt;nexus_file&gt;.</pre></td></tr><tr><td colspan="1" class="confluenceTd"><pre>--recon_range</pre></td><td colspan="1" class="confluenceTd"><pre>-1</pre></td><td colspan="1" class="confluenceTd"><pre>If default is used, angular range is automatically determined from rotation-angle data stored in the input Nexus file, ie &lt;nexus_file&gt;. <br/>This option is particularly useful for limited-angle reconstruction. </pre></td></tr><tr><td colspan="1" class="confluenceTd"><pre>--d0f1 </pre></td><td colspan="1" class="confluenceTd"><pre>False (implicit)</pre></td><td colspan="1" class="confluenceTd"><pre>If this option is included on the command line, then a synthetic dark-field image consisting of all 0's and another synthetic flat-field image of all 1's are used during <br/>reconstruction. This work-around enables one to reconstruct datasets that have been dark-and-flat-field-corrected beforehand. </pre></td></tr><tr><td colspan="1" class="confluenceTd"><pre>--scan_id</pre></td><td colspan="1" class="confluenceTd"><pre>False (implicit)</pre></td><td colspan="1" class="confluenceTd"><pre>If this option is included on the command line, then the scan ID is automatically included in the output filenames, eg for Nexus scan file 91809.nxs, a typical output filename <br/>would be recon_91809_127850_02032.tif (as opposed to recon_127850_02032.tif). </pre></td></tr></tbody></table></div><p><br/></p><h3 id="ReconstructionfromimagedataintheHDFformat:thetomo-centreandtomo-reconcommands-BASICEXAMPLE"><strong><span style="color: rgb(0,128,0);">BASIC</span> EXAMPLE<br/></strong></h3><p><strong><br/></strong></p><p>In most cases, <span style="color: rgb(0,128,0);">basic</span> use of <em>tomo-centre</em> is adequate.<strong> </strong></p><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b>Linux command</b></div><div class="codeContent panelContent pdl">
    <pre class="syntaxhighlighter-pre" data-syntaxhighlighter-params="brush: java; gutter: false; theme: Confluence" data-theme="Confluence">tomo-centre -s 1000 -c 1269.5 --ctot 10 --cstep 0.1 -n /dls/i13/data/2014/mt9377-2/raw/29384.nxs /dls/i13/data/2014/mt9377-2/processing/reconstruction/29384/</pre>
    </div></div><p><br/></p><p style="text-align: left;">In the above <span style="color: rgb(0,128,0);"><strong>basic</strong></span> example, the command structure is as follows:</p><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b>Usage</b></div><div class="codeContent panelContent pdl">
    <pre class="syntaxhighlighter-pre" data-syntaxhighlighter-params="brush: java; gutter: false; theme: Confluence" data-theme="Confluence">tomo-centre [options] &lt;nexus_file&gt; &lt;output_directory&gt;</pre>
    </div></div><div class="table-wrap"><table class="wrapped confluenceTable"><colgroup><col/><col/><col/></colgroup><tbody><tr><th class="highlight-blue confluenceTh" colspan="1" data-highlight-colour="blue" style="text-align: center;"><em>Command Argument(s)</em></th><th class="highlight-blue confluenceTh" colspan="1" data-highlight-colour="blue" style="text-align: center;"><em>Example <em>Command Argument(s)</em></em></th><th class="highlight-blue confluenceTh" colspan="1" data-highlight-colour="blue" style="text-align: center;"><em>Comment(s)</em></th></tr><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow"><span class="confluence-link">[options</span>]</th><td class="confluenceTd"><pre>-s 1000 <br/>-c 1269.5 --ctot 10 --cstep 0.1 <br/>-n </pre></td><td colspan="1" class="confluenceTd">SLICE (used by the s-option) should not exceed the (pixel) height of raw images.</td></tr><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow">&lt;nexus_file&gt;</th><td class="confluenceTd"><pre>/dls/i13/data/2014/mt9377-2/raw/29384.nxs </pre></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow">&lt;output_directory&gt;</th><td class="confluenceTd"><pre>/dls/i13/data/2014/mt9377-2/processing/reconstruction/29384/ </pre></td><td colspan="1" class="confluenceTd">If this output directory doesn't already exist, it will automatically be created.</td></tr></tbody></table></div><p><br/></p><h3 id="ReconstructionfromimagedataintheHDFformat:thetomo-centreandtomo-reconcommands-MOSTEXTENSIVEEXAMPLE"><strong><span style="color: rgb(51,102,255);">MOST EXTENSIVE</span> EXAMPLE<br/></strong></h3><p><strong><br/></strong></p><p>In more complicated cases, <em>tomo-centre</em> needs to be executed with <span style="color: rgb(51,102,255);"> </span>all or an appropriate selection of additional input arguments.</p><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b>Linux command</b></div><div class="codeContent panelContent pdl">
    <pre class="syntaxhighlighter-pre" data-syntaxhighlighter-params="brush: java; gutter: false; theme: Confluence" data-theme="Confluence">tomo-centre -s 1000 -c 1269.5 --ctot 10 --cstep 0.1 -n --dark_file=/dls/i13/data/2014/mt9377-2/raw/29375.nxs --dark_path=/entry1/pco1_sw/data --flat_file=/dls/i13/data/2014/mt9377-2/raw/29383.nxs --flat_path=/entry1/pco1_sw/data /dls/i13/data/2014/mt9377-2/raw/29384.nxs /dls/i13/data/2014/mt9377-2/processing/reconstruction/29384/ --recon_range=180.0 --template=/dls/i13/data/2014/mt9377-2/processing/drain1/settingsHDF.xml</pre>
    </div></div><p><br/></p><p>In the above <span style="color: rgb(51,102,255);"><strong>most extensive</strong></span> example, the command structure is as follows:</p><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b>Usage</b></div><div class="codeContent panelContent pdl">
    <pre class="syntaxhighlighter-pre" data-syntaxhighlighter-params="brush: java; gutter: false; theme: Confluence" data-theme="Confluence">tomo-centre [options] &lt;nexus_file&gt; &lt;output_directory&gt;</pre>
    </div></div><div class="table-wrap"><table class="wrapped confluenceTable"><colgroup><col/><col/><col/></colgroup><tbody><tr><th class="highlight-blue confluenceTh" colspan="1" data-highlight-colour="blue" style="text-align: center;"><em><em><em>Command</em></em> Argument(s)</em></th><th class="highlight-blue confluenceTh" colspan="1" data-highlight-colour="blue" style="text-align: center;"><em>Example</em> <em><em>Command</em></em> <em>Argument(s)</em></th><th class="highlight-blue confluenceTh" colspan="1" data-highlight-colour="blue" style="text-align: center;"><em>Comment(s)</em></th></tr><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow"><span class="confluence-link">[options</span>]</th><td class="confluenceTd"><pre>-s 1000 <br/>-c 1269.5 --ctot 10 --cstep 0.1 <br/>-n <br/>--dark_file=/dls/i13/data/2014/mt9377-2/raw/29375.nxs --dark_path=/entry1/pco1_sw/data <br/>--flat_file=/dls/i13/data/2014/mt9377-2/raw/29383.nxs --flat_path=/entry1/pco1_sw/data <br/>--recon_range=180.0 <br/>--template=/dls/i13/data/2014/mt9377-2/processing/drain1/settingsHDF.xml</pre></td><td colspan="1" class="confluenceTd">SLICE (used by the s-option) should not exceed the (pixel) height of raw images.</td></tr><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow">&lt;nexus_file&gt;</th><td class="confluenceTd"><pre>/dls/i13/data/2014/mt9377-2/raw/29384.nxs </pre></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow">&lt;output_directory&gt;</th><td class="confluenceTd"><pre>/dls/i13/data/2014/mt9377-2/processing/reconstruction/29384/ </pre></td><td colspan="1" class="confluenceTd">If this output directory doesn't already exist, it will automatically be created.</td></tr></tbody></table></div><p><br/></p><hr/><p></p><p></p><h2 id="ReconstructionfromimagedataintheHDFformat:thetomo-centreandtomo-reconcommands-tomo-recon">

    <strong>tomo-recon</strong>

    </h2><p><br/>The <em>tomo-recon</em> script expects a certain number of arguments and provides some additional options to choose from. When executed, it first creates an appropriate Linux environment and then invokes a Python script called <em>full_recon.py</em>. All the input arguments and options, supplied for running <em>tomo-recon,</em> are passed in to <em>full_recon.py</em>. As usual, a more detailed description of all those arguments and options can be viewed by executing:</p><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b>Linux command</b></div><div class="codeContent panelContent pdl">
    <pre class="syntaxhighlighter-pre" data-syntaxhighlighter-params="brush: java; gutter: false; theme: Confluence" data-theme="Confluence">tomo-recon --help</pre>
    </div></div><p>or</p><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b>Linux command</b></div><div class="codeContent panelContent pdl">
    <pre class="syntaxhighlighter-pre" data-syntaxhighlighter-params="brush: java; gutter: false; theme: Confluence" data-theme="Confluence">tomo-recon -h</pre>
    </div></div><p><br/>At the time of writing this section (18 Sep 2017), either of the above two commands outputs the following description:</p>

.. code-block:: console

        tomo-recon -h

             Welcome to the DLS compute cluster

             For MPI jobs, please use 'module load openmpi'.

             If using a different OpenMPI installation,
             or manually specifying path to OpenMPI, option
             '-mca orte_forward_job_control'
             must be added to mpirun to ensure cluster functionality.

             Please report any issues to linux.manager@diamond.ac.uk

        Loading 64-bit Oracle instantclient, version 11.2
        Loading 64-bit python, version 2.7.2
        Loading 64-bit numpy, version 1.6.1
        Starting Full Recon
        Usage: full_recon.py [options] data output_directory

        Options:
          -h, --help            show this help message and exit
          -m MACHINES, --machines=MACHINES
                                Number of machines to deploy to
          -b SLICE_BEGIN, --slice_begin=SLICE_BEGIN
                                Start Slice number
          -e SLICE_END, --slice_end=SLICE_END
                                End Slice Number
          -t TEMPLATE, --template=TEMPLATE
                                Template XML file
          -w WSAMP, --width_sample=WSAMP
                                Set the subsampling of the sinograms width
          -l LSAMP, --length_sample=LSAMP
                                Set the subsampling of the sinograms length
          -c CENTRE, --centre=CENTRE
                                Set the centre of rotation
          -r RUN_SLICES, --run_slices_loc=RUN_SLICES
                                set the run_slices.sh location
          -n, --new_cluster     use the new cluster
          -p, --preview         Run a preview reconstruction
          -a, --angles          Use angular information to reconstruct, do not use
                                with a ROI
          -o, --old_cluster     Use the old cluster
          --dark_file=DARK_FILE
                                Path to the file containing dark images
          --dark_path=DARK_PATH
                                path in the dark file to the data
          --flat_file=FLAT_FILE
                                Path to the file containing flat images
          --flat_path=FLAT_PATH
                                path in the dark file to the data
          --recon_range=RECON_RANGE
                                range for the reconstruction to be done over
          --d0f1                If option included (True), use 0&#39;s for dark- and 1&#39;s
                                for flat-field images
          --scan_id             If option included (True), incorporate the ID of the
                                input Nexus scan file into output filenames





.. raw:: html

    </pre>
    </div></div><p><br/></p><p><br/></p><div class="table-wrap"><table class="wrapped confluenceTable"><colgroup><col/><col/><col/></colgroup><tbody><tr><th class="highlight-blue confluenceTh" data-highlight-colour="blue" style="text-align: center;"><em>Option Switch</em></th><th class="highlight-blue confluenceTh" data-highlight-colour="blue" style="text-align: center;"><em>Option's Default Value</em></th><th class="highlight-blue confluenceTh" data-highlight-colour="blue" style="text-align: center;"><em>Comment(s)</em></th></tr><tr><td class="confluenceTd"><pre>-m</pre></td><td class="confluenceTd"><pre>2</pre></td><td class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd"><pre>-b</pre></td><td colspan="1" class="confluenceTd"><pre>0</pre></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd"><pre>-e</pre></td><td colspan="1" class="confluenceTd"><pre>128</pre></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td class="confluenceTd"><pre>-t</pre></td><td class="confluenceTd"><pre>/dls_sw/apps/tomopy/tomopy/src/settings.xml</pre></td><td class="confluenceTd"><pre>1. Absolute path needs to be supplied (if different from default). <br/>2. Equivalent to --template.</pre></td></tr><tr><td class="confluenceTd"><pre>-w</pre></td><td class="confluenceTd"><pre>1</pre></td><td class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd"><pre>-l</pre></td><td colspan="1" class="confluenceTd"><pre>1</pre></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd"><pre>-r</pre></td><td colspan="1" class="confluenceTd"><pre>/dls_sw/apps/tomopy/tomopy/bin/run_slices.sh</pre></td><td colspan="1" class="confluenceTd"><pre>Path to a tomography reconstruction script to be used (advanced users).</pre></td></tr><tr><td colspan="1" class="confluenceTd"><pre>-n</pre></td><td colspan="1" class="confluenceTd"><pre>False</pre></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd"><pre>-p</pre></td><td colspan="1" class="confluenceTd"><pre>False</pre></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd"><pre>-a</pre></td><td colspan="1" class="confluenceTd"><pre>False</pre></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd"><pre>-o</pre></td><td colspan="1" class="confluenceTd"><pre>False</pre></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd"><pre>--dark_file</pre></td><td colspan="1" class="confluenceTd"><pre>None (Python keyword)</pre></td><td colspan="1" class="confluenceTd"><pre>1. Path to the Nexus file containing dark-field images.<br/>2. Do not specify this path if dark-field images are in the same Nexus file as projections.</pre></td></tr><tr><td colspan="1" class="confluenceTd"><pre>--dark_path</pre></td><td colspan="1" class="confluenceTd"><pre>/entry1/pco1_hw_hdf/data</pre></td><td colspan="1" class="confluenceTd"><pre>1. To be supplied only if --dark_file option is used (see --dark_file). <br/>2. Nexus path to dark-field data residing in the file specified by --dark_file, eg /entry1/instrument/pco1_hw_hdf_nochunking/data. If in doubt, use Dawn or hdfview to verify it.<br/>3. Data must contain only dark-field images (if image key is present, it is ignored). <br/>4. These external dark-field images override any internal dark-field images that may be stored alongside projections in &lt;nexus_file&gt;.   </pre></td></tr><tr><td colspan="1" class="confluenceTd"><pre>--flat_file</pre></td><td colspan="1" class="confluenceTd"><pre>None (Python keyword)</pre></td><td colspan="1" class="confluenceTd"><pre>1. Path to the Nexus file containing flat-field images.<br/>2. Do not specify this path if flat-field images are in the same Nexus file as projections.</pre></td></tr><tr><td colspan="1" class="confluenceTd"><pre>--flat_path</pre></td><td colspan="1" class="confluenceTd"><pre>/entry1/pco1_hw_hdf/data</pre></td><td colspan="1" class="confluenceTd"><pre>1. To be supplied only if --flat_file option is used (see --flat_file).<br/>2. Nexus path to flat-field data residing in the file specified by --flat_file, eg /entry1/instrument/pco1_hw_hdf_nochunking/data. If in doubt, use Dawn or hdfview to verify it.<br/>3. Data must contain only flat-field images (if image key is present, it is ignored). <br/>4. These external flat-field images override any internal flat-field images that may be stored alongside projections in &lt;nexus_file&gt;.</pre></td></tr><tr><td colspan="1" class="confluenceTd"><pre>--recon_range</pre></td><td colspan="1" class="confluenceTd"><pre>-1</pre></td><td colspan="1" class="confluenceTd"><pre>If default is used, angular range is automatically determined from rotation-angle data stored in the input Nexus file, ie &lt;nexus_file&gt;. </pre><pre>This option is particularly useful for limited-angle reconstruction. </pre></td></tr><tr><td colspan="1" class="confluenceTd"><pre>--d0f1</pre></td><td colspan="1" class="confluenceTd"><pre>False (implicit)</pre></td><td colspan="1" class="confluenceTd"><pre>If this option is included on the command line, then a synthetic dark-field image consisting of all 0's and another synthetic flat-field image of all 1's are used during <br/>reconstruction. This work-around enables one to reconstruct datasets that have been dark-and-flat-field-corrected beforehand. </pre></td></tr><tr><td colspan="1" class="confluenceTd"><pre>--scan_id</pre></td><td colspan="1" class="confluenceTd"><pre>False (implicit)</pre></td><td colspan="1" class="confluenceTd"><pre>If this option is included on the command line, then the scan ID is automatically included in the output filenames, eg for Nexus scan file 91809.nxs, a typical output filename <br/>would be recon_91809_127850_02032.tif (as opposed to recon_127850_02032.tif). </pre></td></tr></tbody></table></div><p><br/></p><h3 id="ReconstructionfromimagedataintheHDFformat:thetomo-centreandtomo-reconcommands-BASICEXAMPLE.1"><strong><span style="color: rgb(0,128,0);">BASIC</span> EXAMPLE<br/></strong></h3><p><br/></p><p>In most cases, <span style="color: rgb(0,128,0);">basic</span> use of <em>tomo-recon</em> is adequate.</p><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b>Linux command</b></div><div class="codeContent panelContent pdl">
    <pre class="syntaxhighlighter-pre" data-syntaxhighlighter-params="brush: java; gutter: false; theme: Confluence" data-theme="Confluence">tomo-recon -m 20 -b 0 -e 2159 -c 1271.1 /dls/i13/data/2014/mt9377-2/raw/30119.nxs /dls/i13/data/2014/mt9377-2/processing/reconstruction/30119/</pre>
    </div></div><p><br/></p><p>In the above <span style="color: rgb(0,128,0);"><strong>basic</strong></span> example, the command structure is as follows:</p><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b>Usage</b></div><div class="codeContent panelContent pdl">
    <pre class="syntaxhighlighter-pre" data-syntaxhighlighter-params="brush: java; gutter: false; theme: Confluence" data-theme="Confluence">tomo-recon [options] &lt;nexus_file&gt; &lt;output_directory&gt;</pre>
    </div></div><div class="table-wrap"><table class="wrapped confluenceTable"><colgroup><col/><col/><col/></colgroup><tbody><tr><th class="highlight-blue confluenceTh" colspan="1" data-highlight-colour="blue" style="text-align: center;"><em><em><em>Command</em></em> Argument(s)</em></th><th class="highlight-blue confluenceTh" colspan="1" data-highlight-colour="blue" style="text-align: center;"><em>Example</em> <em><em><em>Command</em></em> Argument(s)</em></th><th class="highlight-blue confluenceTh" colspan="1" data-highlight-colour="blue" style="text-align: center;"><em>Comment(s)</em></th></tr><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow"><span class="confluence-link">[options</span>]</th><td class="confluenceTd"><pre>-m 20 <br/>-b 0 -e 2159 <br/>-c 1271.1 </pre></td><td colspan="1" class="confluenceTd"><p>SLICE_END (used by the e-option) should not exceed the (pixel) height of raw images.</p></td></tr><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow">&lt;nexus_file&gt;</th><td class="confluenceTd"><pre>/dls/i13/data/2014/mt9377-2/raw/30119.nxs </pre></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow">&lt;output_directory&gt;</th><td class="confluenceTd"><pre>/dls/i13/data/2014/mt9377-2/processing/reconstruction/30119/</pre></td><td colspan="1" class="confluenceTd">This output directory must exist before executing tomo-recon.</td></tr></tbody></table></div><p><br/></p><h3 id="ReconstructionfromimagedataintheHDFformat:thetomo-centreandtomo-reconcommands-MOSTEXTENSIVEEXAMPLE.1"><strong><span style="color: rgb(51,102,255);">MOST EXTENSIVE</span> EXAMPLE<br/></strong></h3><p><br/></p><p>In more complicated cases, <span style="color: rgb(0,128,0);"> </span><em>tomo-recon</em> needs to be executed with <span style="color: rgb(51,102,255);"> </span>all or an appropriate selection of additional input arguments.</p><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b>Linux command</b></div><div class="codeContent panelContent pdl">
    <pre class="syntaxhighlighter-pre" data-syntaxhighlighter-params="brush: java; gutter: false; theme: Confluence" data-theme="Confluence">tomo-recon -m 20 -b 0 -e 2159 -c 1271.1 --dark_file=/dls/i13/data/2014/mt9377-2/raw/29375.nxs --dark_path=/entry1/pco1_sw/data --flat_file=/dls/i13/data/2014/mt9377-2/raw/30535.nxs --flat_path=/entry1/pco1_sw/data --recon_range=180.0 --template=/dls/i13/data/2014/mt9377-2/processing/drain1/settingsHDF.xml /dls/i13/data/2014/mt9377-2/raw/30119.nxs /dls/i13/data/2014/mt9377-2/processing/reconstruction/30119/</pre>
    </div></div><p><br/></p><p>In the above <span style="color: rgb(51,102,255);"><strong>most extensive</strong></span> example, the command structure is as follows:</p><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b>Usage</b></div><div class="codeContent panelContent pdl">
    <pre class="syntaxhighlighter-pre" data-syntaxhighlighter-params="brush: java; gutter: false; theme: Confluence" data-theme="Confluence">tomo-recon [options] &lt;nexus_file&gt; &lt;output_directory&gt;</pre>
    </div></div><div class="table-wrap"><table class="wrapped confluenceTable"><colgroup><col/><col/><col/></colgroup><tbody><tr><th class="highlight-blue confluenceTh" colspan="1" data-highlight-colour="blue" style="text-align: center;"><em><em><em>Command</em></em> Argument(s)</em></th><th class="highlight-blue confluenceTh" colspan="1" data-highlight-colour="blue" style="text-align: center;"><em>Example</em> <em><em><em>Command</em></em> Argument(s)</em></th><th class="highlight-blue confluenceTh" colspan="1" data-highlight-colour="blue" style="text-align: center;"><em>Comment(s)</em></th></tr><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow"><span class="confluence-link">[options</span>]</th><td class="confluenceTd"><pre>-m 20 <br/>-b 0 -e 2159 <br/>-c 1271.1 <br/>--dark_file=/dls/i13/data/2014/mt9377-2/raw/29375.nxs --dark_path=/entry1/pco1_sw/data <br/>--flat_file=/dls/i13/data/2014/mt9377-2/raw/30535.nxs --flat_path=/entry1/pco1_sw/data <br/>--recon_range=180.0 <br/>--template=/dls/i13/data/2014/mt9377-2/processing/drain1/settingsHDF.xml</pre></td><td colspan="1" class="confluenceTd">SLICE_END (used by the e-option) should not exceed the (pixel) height of raw images.</td></tr><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow">&lt;nexus_file&gt;</th><td class="confluenceTd"><pre>/dls/i13/data/2014/mt9377-2/raw/30119.nxs </pre></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow">&lt;output_directory&gt;</th><td class="confluenceTd"><pre>/dls/i13/data/2014/mt9377-2/processing/reconstruction/30119/</pre></td><td colspan="1" class="confluenceTd">This output directory must exist before executing tomo-recon.</td></tr></tbody></table></div><p><br/></p><hr/><p></p><h2 id="ReconstructionfromimagedataintheHDFformat:thetomo-centreandtomo-reconcommands-tomo-fix"><strong>tomo-fix</strong></h2><p><br/>The <em>tomo-fix</em> script expects a certain number of arguments and provides some additional options to choose from. When executed, it first creates an appropriate Linux environment and then invokes a Python script called <em>tomo-fix.py</em>. All the input arguments and options, supplied for running <em>tomo-fix,</em> are passed in to <em>tomo-fix.py</em>. As mentioned at the top of this page, this script is <strong>automatically</strong> executed whenever<em> tomo-recon</em> is run. As usual, a more detailed description of all those arguments and options can be viewed by executing:</p><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b>Linux command</b></div><div class="codeContent panelContent pdl">
    <pre class="syntaxhighlighter-pre" data-syntaxhighlighter-params="brush: java; gutter: false; theme: Confluence" data-theme="Confluence">tomo-fix --help</pre>
    </div></div><p>or</p><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b>Linux command</b></div><div class="codeContent panelContent pdl">
    <pre class="syntaxhighlighter-pre" data-syntaxhighlighter-params="brush: java; gutter: false; theme: Confluence" data-theme="Confluence">tomo-fix -h</pre>
    </div></div><p><br/>At the time of writing this section (18 Sep 2017), either of the above two commands outputs the following description:</p><div class="preformatted panel" style="border-width: 1px;"><div class="preformattedContent panelContent">


.. code-block:: console

    tomo-fix -h

    Loading 64-bit Oracle instantclient, version 11.2
    Loading 64-bit python, version 2.7.2
    Loading 64-bit numpy, version 1.6.1
    Usage: tomo-fix.py [options] nexus_file directory_to_check

    Options:
      --version             show program's version number and exit
      -h, --help            show this help message and exit
      -m MACHINES, --machines=MACHINES
                            Number of machines to deploy to
      -b SLICE_BEGIN, --slice_begin=SLICE_BEGIN
                            Start Slice number
      -e SLICE_END, --slice_end=SLICE_END
                            End Slice Number
      -t TEMPLATE, --template=TEMPLATE
                            Template XML file
      -w WSAMP, --width_sample=WSAMP
                            Set the subsampling of the sinograms width
      -l LSAMP, --length_sample=LSAMP
                            Set the subsampling of the sinograms length
      -c CENTRE, --centre=CENTRE
                            Set the centre of rotation
      -r RUN_SLICES, --run_slices_loc=RUN_SLICES
                            set the run_slices.sh location
      -n, --new_cluster     use the new cluster
      -p, --preview         Run a preview reconstruction
      -a, --angles          Use angular information to reconstruct, do not use
                            with a ROI
      -o, --old_cluster     Use the old cluster
      --dark_file=DARK_FILE
                            Path to the file containing dark images
      --dark_path=DARK_PATH
                            path in the dark file to the data
      --flat_file=FLAT_FILE
                            Path to the file containing flat images
      --flat_path=FLAT_PATH
                            path in the dark file to the data
      --recon_range=RECON_RANGE
                            range for the reconstruction to be done over
      --d0f1                If option included (True), use 0's for dark- and 1's
                            for flat-field images
      --scan_id             If option included (True), incorporate the ID of the
                            input Nexus scan file into output filenames

.. raw:: html

    ~&gt;</pre>
    </div></div><p><br/></p><p><br/></p>

    <div class="table-wrap"><table class="wrapped confluenceTable"><colgroup><col/><col/><col/></colgroup><tbody><tr><th class="highlight-blue confluenceTh" data-highlight-colour="blue" style="text-align: center;"><em>Option Switch</em></th><th class="highlight-blue confluenceTh" data-highlight-colour="blue" style="text-align: center;"><em>Option's Default Value</em></th><th class="highlight-blue confluenceTh" data-highlight-colour="blue" style="text-align: center;"><em>Comment(s)</em></th></tr><tr><td class="confluenceTd"><pre>-m</pre></td><td class="confluenceTd"><pre>2</pre></td><td class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd"><pre>-b</pre></td><td colspan="1" class="confluenceTd"><pre>0</pre></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td class="confluenceTd"><pre>-e</pre></td><td class="confluenceTd"><pre>128</pre></td><td class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd"><pre>-t</pre></td><td colspan="1" class="confluenceTd"><pre>/dls_sw/apps/tomopy/tomopy/src/settings.xml</pre></td><td colspan="1" class="confluenceTd"><pre>1. Absolute path needs to be supplied (if different from default).<br/>2. Equivalent to --template.</pre></td></tr><tr><td colspan="1" class="confluenceTd"><pre>-w</pre></td><td colspan="1" class="confluenceTd"><pre>1</pre></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd"><pre>-l</pre></td><td colspan="1" class="confluenceTd"><pre>1</pre></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd"><pre>-r</pre></td><td colspan="1" class="confluenceTd"><pre>/dls_sw/apps/tomopy/tomopy/bin/run_slices.sh</pre></td><td colspan="1" class="confluenceTd"><pre>Path to a tomography reconstruction script to be used (advanced users).</pre></td></tr><tr><td colspan="1" class="confluenceTd"><pre>-n</pre></td><td colspan="1" class="confluenceTd"><pre>False</pre></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd"><pre>-p</pre></td><td colspan="1" class="confluenceTd"><pre>False</pre></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd"><pre>-a</pre></td><td colspan="1" class="confluenceTd"><pre>False</pre></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd"><pre>-o</pre></td><td colspan="1" class="confluenceTd"><pre>False</pre></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><td colspan="1" class="confluenceTd"><pre>--dark_file</pre></td><td colspan="1" class="confluenceTd"><pre>n/a</pre></td><td colspan="1" class="confluenceTd"><pre>1. Path to the Nexus file containing dark-field images.<br/>2. Do not specify this path if dark-field images are in the same Nexus file as projections.</pre></td></tr><tr><td colspan="1" class="confluenceTd"><pre>--dark_path</pre></td><td colspan="1" class="confluenceTd"><pre>n/a</pre></td><td colspan="1" class="confluenceTd"><pre>1.To be supplied only if --dark_file option is used (see --dark_file).<br/>2. Nexus path to dark-field data residing in the file specified by --dark_file, eg /entry1/instrument/pco1_hw_hdf_nochunking/data. If in doubt, use Dawn or hdfview to verify it.<br/>2. Data must contain only dark-field images (if image key is present, it is ignored). <br/>3. These external dark-field images override any internal dark-field images that may be stored alongside projections in &lt;nexus_file&gt;.</pre></td></tr><tr><td colspan="1" class="confluenceTd"><pre>--flat_file</pre></td><td colspan="1" class="confluenceTd"><pre>n/a</pre></td><td colspan="1" class="confluenceTd"><pre>1. Path to the Nexus file containing flat-field images.<br/>2. Do not specify this path if flat-field images are in the same Nexus file as projections.</pre></td></tr><tr><td colspan="1" class="confluenceTd"><pre>--flat_path</pre></td><td colspan="1" class="confluenceTd"><pre>n/a</pre></td><td colspan="1" class="confluenceTd"><pre>1. To be supplied only if --flat_file option is used (see --flat_file).<br/>2. Nexus path to flat-field data residing in the file specified by --flat_file, eg /entry1/instrument/pco1_hw_hdf_nochunking/data. If in doubt, use Dawn or hdfview to verify it.<br/>3. Data must contain only flat-field images (if image key is present, it is ignored). <br/>4. These external flat-field images override any internal flat-field images that may be stored alongside projections in &lt;nexus_file&gt;.</pre></td></tr><tr><td colspan="1" class="confluenceTd"><pre>--d0f1</pre></td><td colspan="1" class="confluenceTd"><pre>False (implicit)</pre></td><td colspan="1" class="confluenceTd"><pre>If this option is included on the command line, then a synthetic dark-field image consisting of all 0's and another synthetic flat-field image of all 1's are used during <br/>reconstruction. This work-around enables one to reconstruct datasets that have been dark-and-flat-field-corrected beforehand. </pre></td></tr><tr><td colspan="1" class="confluenceTd"><pre>--scan_id</pre></td><td colspan="1" class="confluenceTd"><pre>False (implicit)</pre></td><td colspan="1" class="confluenceTd"><pre>If this option is included on the command line, then the scan ID is automatically included in the output filenames, eg for Nexus scan file 91809.nxs, a typical output filename <br/>would be recon_91809_127850_02032.tif (as opposed to recon_127850_02032.tif).</pre></td></tr></tbody></table></div><h3 id="ReconstructionfromimagedataintheHDFformat:thetomo-centreandtomo-reconcommands-"><span style="color: rgb(0,128,0);"><strong><br/></strong></span></h3><h3 id="ReconstructionfromimagedataintheHDFformat:thetomo-centreandtomo-reconcommands-BASICEXAMPLE.2"><span style="color: rgb(0,128,0);"><strong>BASIC</strong></span> EXAMPLE</h3><p><br/></p><p>In most cases, <span style="color: rgb(0,128,0);">basic</span> use of <em>tomo-fix</em> is adequate.</p><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b>Linux command</b></div><div class="codeContent panelContent pdl">
    <pre class="syntaxhighlighter-pre" data-syntaxhighlighter-params="brush: java; gutter: false; theme: Confluence" data-theme="Confluence">tomo-fix -m 20 -b 0 -e 2159 -c 1271.1 /dls/i13/data/2014/mt9377-2/raw/30119.nxs /dls/i13/data/2014/mt9377-2/processing/reconstruction/30119/</pre>
    </div></div><p><br/></p><p style="text-align: left;">In the above <span style="color: rgb(0,128,0);"><strong>basic</strong></span> example, the command structure is as follows:</p><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b>Usage</b></div><div class="codeContent panelContent pdl">
    <pre class="syntaxhighlighter-pre" data-syntaxhighlighter-params="brush: java; gutter: false; theme: Confluence" data-theme="Confluence">tomo-fix [options] &lt;nexus_file&gt; &lt;directory_to_check&gt;</pre>
    </div></div><div class="table-wrap"><table class="wrapped confluenceTable"><colgroup><col/><col/><col/></colgroup><tbody><tr><th class="highlight-blue confluenceTh" colspan="1" data-highlight-colour="blue" style="text-align: center;"><em><em><em>Command</em></em> Argument(s)</em></th><th class="highlight-blue confluenceTh" colspan="1" data-highlight-colour="blue" style="text-align: center;"><em>Example</em> <em><em><em>Command</em></em> Argument(s)</em></th><th class="highlight-blue confluenceTh" colspan="1" data-highlight-colour="blue" style="text-align: center;"><em>Comment(s)</em></th></tr><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow"><span class="confluence-link">[options</span>]</th><td class="confluenceTd"><pre>-m 20 <br/>-b 0 -e 2159 <br/>-c 1271.1 </pre></td><td colspan="1" class="confluenceTd">SLICE_END (used by the e-option) should not exceed the (pixel) height of raw images.</td></tr><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow">&lt;nexus_file&gt;</th><td class="confluenceTd"><pre>/dls/i13/data/2014/mt9377-2/raw/30119.nxs </pre></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow">&lt;directory_to_check&gt;</th><td class="confluenceTd"><pre>/dls/i13/data/2014/mt9377-2/processing/reconstruction/30119/</pre></td><td colspan="1" class="confluenceTd">This output directory must exist before executing tomo-recon.</td></tr></tbody></table></div><h3 id="ReconstructionfromimagedataintheHDFformat:thetomo-centreandtomo-reconcommands-MOSTEXTENSIVEEXAMPLE.2"><span style="color: rgb(51,102,255);"><strong>MOST EXTENSIVE</strong></span> EXAMPLE</h3><p><br/></p><p>In more complicated cases, <em>tomo-fix</em> needs to be executed with <span style="color: rgb(51,102,255);"> </span>all or an appropriate selection of additional input arguments.</p><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b>Linux command</b></div><div class="codeContent panelContent pdl">
    <pre class="syntaxhighlighter-pre" data-syntaxhighlighter-params="brush: java; gutter: false; theme: Confluence" data-theme="Confluence">tomo-fix -m 20 -b 0 -e 2159 -c 1271.1 --dark_file=/dls/i13/data/2014/mt9377-2/raw/29375.nxs --dark_path=/entry1/pco1_sw/data --flat_file=/dls/i13/data/2014/mt9377-2/raw/30535.nxs --flat_path=/entry1/pco1_sw/data --recon_range=180.0 --template=/dls/i13/data/2014/mt9377-2/processing/drain1/settingsHDF.xml /dls/i13/data/2014/mt9377-2/raw/30119.nxs /dls/i13/data/2014/mt9377-2/processing/reconstruction/30119/</pre>
    </div></div><p><br/></p><p>In the above <span style="color: rgb(51,102,255);"><strong>most extensive</strong> </span>example, the command structure is as follows:</p><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b>Usage</b></div><div class="codeContent panelContent pdl">
    <pre class="syntaxhighlighter-pre" data-syntaxhighlighter-params="brush: java; gutter: false; theme: Confluence" data-theme="Confluence">tomo-fix [options] &lt;nexus_file&gt; &lt;directory_to_check&gt;</pre>
    </div></div><div class="table-wrap"><table class="wrapped confluenceTable"><colgroup><col/><col/><col/></colgroup><tbody><tr><th class="highlight-blue confluenceTh" colspan="1" data-highlight-colour="blue" style="text-align: center;"><em><em><em>Command</em></em> Argument(s)</em></th><th class="highlight-blue confluenceTh" colspan="1" data-highlight-colour="blue" style="text-align: center;"><em>Example</em> <em><em>Command</em></em> <em>Argument(s)</em></th><th class="highlight-blue confluenceTh" colspan="1" data-highlight-colour="blue" style="text-align: center;"><em>Comment(s)</em></th></tr><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow"><span class="confluence-link">[options</span>]</th><td class="confluenceTd"><pre>-m 20 <br/>-b 0 -e 2159 <br/>-c 1271.1 <br/>--dark_file=/dls/i13/data/2014/mt9377-2/raw/29375.nxs --dark_path=/entry1/pco1_sw/data <br/>--flat_file=/dls/i13/data/2014/mt9377-2/raw/30535.nxs --flat_path=/entry1/pco1_sw/data <br/>--recon_range=180.0 <br/>--template=/dls/i13/data/2014/mt9377-2/processing/drain1/settingsHDF.xml</pre></td><td colspan="1" class="confluenceTd"><p>SLICE_END (used by the e-option) should not exceed the (pixel) height of raw images.</p></td></tr><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow">&lt;nexus_file&gt;</th><td class="confluenceTd"><pre>/dls/i13/data/2014/mt9377-2/raw/30119.nxs </pre></td><td colspan="1" class="confluenceTd"><br/></td></tr><tr><th class="highlight-yellow confluenceTh" data-highlight-colour="yellow">&lt;directory_to_check&gt;</th><td class="confluenceTd"><pre>/dls/i13/data/2014/mt9377-2/processing/reconstruction/30119/</pre></td><td colspan="1" class="confluenceTd">This output directory must exist before executing tomo-recon.</td></tr></tbody></table></div><p><br/></p><p><br/></p><h2 id="ReconstructionfromimagedataintheHDFformat:thetomo-centreandtomo-reconcommands-AppendixA:Ring-artefactsuppression"><strong>Appendix A</strong><strong>: Ring-artefact suppression</strong></h2><p>Ring-artefact suppression can be performed as part of the reconstruction process with the help of an appropriately configured settings.xml. Note that the default <strong>/dls_sw/apps/tomopy/tomopy/src/settings.xml</strong> has ring-artefact suppression enabled with the following parameters: </p><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b> /dls_sw/apps/tomopy/tomopy/src/settings.xml (part)</b></div><div class="codeContent panelContent pdl">
    <pre class="syntaxhighlighter-pre" data-syntaxhighlighter-params="brush: java; gutter: false; theme: Confluence" data-theme="Confluence">...
    &lt;RingArtefacts&gt;
       &lt;Type info=&quot;No, Column, AML&quot;&gt;AML&lt;/Type&gt;
       &lt;ParameterN&gt;0.000&lt;/ParameterN&gt;
       &lt;ParameterR&gt;0.0050&lt;/ParameterR&gt;
       &lt;NumSeries info=&quot;1 - default, if greater, then nonlinear&quot;&gt;1.0&lt;/NumSeries&gt;
    &lt;/RingArtefacts&gt;
    ...</pre>
    </div></div><p>To optimise ring-artefact suppression, you need to first modify the <em>ParameterR</em> or <em>NumSeries</em> parameters in your own<strong> copy</strong> of the default <strong>/dls_sw/apps/tomopy/tomopy/src/settings.xml</strong> and then explicitly specify a path to this modified <strong>copy</strong> to run <em>tomo-recon</em> (use the t-option) in order to reconstruct a few representative slices for subsequent visual inspection (this workflow is similar to that employed for finding an optimal value of CoR)<strong>. </strong><em>ParameterR</em> controls the strength of ring-artefact suppression, and it is best to change it in order-of-magnitude steps, e. g. 0.5, 0.05, 0.005 (default), 0.0005. Note that the smaller <em>ParameterR,</em> the more aggressive ring-artefact suppression. <em>NumSeries </em>is used for controlling the high-aspect-ratio compensation (for plate-like samples). </p><p>If desired, ring-suppression can be completely switched off by changing <strong><em>Type</em></strong> (from the default value of <strong>AML)</strong> to <strong>No</strong>:</p><div class="code panel pdl" style="border-width: 1px;"><div class="codeContent panelContent pdl">
    <pre class="syntaxhighlighter-pre" data-syntaxhighlighter-params="brush: java; gutter: false; theme: Confluence" data-theme="Confluence">...
    &lt;RingArtefacts&gt;
       &lt;Type info=&quot;No, Column, AML&quot;&gt;No&lt;/Type&gt;
       &lt;ParameterN&gt;0.000&lt;/ParameterN&gt;
       &lt;ParameterR&gt;0.0050&lt;/ParameterR&gt;
       &lt;NumSeries info=&quot;1 - default, if greater, then nonlinear&quot;&gt;1.0&lt;/NumSeries&gt;
    &lt;/RingArtefacts&gt;
    ...</pre>
    </div></div><p><strong><br/></strong></p><h2 id="ReconstructionfromimagedataintheHDFformat:thetomo-centreandtomo-reconcommands-AppendixB:Optionalbit-depthreductionofoutputTIFFs"><strong>Appendix B</strong><strong>: Optional bit-depth reduction of output TIFFs</strong></h2><p>Bit-depth reduction can be performed as part of the reconstruction process with the help of an appropriately configured <strong>settings.xml</strong>:</p><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b> /dls_sw/apps/tomopy/tomopy/src/settings.xml (part)</b></div><div class="codeContent panelContent pdl">
    <pre class="syntaxhighlighter-pre" data-syntaxhighlighter-params="brush: java; gutter: false; theme: Confluence" data-theme="Confluence">...
    &lt;OutputData&gt;
      ...
      &lt;BitsType info=&quot;Input, Given&quot;&gt;Given&lt;/BitsType&gt;
      &lt;Bits&gt;32&lt;/Bits&gt;
      &lt;Restrictions info=&quot;Yes, No&quot;&gt;No&lt;/Restrictions&gt;
      &lt;ValueMin&gt;0.5&lt;/ValueMin&gt;
      &lt;ValueMax&gt;1.1&lt;/ValueMax&gt;
      ...
    &lt;/OutputData&gt;
    ...</pre>
    </div></div><p>The above snippet of XML shows the default (32-bit) settings (in the default <strong>/dls_sw/apps/tomopy/tomopy/src/settings.xml</strong> file). Before modifying these settings (in your own <strong>copy</strong> of the default <strong>/dls_sw/apps/tomopy/tomopy/src/settings.xml</strong>), it is crucial to find some sensible replacement values for the above <em><strong>ValueMin</strong></em> and <em><strong>ValueMax</strong>.</em> Since these values are image-dependent, it is best to select them with the help of a histogram (e.g. in ImageJ) of your typical, 32-bit reconstructed slice.  </p><p>Alternatively, bit-depth reduction can be done after the reconstruction process, as described in

:ref:`Extraction of TIFF images from image data in the HDF format (with optional bit-depth reduction) and related matters<extraction_tiff_images>`


.. raw:: html

    <strong></strong></p><p><strong></strong></p>
    <h2 id="ReconstructionfromimagedataintheHDFformat:thetomo-centreandtomo-reconcommands-AppendixC:Batchreconstruction">
    <strong>Appendix C</strong><strong>: Batch reconstruction</strong></h2><p>It is sometimes desirable to reconstruct a batch of similar tomography scans. The Bash script presented below provides a simple example of how to do it for a sequence of consecutive scans sharing the <strong>same</strong> centre of rotation. More precisely, this script reconstructs a batch of 4 consecutive scans, numbered from 10000 to 10003, using the same centre of rotation, 1234.5, and the same flat- and dark-field datasets, stored in 2 separate Nexus files (one for flats and the other for darks). The values of 0 and 2159 for the <em>b</em> and, respectively, the <em>e</em> option have been chosen to match the full size of images produced by PCO Edge.</p><p>Please note that, to prevent the DLS compute cluster from getting overloaded, the script reconstructs scans <strong>one</strong> <strong>after </strong><strong>another</strong> (sequentially) as opposed to reconstructing all scans in parallel at the same time.   </p><p><br/></p><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b>Batch Example 1</b></div>
    <div class="codeContent panelContent pdl">
    <pre class="syntaxhighlighter-pre" data-syntaxhighlighter-params="brush: bash; gutter: false; theme: Confluence" data-theme="Confluence">#! /bin/bash

    echo &quot;Running batch reconstruction...&quot;

    ### USER INPUT: START
    # What is your visit&#39;s ID and year?
    visitID=&quot;xx12345-6&quot;
    year=2016

    # What is the COMMON centre of rotation for all the scans?
    CENTRE=1234.5

    # What is the first scan number?
    START=10000

    # What is the last scan number?
    END=10003

    # Which directory contains the scans (with sample projections)?
    RAWDIR=&quot;/dls/i13/data/${year}/${visitID}/raw&quot;

    # Which directory contains the flat scan?
    FLATDIR=&quot;/dls/i13/data/${year}/${visitID}/raw&quot;

    # What is the flat-scan number?
    FLAT=11111

    # Which directory contains the dark scan?
    DARKDIR=&quot;/dls/i13/data/${year}/${visitID}/raw&quot;

    # What is the dark-scan number?
    DARK=66666

    # Which directory is to be used for saving reconstructed images in scan-numbered sub-directories?
    PRODIR=&quot;/dls/i13/data/${year}/${visitID}/processing/reconstruction&quot;
    ### USER INPUT: END

    module add tomography

    echo &quot;BATCH START = ${START}&quot;
    echo &quot;BATCH END = ${END}&quot;

    for (( i=$START; i&lt;=$END; i++ ))

    do
        cd $PRODIR
        echo &quot;in directory: &quot;`pwd`
        echo &quot;making reconstruction directory for scan: $i&quot;
        [ -d $i ] || mkdir $i
        echo &quot;reconstructing scan: $i&quot;
        echo &quot;tomo-recon command is:&quot;
        # the next two lines print out the command before it is executed (in the 3rd line), which is useful for testing, etc
        echo \
        tomo-recon -m 20 -b 0 -e 2159 -c $CENTRE --dark_file=$DARKDIR/$DARK.nxs --dark_path=/entry1/pco1_hw_hdf_nochunking/data --flat_file=$FLATDIR/$FLAT.nxs --flat_path=/entry1/pco1_hw_hdf_nochunking/data $RAWDIR/$i.nxs $PRODIR/$i/ --recon_range=180.0 --template=/dls/i13/data/2014/visitID/processing/settingsHDF.xml
        tomo-recon -m 20 -b 0 -e 2159 -c $CENTRE --dark_file=$DARKDIR/$DARK.nxs --dark_path=/entry1/pco1_hw_hdf_nochunking/data --flat_file=$FLATDIR/$FLAT.nxs --flat_path=/entry1/pco1_hw_hdf_nochunking/data $RAWDIR/$i.nxs $PRODIR/$i/ --recon_range=180.0 --template=/dls/i13/data/2014/visitID/processing/settingsHDF.xml

        echo &quot;finished reconstructing scan: $i&quot;
    done

    echo &quot;Finished batch reconstruction.&quot;</pre>
    </div></div><p><br/></p><p>If your batch contains scans which are <strong>not</strong> consecutively numbered or if they do <strong>not</strong> share the common centre of rotation, then the script presented below can be used to reconstruct such a batch. More precisely, this script reconstructs a batch of 2 non-consecutive scans, numbered 10000 and 10003, using 2 different centres of rotation (1234.5 and 5432.1, respectively), and the same flat- and dark-field datasets, stored in 2 separate Nexus files (one for flats and the other for darks):</p><p><br/></p><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b>Batch Example 2</b></div><div class="codeContent panelContent pdl">
    <pre class="syntaxhighlighter-pre" data-syntaxhighlighter-params="brush: bash; gutter: false; theme: Confluence" data-theme="Confluence">#! /bin/bash

    echo &quot;Running batch reconstruction...&quot;

    # Declare associative array
    declare -A arr

    ### USER INPUT: START
    # What is your visit&#39;s ID and year?
    visitID=&quot;xx12345-6&quot;
    year=2016

    # What are your scan numbers and the corresponding centres of rotations?
    # TEMPLATE: arr[scan_number]=centre_of_rotation
    arr[10000]=1234.5
    arr[10003]=5432.1

    # Which directory contains the scans (with sample projections)?
    RAWDIR=&quot;/dls/i13/data/${year}/${visitID}/raw&quot;

    # Which directory contains the flat scan?
    FLATDIR=&quot;/dls/i13/data/${year}/${visitID}/raw&quot;

    # What is the flat-scan number?
    FLAT=11111

    # Which directory contains the dark scan?
    DARKDIR=&quot;/dls/i13/data/${year}/${visitID}/raw&quot;

    # What is the dark-scan number?
    DARK=66666

    # Which directory is to be used for saving reconstructed images in scan-numbered sub-directories?
    PRODIR=&quot;/dls/i13/data/${year}/${visitID}/processing/reconstruction&quot;
    ### USER INPUT: END

    module add tomography
    echo &quot;BATCH:&quot;
    item=1
    for i in ${!arr[@]]}
    do
       echo ${item}. scan=${i} CoR=${arr[${i}]}
       item=$((item+1))
    done

    for i in ${!arr[@]]}

    do
        cd $PRODIR
        echo &quot;in directory: &quot;`pwd`
        echo &quot;making reconstruction directory for scan: $i&quot;
        [ -d $i ] || mkdir $i
        echo &quot;reconstructing scan: $i&quot;
        echo &quot;tomo-recon command is:&quot;
        # the next two lines print out the command before it is executed (in the 3rd line), which is useful for testing, etc
        echo \
        tomo-recon -m 20 -b 0 -e 2159 -c ${arr[${i}]} --dark_file=$DARKDIR/$DARK.nxs --dark_path=/entry1/pco1_hw_hdf_nochunking/data --flat_file=$FLATDIR/$FLAT.nxs --flat_path=/entry1/pco1_hw_hdf_nochunking/data $RAWDIR/$i.nxs $PRODIR/$i/ --recon_range=180.0 --template=/dls/i13/data/2014/visitID/processing/settingsHDF.xml
        tomo-recon -m 20 -b 0 -e 2159 -c ${arr[${i}]} --dark_file=$DARKDIR/$DARK.nxs --dark_path=/entry1/pco1_hw_hdf_nochunking/data --flat_file=$FLATDIR/$FLAT.nxs --flat_path=/entry1/pco1_hw_hdf_nochunking/data $RAWDIR/$i.nxs $PRODIR/$i/ --recon_range=180.0 --template=/dls/i13/data/2014/visitID/processing/settingsHDF.xml

        echo &quot;finished reconstructing scan: $i&quot;
    done

    # Clear the array
    unset arr

    echo &quot;Finished batch reconstruction.&quot;</pre>
    </div></div><p><br/></p><p>To use either of these two example scripts for batch processing, please follow these steps:</p><ul><li>copy-and-paste the above code into your own <em>.sh</em> file (e.g. mybatch.sh);</li><li>modify the script in this file to suit your particular needs, making sure that all input arguments match the size of your images and that all input paths to files or directories point to some existing and accessible objects (the script automatically creates the output directory, if it does not exist);  </li><li>save the file;</li><li>make the file executable (e.g. chmod u+x mybatch.sh);</li><li>execute the script (e.g. ./mybatch.sh)</li></ul><p>It is always a good practice to first <strong>test</strong> your new script without running any jobs on the compute cluster. This can be accomplished by commenting out (c.f. the leading <span style="color: rgb(0,128,0);">#</span>) the <strong>last</strong> occurrence of the two <strong>identical</strong> lines beginning with 'tomo-recon', i.e.        </p><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b>Batch testing</b></div><div class="codeContent panelContent pdl">
    <pre class="syntaxhighlighter-pre" data-syntaxhighlighter-params="brush: bash; gutter: false; theme: Confluence" data-theme="Confluence">echo \
    tomo-recon -m 20 -b 0 -e 2159 -c $CENTRE --dark_file=$DARKDIR/$DARK.nxs --dark_path=/entry1/pco1_hw_hdf_nochunking/data --flat_file=$FLATDIR/$FLAT.nxs --flat_path=/entry1/pco1_hw_hdf_nochunking/data $RAWDIR/$i.nxs $PRODIR/$i/ --recon_range=180.0 --template=/dls/i13/data/2014/visitID/processing/settingsHDF.xml
    #tomo-recon -m 20 -b 0 -e 2159 -c $CENTRE --dark_file=$DARKDIR/$DARK.nxs --dark_path=/entry1/pco1_hw_hdf_nochunking/data --flat_file=$FLATDIR/$FLAT.nxs --flat_path=/entry1/pco1_hw_hdf_nochunking/data $RAWDIR/$i.nxs $PRODIR/$i/ --recon_range=180.0 --template=/dls/i13/data/2014/visitID/processing/settingsHDF.xml</pre>
    </div></div><p><br/></p><p>Please note that the first occurrence of this line simply prints out the intended <em>tomo-recon</em> command with its expanded arguments (which is useful for spotting any typos, etc), whereas the second occurrence would normally execute this command for real, sending a number of jobs to run on the compute cluster. This <strong>dry run</strong> should help one verify that all input arguments are correct and that all input paths to files or directories point to some existing and accessible objects on the file system (the script automatically creates the output directory, if the latter does not already exist). If no problems are detected with the script, then the commented-out line needs, of course, to be commented back in before the script can be executed for real.  </p><p><br/></p><h2 id="ReconstructionfromimagedataintheHDFformat:thetomo-centreandtomo-reconcommands-AppendixD:Troubleshooting"><strong>Appendix D: Troubleshooting</strong></h2><p>If the reconstruction scripts do not produce any output files, experienced users can find the logs at the following location:</p><div class="code panel pdl" style="border-width: 1px;"><div class="codeHeader panelHeader pdl" style="border-bottom-width: 1px;"><b>log file directories</b></div><div class="codeContent panelContent pdl">
    <pre class="syntaxhighlighter-pre" data-syntaxhighlighter-params="brush: java; gutter: false; theme: Confluence" data-theme="Confluence">/dls/tmp/tomopy/tomo-centre/
    /dls/tmp/tomopy/tomo-recon/</pre>
    </div></div><p>For finding the latest log files, sort the contents and open the logfile for example with gedit:</p><div class="code panel pdl" style="border-width: 1px;"><div class="codeContent panelContent pdl">
    <pre class="syntaxhighlighter-pre" data-syntaxhighlighter-params="brush: java; gutter: false; theme: Confluence" data-theme="Confluence">[user@machine tomo-centre]$ ls -lthr
    -rw-r--r--. 1 fedid123 fedid123    0 Feb 13 15:43 run_slices.sh.po22535829
    -rw-r--r--. 1 fedid123 fedid123    0 Feb 13 15:43 run_slices.sh.pe22535829
    -rw-r--r--. 1 fedid123 fedid123  599 Feb 13 15:43 run_slices.sh.e22535827
    -rw-r--r--. 1 fedid123 fedid123  599 Feb 13 15:43 run_slices.sh.e22535828
    -rw-r--r--. 1 fedid123 fedid123  599 Feb 13 15:43 run_slices.sh.e22535829
    -rw-r--r--. 1 fedid123 fedid123  599 Feb 13 15:43 run_slices.sh.e22535826
    -rw-r--r--. 1 fedid123 fedid123 4.1K Feb 13 15:43 run_slices.sh.o22535829
    -rw-r--r--. 1 fedid123 fedid123 4.1K Feb 13 15:43 run_slices.sh.o22535828
    -rw-r--r--. 1 fedid123 fedid123 4.1K Feb 13 15:43 run_slices.sh.o22535826
    -rw-r--r--. 1 fedid123 fedid123 4.1K Feb 13 15:43 run_slices.sh.o22535827
    [user@machine tomo-centre] gedit  run_slices.sh.o22535827</pre>
    </div></div><p><br/></p><p><br/></p><p><br/></p><p><br/></p>
                        </div>

                    </div>             </div>

            </div>     </body>

    </html>
