# # Copyright 2014 Diamond Light Source Ltd.
# #
# # Licensed under the Apache License, Version 2.0 (the "License");
# # you may not use this file except in compliance with the License.
# # You may obtain a copy of the License at
# #
# #     http://www.apache.org/licenses/LICENSE-2.0
# #
# # Unless required by applicable law or agreed to in writing, software
# # distributed under the License is distributed on an "AS IS" BASIS,
# # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# # See the License for the specific language governing permissions and
# # limitations under the License.
# 
# """
# .. module:: spectrum_crop
#    :platform: Unix
#    :synopsis: A plugin to crop a spectra
# 
# .. moduleauthor:: Aaron D. Parsons <scientificsoftware@diamond.ac.uk>
# """
# import logging
# from savu.plugins.base_filter import BaseFilter
# from savu.plugins.driver.cpu_plugin import CpuPlugin
# from savu.plugins.utils import register_plugin,dawn_compatible
# import numpy as np
# import os
# import savu.test.test_utils as tu
# from PyMca5.PyMcaPhysics.xrf import McaAdvancedFitBatch
# 
# # @dawn_compatible
# @register_plugin
# class Pymca(BaseFilter, CpuPlugin):
#     """
#     crops a spectrum to a range
# 
#     :param config: path to the config file. Default: 'Savu/test_data/data/test_config.cfg'.
# 
#     """
# 
#     def __init__(self):
#         logging.debug("cropping spectrum")
#         super(Pymca, self).__init__("Pymca")
#         
#     def pre_process(self):
#         slice_dir = self.get_plugin_in_datasets()[0].get_slice_dimension()
# #         print "the slice dir in the preprocess is:"+str(slice_dir)
# 
#     def filter_frames(self, data):
# #         print np.array(data).shape
#         y=np.array(data)
#         y = np.expand_dims(data,0)
# #         print "filter IN shape is:"+str(y.shape)
#         b = self.setup_fit(y)
#         b._McaAdvancedFitBatch__processStack()
#         stack = np.array(b._McaAdvancedFitBatch__images.values())
# #         print "stack shape is:",stack.shape
#         op_stack = np.rollaxis(stack,0,3)
# #         print "filter OUT shape is"+str(op_stack.shape)
#         return op_stack[0]# savu expects us to output a rank 2 here
# 
#     def setup(self):
#         logging.debug('setting up the pymca fitting')
#         in_dataset, out_datasets = self.get_datasets()
#         inshape = in_dataset[0].get_shape()
#         spectra_shape = inshape[-1] #  nearly always true.
#         rest_shape = inshape[:-1]
#         c = self.setup_fit(np.random.random((1,1,spectra_shape)))# seed it with junk, zeros made the matrix singular unsurprisingly and this bungles it.
#         c._McaAdvancedFitBatch__processStack()# perform an initial fit to get the shapes
#         fit_labels = c._McaAdvancedFitBatch__images.keys() # and then take out the axis labels for the channels
#         outputshape = rest_shape+(len(fit_labels),) # and this is the shape the thing will be
# #         print "input shape is", in_dataset[0].get_shape()
# #         print "the output shape in setup is"+str(outputshape)
#         
#         axis_labels = ['-1.FitAreas.unit']
#         pattern_list = ['SINOGRAM', 'PROJECTION']
#         fitResult = out_datasets[0]
# 
#         fitResult.create_dataset(patterns={in_dataset[0]: pattern_list},
#                                 axis_labels={in_dataset[0]: axis_labels},
#                                 shape=outputshape)
#         fitResult.meta_data.set_meta_data('FitAreas',fit_labels)
#         slice_directions = tuple(range(len(rest_shape)))
# #         print "slice directions are:"+str(slice_directions)
#         fitResult.add_pattern("CHANNEL", core_dir=(-1,),
#                         slice_dir=slice_directions)
#         
#         in_pData, out_pData = self.get_plugin_datasets()
#         in_pData[0].plugin_data_setup(self.get_plugin_pattern(), self.get_max_frames())
#         out_pData[0].plugin_data_setup('CHANNEL', self.get_max_frames())
#         
#         
#     def get_max_frames(self):
#         """
#         This filter processes 1 frame at a time
# 
#         """
#         return 1
# 
#     def get_plugin_pattern(self):
#         return 'SPECTRUM'
# 
#     def nOutput_datasets(self):
#         return 1
# 
#     def setup_fit(self,y):
#         '''
#         takes a data shape and returns a fit-primed object
#         '''
#         
#         cfg=[self.get_conf_path()] # needs to be a list, apparently
#         inputfile= self.get_dummyhdf_path() # this is needed because we do a hard check on the file type, which we then override... just trust me...Line204 of getFileHandle
#         outputdir=None # nope
#         roifit=0# nope
#         roiwidth=y.shape[1] #need this to pretend its an image
#         b = McaAdvancedFitBatch.McaAdvancedFitBatch(cfg,
#                                                     inputfile,
#                                                     outputdir,
#                                                     roifit,
#                                                     roiwidth,
#                                                     fitfiles=0) # prime the beauty
#         b.pleaseBreak = 1 # we want to run it up to just before loading the data
#         b.processList() # but only up to loading before it breaks
#         # populate this manually so that we can bypass the loading
#         b.file.info['McaCalib'] = [0.0, 1.0, 0.0] #  are these actually used? Or is the calib from the file taken....must check!
#         b.file.info["McaIndex"] = 2 # the signal is in axis=2
#         b.file.info['Channel0'] = 0#not sure what this does. Presumably good for fitting multielement detectors?
#         b.file.info['Size'] = 1# no idea what this does. Should check it
#         b.file.info['Dim_1'] = y.shape[0]# auto populate these sizes with something
#         b.file.info['Dim_2'] = y.shape[1]
#         b.file.info['Dim_3'] = y.shape[2]
#         b.file.info['SourceName'] = 'Benjamin'# just a random name
#         b.file.info['SourceType'] = 'array'# just a random type
#         b.file.info['NumberOfFiles'] = 1# we are only giving it one fake file
#         b.file.info['FileIndex'] = 0# ... and it is index 0
#         b.file.data = y #  now we cram in the data
#         b.file.incrProgressBar = 0 #this does nothing in what we are using
#         b.file._HDF5Stack1D__dtype = np.dtype('float64') # there you are!
#         b._McaAdvancedFitBatch__stack = True # we skip this in the bypass, but we should be true!
#         b.pleaseBreak =0# now deactivate this switch so it doesn't interfere in future
#         return b
#     
#     def get_conf_path(self):
#         path = self.parameters['config']
#         if path.split(os.sep)[0] == 'Savu':
#             path = tu.get_test_data_path(path.split('/test_data/data')[1])
#         return path
#     
#     def get_dummyhdf_path(self):
#         return tu.get_test_data_path('i18_test_data.nxs')
#             