Tomo recon phase gradient with new plugin
--------------------------------------------------------------

Tunhe Zhou

.. raw:: html

    <!DOCTYPE html>
    <html>
        <head>
            <title>Tomo recon phase gradient with new plugin</title>
            <link rel="stylesheet" href="styles/site.css" type="text/css" />
            <META http-equiv="Content-Type" content="text/html; charset=UTF-8">
        </head>

        <body class="theme-default aui-theme-default">
            <div id="page">
                <div id="main" class="aui-page-panel">


                    <div id="content" class="view">
                        <div class="page-metadata">







                            </div>
                        <div id="main-content" class="wiki-content group">
                        <p>example of savu pipeline:</p><p>note:</p><p>1. imageloader can load tif. need to set the angle to the correct image number</p><p>2. HilbertFilter needs to be before VoCentering otherwise vocentering cannot find correct center in phase gradient (not symmetric)</p><p>3. turn log and fbp_filter off.</p><p><br/></p><p><br/></p><p>-------------------------------------------------------------------------------------</p><p> 1) ImageLoader                                                                      </p><p>    1)                preview : [:, :, :]</p><p>    2)            data_prefix : None</p><p>    3)            flat_prefix : None</p><p>    4)            dark_prefix : None</p><p>    5)               <span style="color: rgb(255,0,0);">  angles : np.linspace(0,180,361)</span></p><p>    6)              frame_dim : 0</p><p>    7)           dataset_name : tomo</p><p>-------------------------------------------------------------------------------------</p><p> 2) HilbertFilter                                                                    </p><p>    1)            in_datasets : []</p><p>    2)           out_datasets : []</p><p>-------------------------------------------------------------------------------------</p><p> 3) VoCentering                                                                      </p><p>    1)                preview : [:, mid-5:mid+5, :]</p><p>    2)            start_pixel : None</p><p>    3)            search_area : [-50, 50]</p><p>    4)            in_datasets : []</p><p>    5)          search_radius : 6</p><p>    6)                  ratio : 0.5</p><p>    7)           out_datasets : [cor_raw, cor_fit]</p><p>    8)   datasets_to_populate : []</p><p>    9)               row_drop : 20</p><p>   10)                   step : 0.5</p><p>-------------------------------------------------------------------------------------</p><p> 4) AstraReconGpu                                                                    </p><p>    1)               init_vol : None</p><p>    2)                preview : []</p><p>    <span style="color: rgb(255,0,0);">3)                    log : False</span></p><p>    4)              algorithm : FBP_CUDA</p><p>    5)           n_iterations : 1</p><p>    6)               res_norm : False</p><p>    7)     centre_of_rotation : 0.0</p><p>  <span style="color: rgb(255,0,0);">  8)             FBP_filter : none</span></p><p>    9)            in_datasets : []</p><p>   10)                  ratio : 0.95</p><p>   11)           out_datasets : []</p><p>   12)             centre_pad : False</p><p>   13)              outer_pad : False</p><p>   14)               log_func : np.nan_to_num(-np.log(sino))</p><p>   15)             force_zero : [None, None]</p><p>-------------------------------------------------------------------------------------</p><p><br/></p><p><br/></p>
                        </div>



                    </div>             </div>

            </div>     </body>
    </html>
