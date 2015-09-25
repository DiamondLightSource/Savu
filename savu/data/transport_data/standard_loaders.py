# Copyright 2014 Diamond Light Source Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
.. module:: standard_loaders
   :platform: Unix
   :synopsis: Classes for different experimental setups containing standard
   data loaders.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""
import os.path as os
import h5py
import logging
from savu.test import test_utils as tu
import savu.data.data_structures as ds

class _NXAppFinder(object):
    '''
    Returns a given application entry
    '''
    def __init__(self,application="NXfluo"):
        self.hits = []
        self.appl=application

    def _visit_NXapp(self, name, obj):
        if "NX_class" in obj.attrs.keys():
            if obj.attrs["NX_class"] in ["NXentry", "NXsubentry"]:
                if "definition" in obj.keys():
                    if obj["definition"].value == self.appl:
                        self.hits.append(obj)
    
    def get_NXapp(self, nx_file, entry):
        self.hits = []
        nx_file[entry].visititems(self._visit_NXapp)
        return self.hits

class TomographyLoaders(object):
    """
    This class is called from a tomography loader to use a standard loader. It 
    deals with loading of the data for different formats (e.g. hdf5, tiff,...)
    """

    def load_from_nx_tomo(self, exp):
        """
         Define the input nexus file

        :param exp: The Experiment object
        """
        base_classes = [ds.TomoRaw]
        data_obj = exp.create_data_object("in_data", "tomo", base_classes)
        data_obj.meta_data.set_meta_data("base_classes", base_classes)
                
        data_obj.add_pattern("PROJECTION", core_dir = (1, 2), slice_dir = (0,))
        data_obj.add_pattern("SINOGRAM", core_dir = (0, 2), slice_dir = (1,))
        data_obj.set_direction_parallel_to_rotation_axis(0)
        data_obj.set_direction_perp_to_rotation_axis(1)

        objInfo = data_obj.meta_data
        expInfo = exp.meta_data

        data_obj.backing_file = h5py.File(expInfo.get_meta_data("data_file"),'r')
        
        logging.debug("Creating file '%s' '%s'", 'tomo_entry',
                      data_obj.backing_file.filename)

        data_obj.data = data_obj.backing_file['entry1/tomo_entry/data/data']

        data_obj.set_image_key(data_obj.backing_file\
                           ['entry1/tomo_entry/instrument/detector/image_key'])

        objInfo.set_meta_data("image_key", data_obj.get_image_key())

        rotation_angle = \
            data_obj.backing_file['entry1/tomo_entry/data/rotation_angle']
        objInfo.set_meta_data("rotation_angle",
                   rotation_angle[(objInfo.get_meta_data("image_key"))==0,...])

        try:
            control = data_obj.backing_file['entry1/tomo_entry/control/data']
            objInfo.set_meta_data("control", control[...])
        except:
            logging.warn("No Control information available")

        data_obj.set_shape(data_obj.data.shape)
                
    def load_test_projection_data(self, exp):

        data_obj = exp.create_data_object("in_data", "tomo")
        data_obj.add_pattern("PROJECTION", core_dir = (1, 2), slice_dir = (0,))
        data_obj.add_pattern("SINOGRAM", core_dir = (0, -1), slice_dir = (1,))

        objInfo = data_obj.meta_data
        expInfo = exp.meta_data

        data_obj.backing_file = h5py.File(expInfo.get_meta_data("data_file"),'r')
        logging.debug("Creating file '%s' '%s'", 'tomo_entry',
                                              data_obj.backing_file.filename)

        data_obj.data = data_obj.backing_file['TimeseriesFieldCorrections/data']

        rotation_angle = \
            data_obj.backing_file['TimeseriesFieldCorrections/rotation_angle']
        objInfo.set_meta_data("rotation_angle", rotation_angle[...])

        data_obj.set_shape(data_obj.data.shape)
               


#AARON DIT: I will refactor the following code in the future. At the moment it is massively redundant - This is unacceptable!

