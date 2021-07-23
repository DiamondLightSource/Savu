.. dropdown:: >>> add NxtomoLoader

    .. code-block:: bash 

        Running the configurator
        Starting Savu Config tool (please wait for prompt)
        
        *** Press Enter for a list of available commands. ***
        
        
        -------------------------------------------------------------------------------------
         1) NxtomoLoader                                                                     
        -------------------------------------------------------------------------------------
        
        
.. dropdown:: >>> mod 1.1 []

    .. code-block:: bash 

        
        -------------------------------------------------------------------------------------
         1) NxtomoLoader                                                                     
        --basic------------------------------------------------------------------------------
            1)                preview : []
        -------------------------------------------------------------------------------------
        
        
.. dropdown:: >>> disp -a

    .. code-block:: bash 

        
        -------------------------------------------------------------------------------------
         1) NxtomoLoader                                                                     
        --basic------------------------------------------------------------------------------
            1)                preview : []
            2)              data_path : entry1/tomo_entry/data/data
            3)                   dark : [None, None, 1.0]
            4)                   flat : [None, None, 1.0]
        --intermediate-----------------------------------------------------------------------
            5)                   name : tomo
            6)         image_key_path : entry1/tomo_entry/instrument/detector/image_key
            7)                 angles : None
            8)               3d_to_4d : False
            9)           ignore_flats : None
        -------------------------------------------------------------------------------------
        
        
.. dropdown:: >>> add ProjectionShift

    .. code-block:: bash 

        
        -------------------------------------------------------------------------------------
         1) NxtomoLoader                                                                     
        -------------------------------------------------------------------------------------
         2) ProjectionShift                                                                  
        -------------------------------------------------------------------------------------
        
        
.. dropdown:: >>> disp 1.3 -vv

    .. code-block:: bash 

        
        -------------------------------------------------------------------------------------
         1) NxtomoLoader (savu.plugins.loaders.full_field_loaders.nxtomo_loader)             
          A class for loading standard tomography data in Nexus format.                      
          A class to load tomography data from a hdf5 file                                   
            3)                   dark : [None, None, 1.0]
              Specify the nexus file location where the dark field images are stored. Then   
              specify the path within this nexus file, at which the dark images are located. 
              The last value will be a scale value.                                          
        -------------------------------------------------------------------------------------
        
        
.. dropdown:: >>> open /home/glb23482/git_projects/Savu/test_data/process_lists/vo_centering_process.nxs

    .. code-block:: bash 

        
        -------------------------------------------------------------------------------------
         1) NxtomoLoader                                                                     
        -------------------------------------------------------------------------------------
         2) DarkFlatFieldCorrection                                                          
        -------------------------------------------------------------------------------------
         3) VoCentering                                                                      
        -------------------------------------------------------------------------------------
         4) ScikitimageFilterBackProjection                                                  
        -------------------------------------------------------------------------------------
        
        
.. dropdown:: >>> exit

    .. code-block:: bash 

        
