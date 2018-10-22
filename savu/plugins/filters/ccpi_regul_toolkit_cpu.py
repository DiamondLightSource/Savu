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
.. module:: Wrapper for CCPi-Regularisation Toolkit (CPU) for efficient 2D/3D denoising
   :platform: Unix
   :synopsis: CCPi-Regularisation Toolkit delivers a variety of variational 2D/3D denoising methods. The available methods are:  'ROF_TV','FGP_TV','SB_TV','TGV','LLT_ROF','NDF','DIFF4th'
   
.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""

from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin

from ccpi.filters.regularisers import ROF_TV, FGP_TV, SB_TV, TGV, LLT_ROF, NDF, DIFF4th
from savu.data.plugin_list import CitationInformation

@register_plugin
class CcpiRegulToolkitCpu(Plugin, CpuPlugin):
    """
    'ROF_TV': Rudin-Osher-Fatemi Total Variation model;  
    'FGP_TV': Fast Gradient Projection Total Variation model;  
    'SB_TV': Split Bregman Total Variation model;  
    'TGV': Total Generalised Variation model;  
    'LLT_ROF': Lysaker, Lundervold and Tai model combined with Rudin-Osher-Fatemi;  
    'NDF': Nonlinear/Linear Diffusion model (Perona-Malik, Huber or Tukey);  
    'DIFF4th': Fourth-order nonlinear diffusion model
    
    :param method: Choose methods |ROF_TV|FGP_TV|SB_TV|TGV|LLT_ROF|NDF|DIFF4th. Default: 'FGP_TV'.
    :param reg_par: Regularisation (smoothing) parameter. Default: 0.05.
    :param max_iterations: Total number of iterations. Default: 200.
    :param time_step: Time marching step, relevant for ROF_TV, LLT_ROF,\
     NDF, DIFF4th methods. Default: 0.001.
    :param lipshitz_constant: TGV method, Lipshitz constant. Default: 12.
    :param alpha1: TGV method, parameter to control the 1st-order term. Default: 1.0.
    :param alpha0: TGV method, parameter to control the 2nd-order term. Default: 0.8.
    :param reg_parLLT: LLT-ROF method, parameter to control the 2nd-order term. Default: 0.05.
    :param penalty_type: NDF method, Penalty type for the duffison, choose from\
    huber, perona or tukey. Default: 'huber'.
    :param edge_par: NDF and DIFF4th methods, noise magnitude parameter. Default: 0.01.
    """

    def __init__(self):
        super(CcpiRegulToolkitCpu, self).__init__('CcpiRegulToolkitCpu')

    def nInput_datasets(self):
        return 1

    def nOutput_datasets(self):
        return 1
    
    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        out_dataset[0].create_dataset(in_dataset[0])
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('VOLUME_XZ', 'single')
        out_pData[0].plugin_data_setup('VOLUME_XZ', 'single')

    def pre_process(self):
	# accessing Ccpi-RGLTK modules
   	self.device = 'cpu'
        if (self.parameters['method'] == 'ROF_TV'):
            # set parameters for the ROF-TV method
            self.pars = {'algorithm': self.parameters['method'], \
                'regularisation_parameter':self.parameters['reg_par'],\
                'number_of_iterations': self.parameters['max_iterations'],\
                'time_marching_parameter': self.parameters['time_step']}            
        if (self.parameters['method'] == 'FGP_TV'):
            # set parameters for the FGP-TV method
            self.pars = {'algorithm': self.parameters['method'], \
                'regularisation_parameter':self.parameters['reg_par'],\
                'number_of_iterations': self.parameters['max_iterations'],\
                'tolerance_constant':1e-06,\
                'methodTV': 0 ,\
                'nonneg': 0 ,\
                'printingOut': 0}            
        if (self.parameters['method'] == 'SB_TV'):
            # set parameters for the SB-TV method
            self.pars = {'algorithm': self.parameters['method'], \
                'regularisation_parameter':self.parameters['reg_par'],\
                'number_of_iterations': self.parameters['max_iterations'],\
                'tolerance_constant':1e-06,\
                'methodTV': 0 ,\
                'printingOut': 0}
        if (self.parameters['method'] == 'TGV'):
            # set parameters for the TGV method
            self.pars = {'algorithm': self.parameters['method'], \
                'regularisation_parameter' : self.parameters['reg_par'],\
                'alpha1' : self.parameters['alpha1'],\
                'alpha0': self.parameters['alpha0'],\
                'number_of_iterations': self.parameters['max_iterations'],\
                'LipshitzConstant' :self.parameters['lipshitz_constant']}            
        if (self.parameters['method'] == 'LLT_ROF'):
            # set parameters for the LLT-ROF method
            self.pars = {'algorithm': self.parameters['method'], \
                'regularisation_parameter':self.parameters['reg_par'],\
                'regularisation_parameterLLT':self.parameters['reg_parLLT'], \
                'number_of_iterations': self.parameters['max_iterations'],\
                'time_marching_parameter': self.parameters['time_step']}            
        if (self.parameters['method'] == 'NDF'):
            # set parameters for the NDF method
            if (self.parameters['penalty_type'] == 'huber'):
                # Huber function for the diffusivity
                penaltyNDF = 1
            if (self.parameters['penalty_type'] == 'perona'):
                # Perona-Malik function for the diffusivity
                penaltyNDF = 2
            if (self.parameters['penalty_type'] == 'tukey'):
                # Tukey Biweight function for the diffusivity
                penaltyNDF = 3            
            self.pars = {'algorithm': self.parameters['method'], \
                'regularisation_parameter':self.parameters['reg_par'],\
                'edge_parameter':self.parameters['edge_par'],\
                'number_of_iterations': self.parameters['max_iterations'],\
                'time_marching_parameter': self.parameters['time_step'],\
                'penalty_type': penaltyNDF}            
        if (self.parameters['method'] == 'DIFF4th'):
            # set parameters for the DIFF4th method
            self.pars = {'algorithm': self.parameters['method'], \
                'regularisation_parameter':self.parameters['reg_par'],\
                'edge_parameter':self.parameters['edge_par'],\
                'number_of_iterations': self.parameters['max_iterations'],\
                'time_marching_parameter': self.parameters['time_step']}        
        return self.pars
        #print "The full data shape is", self.get_in_datasets()[0].get_shape()
        #print "Example is", self.parameters['example']
    def process_frames(self, data):
        # print "The input data shape is", data[0].shape	
	import numpy as np	
	self.pars['input'] = np.nan_to_num(data[0])
        # Running Ccpi-RGLTK modules on CPU
        if (self.parameters['method'] == 'ROF_TV'):
            im_res = ROF_TV(self.pars['input'], 
               		    self.pars['regularisation_parameter'],
	                    self.pars['number_of_iterations'], 
	                    self.pars['time_marching_parameter'],self.device)
        if (self.parameters['method'] == 'FGP_TV'):
            im_res = FGP_TV(self.pars['input'], 
                            self.pars['regularisation_parameter'],
                            self.pars['number_of_iterations'],
                            self.pars['tolerance_constant'], 
                            self.pars['methodTV'],
                            self.pars['nonneg'],
                            self.pars['printingOut'],self.device )
        if (self.parameters['method'] == 'SB_TV'):
            im_res = SB_TV(self.pars['input'], 
                            self.pars['regularisation_parameter'],
                            self.pars['number_of_iterations'],
                            self.pars['tolerance_constant'], 
                            self.pars['methodTV'],
                            self.pars['printingOut'],self.device)
        if (self.parameters['method'] == 'TGV'):
            im_res = TGV(self.pars['input'], 
           		   self.pars['regularisation_parameter'],
		           self.pars['alpha1'],
	                   self.pars['alpha0'],
		           self.pars['number_of_iterations'],
		           self.pars['LipshitzConstant'],self.device)
        if (self.parameters['method'] == 'LLT_ROF'):
            im_res = LLT_ROF(self.pars['input'],
                           self.pars['regularisation_parameter'],
                           self.pars['regularisation_parameterLLT'],
                           self.pars['number_of_iterations'],
                           self.pars['time_marching_parameter'],self.device)
        if (self.parameters['method'] == 'NDF'):
            im_res = NDF(self.pars['input'], 
         	           self.pars['regularisation_parameter'],
                           self.pars['edge_parameter'], 
                           self.pars['number_of_iterations'],
                           self.pars['time_marching_parameter'], 
                           self.pars['penalty_type'],self.device)
        if (self.parameters['method'] == 'DIFF4th'):
            im_res = DIFF4th(self.pars['input'], 
                           self.pars['regularisation_parameter'],
                           self.pars['edge_parameter'], 
                           self.pars['number_of_iterations'],
                          self.pars['time_marching_parameter'],self.device)
        #print "calling process frames", data[0].shape
        return im_res
    def post_process(self):
        pass

    def get_citation_information(self):
        cite_info1 = CitationInformation()
        cite_info1.name = 'citation1'
        cite_info1.description = \
            ("The CCPi-Regularisation toolkit provides a set of variational regularisers (denoisers)\
             which can be embedded in a plug-and-play fashion into proximal splitting methods \
             for image reconstruction. CCPi-RGL comes with algorithms that can satisfy various \
             prior expectations of the reconstructed object, for example being piecewise-constant \
             or piecewise-smooth nature.")
        cite_info1.bibtex = \
            ("@article{kazantsev2019,\n" +
             "title={CCPi-Regularisation Toolkit for computed tomographic image reconstruction with proximal splitting algorithms \},\n" +
             "author={Daniil and Kazantsev, Edoardo and Pasca, \
             Martin and Turner, Philip and Withers},\n" +
             "journal={Software X},\n" +
             "volume={Under revision},\n" +
             "number={--},\n" +
             "pages={--},\n" +
             "year={2019},\n" +
             "publisher={Elsevier}\n" +
             "}")
        cite_info1.endnote = \
            ("%0 Journal Article\n" +
             "%T CCPi-Regularisation Toolkit for computed tomographic image reconstruction with proximal splitting algorithms\n" +
             "%A Kazantsev, Daniil\n" +
             "%A Pasca, Edoardo\n" +
             "%A Turner, Martin\n" +
             "%A Withers, Philip\n" +
             "%J Software X\n" +
             "%V --\n" +
             "%N --\n" +
             "%P --\n" +
             "%@ --\n" +
             "%D 2019\n" +
             "%I Elsevier\n")
        cite_info1.doi = "doi: "
        return [cite_info1]
    