class FluorescenceLoaders(object):
    """
    This class is called from a fluorescence loader to use a standard loader. It 
    deals with loading of the data for different formats (e.g. hdf5, tiff,...)
    A.D Parsons 13th August 2015
    """

    def load_from_nx_fluo(self, exp):
        """
         Define the input nexus file
        
        :param path: The full path of the NeXus file to load.
        :type path: str
        """
        import numpy as np
        
        # set up the file handles
        data_obj = exp.create_data_object("in_data", "fluo")
        mData = data_obj.meta_data # the application meta data
        
        data_obj.backing_file = h5py.File(exp.meta_data.get_meta_data("data_file"), 'r')
        
        mData.set_meta_data("backing_file", data_obj.backing_file)
        logging.debug("Creating file '%s' '%s'", 'fluo_entry', data_obj.backing_file.filename)
        # now lets extract the fluo entry so we can figure out our geometries!
        finder = _NXAppFinder()
        fluo_entry = finder.get_NXapp(data_obj.backing_file, 'entry1/')[0]
        beam = exp.meta_data
        #lets get the data out
        data_obj.data = data_obj.backing_file[fluo_entry.name+'/instrument/fluorescence/data']
        
        data_obj.set_shape(data_obj.data.shape) # and set its shape

        average = np.mean(np.mean(np.mean(data_obj.data, axis=0),axis=0),axis=0)
        # and the energy axis
        energy = data_obj.backing_file[fluo_entry.name+'/data/energy']
        mono_energy = data_obj.backing_file[fluo_entry.name+'/instrument/monochromator/energy'].value
        mData.set_meta_data("energy", energy)
        mData.set_meta_data("mono_energy", mono_energy) # global since it is to do with the beam
        mData.set_meta_data("average", average)
        #and get the mono energy
        
        # now lets extract the map, if there is one!
        mData.set_meta_data("is_tomo",False) # to begin with
        mData.set_meta_data("is_map",False) # will change to the order of the map
        cts = 0
        motors = []
        motor_type = []
        if ((len(fluo_entry['data'].attrs["axes"])-1)>0):# the -1 here comes from the fact that the data is the last axis only
            for ii in range(len(fluo_entry['data'].attrs["axes"])-1):
                if (fluo_entry['data/'+fluo_entry['data'].attrs["axes"][ii]].attrs['transformation_type']=="rotation"):# find the rotation axis
                    #what axis is this? Could we store it?
                    motors.append(data_obj.backing_file[fluo_entry.name+'/data/'+fluo_entry['data'].attrs["axes"][ii]])
                    mData.set_meta_data("is_tomo",True)
                    motor_type.append('rotation')
                    logging.debug("Fluo reader: '%s'", "Is a tomo scan")
                elif (fluo_entry['data/'+fluo_entry['data'].attrs["axes"][ii]].attrs['transformation_type']=="translation"):# look for translations too!
                    cts+=1# increase the order of the map
                    #what axes are these? Would be good to have for hte pattern stuff
                    motors.append(data_obj.backing_file[fluo_entry.name+'/data/'+fluo_entry['data'].attrs["axes"][ii]])# attach this to the scan map
                    motor_type.append('translation')
        else:
            logging.debug("Fluo reader: '%s' '%s'", "No maps found!")
            pass # no map
        mData.set_meta_data("motors", motors)
        mData.set_meta_data("motor_type", motor_type)
        if (cts):
            mData.set_meta_data("is_map",cts) # set the map counts to be the number of linear scan dimensions
            # chuck to meta
        else:
            logging.debug("Fluo reader: '%s' '%s'", "No translations found!")
            pass
        
        #Now the beam fluctuations
        control = data_obj.backing_file[fluo_entry.name+'/monitor/data']# the ion chamber "normalisation"
        beam.set_meta_data("control", control) # this is global since it is to do with the beam
        
        
        # now we will set up the core directions that we need for processing
        projection = []
        projection_slice = []
        for item,key in enumerate(motor_type):
            if key == 'translation':
                projection.append(item)
            elif key !='translation':
                projection_slice.append(item)
            if key == 'rotation':
                rotation = item # we will assume one rotation for now to save my headache
        projdir = tuple(projection)
        projsli = tuple(projection_slice)
        data_obj.add_pattern("SPECTRUM", core_dir = (-1,), slice_dir = range(len(data_obj.data.shape)-1))
        if mData.get_meta_data("is_map"):
            data_obj.add_pattern("PROJECTION", core_dir = projdir, slice_dir = projsli)# two translation axes
        if mData.get_meta_data("is_tomo"):
            data_obj.add_pattern("SINOGRAM", core_dir = (rotation,projdir[-1]), slice_dir = projdir[:-1])#rotation and fast axis



