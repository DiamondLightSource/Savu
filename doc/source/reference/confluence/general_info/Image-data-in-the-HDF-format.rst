Image data in the HDF5 format
-----------------------------

.. raw:: html

    <!DOCTYPE html>
    <html>
        <head>
            <title>Tomography Reconstruction : Image data in the HDF format</title>
            <link rel="stylesheet" href="styles/site.css" type="text/css" />
            <META http-equiv="Content-Type" content="text/html; charset=UTF-8">
        </head>

        <body class="theme-default aui-theme-default">
            <div id="page">
                <div id="main" class="aui-page-panel">


                    <div id="content" class="view">
                        <div class="page-metadata">

                Created by <span class='author'> Kaz Wanelik</span>
                            </div>
                        <div id="main-content" class="wiki-content group">
                        <p></p><p>For more information about the HDF file format, please go to <a class="external-link" href="http://www.hdfgroup.org/" rel="nofollow">http://www.hdfgroup.org/</a>.</p><p>For more information about the NeXus file format, please go to <a class="external-link" href="http://www.nexusformat.org/" rel="nofollow">http://www.nexusformat.org/</a>.</p><p></p><p>The Tomography Nexus format (which is stored in HDF5) is described as follows from the Pandata Europe Deliverable 5.3</p><p></p><p>5.3 Tomography Raw Data</p><p>This is again a scan around the sample rotation axis. However, in tomography it is common to collect dark field and bright field images before, during and after the actual sample scan in order to be able to correct the data for detector effects. For data reduction the order in which those images have been collected is important.</p><ul><li>entry:NXentry<ul><li>title</li><li>start_time</li><li>end_time</li><li>definition</li><li>instrument:NXinstrument<ul><li>NXsource<ul><li>type</li><li>name</li><li>probe</li></ul></li><li>detector:NXdetector<ul><li>data[nFrames,xsize,ysize]<ul><li>@signal=1</li></ul></li><li>image_key[nFrames]</li><li>x_pixel_size</li><li>y_pixel_size</li><li>distance</li></ul></li></ul></li><li>sample:NXsample<ul><li>name</li><li>rotation_angle[nFrames]<ul><li>@axis=1</li></ul></li><li>x_translation[nFrames]</li><li>y_translation[nFrames]</li><li>z_translation[nFrames]</li></ul></li><li>control:NXmonitor<ul><li>data[nFrames]</li></ul></li><li>data:NXdata<ul><li>data --&gt; /NXentry/NXinstrument/data:NXdetector/data</li><li>rotation_angle --&gt; /NXentry/NXsample/rotation_angle</li></ul></li></ul></li></ul><p>Where image_key is an array which holds for each image either 0,1 or 2 depending if it is a sample, bright field or dark field image.</p><p><br/></p><hr/><p><br/></p><h2 id="ImagedataintheHDFformat-TomoEntry"><strong>Tomo Entry</strong></h2><p>See <a class="external-link" href="http://www.nexusformat.org/" rel="nofollow">http://www.nexusformat.org/</a><a class="external-link" href="http://download.nexusformat.org/sphinx/classes/applications/NXtomo.html" rel="nofollow">http://download.nexusformat.org/sphinx/classes/applications/NXtomo.html</a>.</p><p>An example NeXus scan file, viewed in <em>hdfview</em>, is presented below:</p><p><br/></p><p><span class="confluence-embedded-file-wrapper confluence-embedded-manual-size">

.. image:: ../../../files_and_images/confluence/17827236/32113718.png


.. raw:: html

    </span></p><p></p><p></p><p></p><p><span class="confluence-embedded-file-wrapper confluence-embedded-manual-size">


.. image:: ../../../files_and_images/confluence/17827236/32113719.png


.. raw:: html

    </span></p><p>
    </p><p>Please note that the following items are currently <strong>essential</strong> for running tomography reconstruction with the help of <em>Tomo Recon GUI</em> in Dawn:</p><ol><li>tomo_entry/data/data</li><li>tomo_entry/data/rotation_angle</li><li>tomo_entry/instrument/detector/image_key</li></ol><p>The above Nexus paths are also used as default locations in the <em>tomo-centre</em> &amp; <em>tomo-recon</em> commands and in <em>Savu</em> Reconstruction Pipeline. For more information about tomography reconstruction in DLS, see <a href="Reconstruction-from-image-data-in-the-HDF-format_76392055.html">Reconstruction from image data in the HDF format</a>. </p>
    </div>

                        <div class="pageSection group">

    </div>


                    </div>             </div>

            </div>     </body>
    </html>




