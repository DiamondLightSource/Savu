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
.. module:: tomopy_recon
   :platform: Unix
   :synopsis: Wrapper around the tomopy reconstruction algorithms.  See \
       'http://tomopy.readthedocs.io/en/latest/api/tomopy.recon.algorithm.html'

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

from savu.plugins.driver.cpu_plugin import CpuPlugin

# import tomopy before numpy
import tomopy
import numpy as np

from savu.data.plugin_list import CitationInformation
from savu.plugins.utils import register_plugin
from savu.plugins.base_recon import BaseRecon


@register_plugin
class TomopyRecon(BaseRecon, CpuPlugin):
    """
     A wrapper to the tomopy reconstruction library. Extra keywords not \
     required for the chosen algorithm will be ignored.

    :param algorithm: The reconstruction algorithm (art|bart|fbp|gridrec|mlem|\
    osem|ospml_hybrid|ospml_quad|pml_hybrid|pml_quad|sirt). Default: 'gridrec'.
    :param filter_name: Analytic reconstruction filter (none|shepp|cosine|\
     hann|hamming|ramlak|parzen|butterworth). Default: None
    :param reg_par: Regularization parameter for smoothing. Default: 0.0.
    :param num_iter: Number of iterations. Default: 10.
    :param init_vol: Dataset to use as volume initialiser \
     (doesn't currently work with preview). Default: None.
    :param sino_pad: Pad the sinogram to remove edge artefacts in the \
        reconstructed ROI (NB. This will increase the size of the data and \
        the time taken to perform the reconstruction). Default: False.
    """

    def __init__(self):
        super(TomopyRecon, self).__init__("TomopyRecon")

    def pre_process(self):
        self.sl = self.get_plugin_in_datasets()[0].get_slice_dimension()
        vol_shape = self.get_vol_shape()
        options = {'filter_name': self.parameters['filter_name'],
                   'reg_par': self.parameters['reg_par']-1,
                   'num_iter': self.parameters['num_iter'],
                   'num_gridx': vol_shape[0], 'num_gridy': vol_shape[2]}

        self.alg_keys = tomopy.get_allowed_kwargs()
        self.alg = self.parameters['algorithm']
        self.kwargs = {key: options[key] for key in self.alg_keys[self.alg] if
                       key in options.keys()}

    def reconstruct(self, sino, cors, angles, vol_shape, init):
        recon = tomopy.recon(sino, np.deg2rad(angles), center=cors[0],
                             ncore=1, algorithm=self.alg, init_recon=init,
                             **self.kwargs)
        recon = tomopy.circ_mask(recon, axis=0, ratio=0.95)
        return np.transpose(recon, (1, 0, 2))

    def get_max_frames(self):
        return 8

    def get_citation_information(self):
        cite_info = CitationInformation()
        cite_info.description = \
            ("An algorithm from the TomoPy framework is used to perform the \
             reconstruction in this processing pipeline")
        cite_info.bibtex = \
            ("@article{gursoy2014tomopy,\n" +
             "title={TomoPy: a framework for the analysis of synchrotron,\n" +
             "tomographic data},\n" +
             "author={G{\"u}rsoy, Doga and De Carlo, Francesco and Xiao,\n" +
             "Xianghui and Jacobsen, Chris},\n" +
             "journal={Journal of synchrotron radiation},\n" +
             "volume={21},\n" +
             "number={5},\n" +
             "pages={1188--1193},\n" +
             "year={2014},\n" +
             "publisher={International Union of Crystallography}\n" +
             "}")
        cite_info.endnote = \
            ("%0 Journal Article\n" +
             "%T TomoPy: a framework for the analysis of synchrotron\n" +
             "tomographic data\n" +
             "%A Gursoy, Doga\n" +
             "%A De Carlo, Francesco" +
             "%A Xiao, Xianghui" +
             "%A Jacobsen, Chris" +
             "%J Journal of synchrotron radiation" +
             "%V 21" +
             "%N 5" +
             "%P 1188-1193" +
             "%@ 1600-5775" +
             "%D 2014" +
             "%I International Union of Crystallography")
        cite_info.doi = "doi: 10.1107/S1600577514013939"