class STXMLoaders(object):
    """
    This class is called from a stxm loader to use a standard loader. It 
    deals with loading of the data for different formats (e.g. hdf5,...)
    A.D Parsons 17th August 2015
    """
    
    def load_from_nx_stxm(self, exp):
        """
         Define the input nexus file
        
        :param path: The full path of the NeXus file to load.
        :type path: str
        """
        # set up the file handles
        data_obj = exp.create_data_object("in_data", "stxm")
        data_obj.backing_file = h5py.File(exp.meta_data.get_meta_data("data_file"), 'r')
        exp.meta_data.set_meta_data("backing_file", data_obj.backing_file)
        logging.debug("Creating file '%s' '%s'", 'stxm_entry', data_obj.backing_file.filename)
        # now lets extract the fluo entry so we can figure out our geometries!
        finder = _NXAppFinder(application="NXstxm")
        print data_obj.backing_file
        stxm_entry = finder.get_NXapp(data_obj.backing_file, 'entry1/')[0]
        print stxm_entry
        mData = data_obj.meta_data
        beam = exp.meta_data
        #lets get the data out
        data_obj.data = data_obj.backing_file[stxm_entry.name+'/instrument/detector/data']
        data_obj.set_shape(data_obj.data.shape) # and set its shape
        # and the energy axis
        mono_energy = data_obj.backing_file[stxm_entry.name+'/instrument/monochromator/energy']
        beam.set_meta_data("mono_energy", mono_energy)
        #and get the mono energy
        
        # now lets extract the map, if there is one!
        mData.set_meta_data("is_tomo",False) # to begin with
        mData.set_meta_data("is_map",False) # will change to the order of the map
        cts = 0
        motors = []
        motor_type = []
        if ((len(stxm_entry['data'].attrs["axes"]))>0):# the -1 here comes from the fact that the data is the last axis only
            for ii in range(len(stxm_entry['data'].attrs["axes"])):
                if (stxm_entry['data/'+stxm_entry['data'].attrs["axes"][ii]].attrs['transformation_type']=="rotation"):# find the rotation axis
                    #what axis is this? Could we store it?
                    motors.append(data_obj.backing_file[stxm_entry.name+'/data/'+stxm_entry['data'].attrs["axes"][ii]])
                    mData.set_meta_data("is_tomo",True)
                    motor_type.append('rotation')
                    logging.debug("STXM reader: '%s' ", "Is a tomo scan")
                elif (stxm_entry['data/'+stxm_entry['data'].attrs["axes"][ii]].attrs['transformation_type']=="translation"):# look for translations too!
                    cts+=1# increase the order of the map
                    #what axes are these? Would be good to have for hte pattern stuff
                    motors.append(data_obj.backing_file[stxm_entry.name+'/data/'+stxm_entry['data'].attrs["axes"][ii]])# attach this to the scan map
                    motor_type.append('translation')
        else:
            logging.debug("STXM reader: '%s' '%s'", "No maps found!")
            pass # no map
        mData.set_meta_data("motors", motors)
        mData.set_meta_data("motor_type", motor_type)
        if (cts):
            mData.set_meta_data("is_map",cts) # set the map counts to be the number of linear scan dimensions
            # chuck to meta
        else:
            logging.debug("STXM reader: '%s' '%s'", "No translations found!")
            pass
        
        #Now the beam fluctuations
        control = data_obj.backing_file[stxm_entry.name+'/monitor/data']# the ion chamber "normalisation"
        beam.set_meta_data("control", control)

        
        # now we will set up the core directions that we need for processing
        projection = []
        projection_slice = []
        for item,key in enumerate(motor_type):
            if key == 'translation':
                projection.append(item)
            elif key !='translation':
                projection_slice.append(item)
            if key == 'rotation':
                rotation = item # we will assume one rotation for now to save my headache
        projdir = tuple(projection)
        projsli = tuple(projection_slice)
        if mData.get_meta_data("is_map"):
            logging.debug("map")
            data_obj.add_pattern("PROJECTION", core_dir = projdir, slice_dir = projsli)# two translation axes
            logging.debug("datshape="+str(data_obj.data.shape))
            logging.debug("projection directions"+str(projdir))
            logging.debug("slice directions"+str(projsli))
            #logging.debug("slice directions %s",projsli)
        if mData.get_meta_data("is_tomo"):
            logging.debug("tomo")
            data_obj.add_pattern("SINOGRAM", core_dir = (rotation,projdir[-1]), slice_dir = projdir[:-1])#rotation and fast axis
            print("datshape="+str(data_obj.data.shape))
            print("sinogram directions"+str((rotation,projdir[-1])))
            print("slice directions"+str(projdir[:-1]))
            
