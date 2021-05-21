Image data in the TIFF format
-----------------------------

.. raw:: html

    <!DOCTYPE html>
    <html>
        <head>
            <title>Tomography Reconstruction : Image data in the TIFF format</title>
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
                        <p><br/></p><p>There are no particular restrictions on tomography data in the TIFF format. A typical tomography TIFF image, recorded in DLS, has the following properties:</p><div class="sectionColumnWrapper"><div class="sectionMacroWithBorder"><p>
                        <code class="java plain">Bits/Sample: </code><code class="java value">16</code></p><div class="sectionMacroRow"><div class="line number5 index4 alt2"><code class="java plain">Sample Format: unsigned integer</code></div><div class="line number6 index5 alt1"><code class="java plain">Compression Scheme: None</code></div><div class="line number7 index6 alt2"><code class="java plain">Photometric Interpretation: min-is-black</code></div><div class="line number8 index7 alt1">
                        <code class="java plain">Samples/Pixel: </code><code class="java value">1</code></div><div class="line number10 index9 alt1"><code class="java plain">Planar Configuration: single image plane</code>
                        </div>
                        </div>
                        </div>
                        </div>

                        <p>
                        </br>
                        Sample-projection images may already be flat-and-dark-field corrected or not. In the latter case, separate dark- and flat-field images can be provided for use by the reconstruction process. All images (projection, flat- and dark-field images) need to be congruent (in shape). If no dark- or flat-field images are available, then appropriate synthetic images can be supplied as substitutes.    </p>
                        </div>



                    </div>             </div>

            </div>     </body>
    </html>