class XRDLoaders(object):
    """
    This class is called from an XRD loader to use a standard loader. It 
    deals with loading of the data for different formats (e.g. hdf5,...)
    A.D Parsons 17th August 2015
    
    """    
    
    def __init__(self, params):
        self.parameters = params

    def load_from_nx_xrd(self, exp):
        """
         Define the input nexus file
        
        :param path: The full path of the NeXus file to load.
        :type path: str
        """
        # set up the file handles
        data_obj = exp.create_data_object("in_data", "xrd")
        data_obj.backing_file = h5py.File(exp.meta_data.get_meta_data("data_file"), 'r')
        exp.meta_data.set_meta_data("backing_file", data_obj.backing_file)
        logging.debug("Creating file '%s' '%s'", 'xrd_entry', data_obj.backing_file.filename)
        # now lets extract the fluo entry so we can figure out our geometries!
        finder = _NXAppFinder(application="NXxrd")
        xrd_entry = finder.get_NXapp(data_obj.backing_file, 'entry1/')[0]
        mData = data_obj.meta_data
        beam = exp.meta_data
        #lets get the data out
        data_obj.data = data_obj.backing_file[xrd_entry.name+'/instrument/detector/data']
        data_obj.set_shape(data_obj.data.shape) # and set its shape
        # and the energy axis
        mono_energy = data_obj.backing_file[xrd_entry.name+'/instrument/monochromator/energy']
        beam.set_meta_data("mono_energy", mono_energy)
        #and get the mono energy
        
        # now lets extract the map, if there is one!
        mData.set_meta_data("is_tomo",False) # to begin with
        mData.set_meta_data("is_map",False) # will change to the order of the map
        cts = 0
        motors = []
        motor_type = []
        if ((len(xrd_entry['data'].attrs["axes"])-1)>0):# the -1 here comes from the fact that the data is the last axis only
            for ii in range(len(xrd_entry['data'].attrs["axes"])-1):
                if (xrd_entry['data/'+xrd_entry['data'].attrs["axes"][ii]].attrs['transformation_type']=="rotation"):# find the rotation axis
                    #what axis is this? Could we store it?
                    motors.append(data_obj.backing_file[xrd_entry.name+'/data/'+xrd_entry['data'].attrs["axes"][ii]])
                    beam.set_meta_data("is_tomo",True)
                    motor_type.append('rotation')
                    logging.debug("xrd reader: '%s'", "Is a tomo scan")
                elif (xrd_entry['data/'+xrd_entry['data'].attrs["axes"][ii]].attrs['transformation_type']=="translation"):# look for translations too!
                    cts+=1# increase the order of the map
                    #what axes are these? Would be good to have for hte pattern stuff
                    motors.append(data_obj.backing_file[xrd_entry.name+'/data/'+xrd_entry['data'].attrs["axes"][ii]])# attach this to the scan map
                    motor_type.append('translation')
        else:
            logging.debug("xrd reader: '%s' '%s'", "No maps found!")
            pass # no map
        mData.set_meta_data("motors", motors)
        mData.set_meta_data("motor_type", motor_type)
        if (cts):
            mData.set_meta_data("is_map",cts) # set the map counts to be the number of linear scan dimensions
            # chuck to meta
        else:
            logging.debug("xrd reader: '%s' '%s'", "No translations found!")
            pass
        
        #Now the beam fluctuations
        control = data_obj.backing_file[xrd_entry.name+'/monitor/data']# the ion chamber "normalisation"
        beam.set_meta_data("control", control)
        
        
        # now we will set up the core directions that we need for processing
        projection = []
        projection_slice = []
        for item,key in enumerate(motor_type):
            if key == 'translation':
                projection.append(item)
            elif key !='translation':
                projection_slice.append(item)
            if key == 'rotation':
                rotation = item # we will assume one rotation for now to save my headache
        projdir = tuple(projection)
        projsli = tuple(projection_slice)
        if mData.get_meta_data("is_map"):
            data_obj.add_pattern("PROJECTION", core_dir = projdir, slice_dir = projsli)# two translation axes
        if mData.get_meta_data("is_tomo"):
            data_obj.add_pattern("SINOGRAM", core_dir = (rotation,projdir[-1]), slice_dir = projdir[:-2])#rotation and fast axis
        #data_obj.add_pattern("DIFFRACTION", core_dir = (-2,-1), slice_dir = data_obj.data.shape[:-2])
        slicedir=range(len(data_obj.data.shape)-2)
        print slicedir
        data_obj.add_pattern("DIFFRACTION", core_dir = (-2,-1), slice_dir =slicedir)
        # now to load the calibration file
        if os.exists(self.parameters['calibration_path']):
            logging.info("Using the calibration file in the working directory")
            calibration_path=self.parameters['calibration_path']
        elif os.exists(tu.get_test_data_path(self.parameters['calibration_path'])):
            logging.info("Using the calibration path in the test directory")
            calibration_path=tu.get_test_data_path(self.parameters['calibration_path'])
        else:
            logging.info("No calibration file found!")
        calibrationfile = h5py.File(calibration_path, 'r')
        
        mData.set_meta_data("beam_center_x", calibrationfile['/entry/instrument/detector/beam_center_x'])
        mData.set_meta_data("beam_center_y", calibrationfile['/entry/instrument/detector/beam_center_y'])
        mData.set_meta_data("distance", calibrationfile['/entry/instrument/detector/distance'])
        mData.set_meta_data("incident_wavelength", calibrationfile['/entry/calibration_sample/beam/incident_wavelength'])
        mData.set_meta_data("x_pixel_size", calibrationfile['/entry/instrument/detector/x_pixel_size'])
        mData.set_meta_data("detector_orientation", calibrationfile['/entry/instrument/detector/detector_orientation'])


