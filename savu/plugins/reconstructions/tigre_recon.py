# Copyright 2018 Diamond Light Source Ltd.
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
.. module:: tigre_recon
   :platform: Unix
   :synopsis: A wrapper around TIGRE software for iterative image reconstruction

.. moduleauthor:: Reuben Lindroos and Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""

from savu.plugins.reconstructions.base_recon import BaseRecon
from savu.data.plugin_list import CitationInformation
from savu.plugins.driver.gpu_plugin import GpuPlugin

import numpy as np
# IMPORT TIGRE HERE
import tigre
import tigre.algorithms as algs

from savu.plugins.utils import register_plugin
from scipy import ndimage


@register_plugin
class TigreRecon(BaseRecon, GpuPlugin):
    """
    A Plugin to reconstruct full-field tomographic projection data using ierative algorithms from \
    the TIGRE package. 

    <tigre.toolbox@gmail.com> <https://github.com/CERN/TIGRE/>

    :param recon_method: The reconstruction method. Methods to choose: 'sart','sirt','ossart','ossart_tv','FDK',
    'asd_pocs','awasd_pocs','fbp','cgls','fista','ista'
    Default: 'cgls'.
    :param iterations: Number of iterations. Default: 20.

    :param blocksize: (int)
        number of angles to be included in each iteration
        of proj and backproj for OS_SART, Default: 20.
    :param lmbda: (np.float64)
        Sets the value of the hyperparameter.

    :param lmbda_red: (np.float64)
        Reduction of lambda every iteration
        lambda=lambdared*lambda. Default: 0.99.

    :param init: (str)
        Describes different initialization techniques.
              "none"     : Initializes the image to zeros (default)
              "FDK"      : intializes image to FDK reconstrucition
              "multigrid": Initializes image by solving the problem in
                           small scale and increasing it when relative
                           convergence is reached.
              "image"    : Initialization using a user specified
                           image. Not recommended unless you really
                           know what you are doing.

    :param verbose:  (Boolean)
        Feedback print statements for algorithm progress
        Default: True.

    :param Quameasopts: (list)
        Asks the algorithm for a set of quality measurement
        parameters. Input should contain a list or tuple of strings of
        quality measurement names. Examples:
            RMSE, CC, UQI, MSSIM

    :param OrderStrategy : (str)
        Chooses the subset ordering strategy. Options are:
                 "ordered"        : uses them in the input order, but
                                    divided
                 "random"         : orders them randomply
                 "angularDistance": chooses the next subset with the
                                    biggest angular distance with the
                                    ones used

    :param tviter: (int)
        For algorithms that make use of a tvdenoising step in their
        iterations. Default (OSSART_TV) : 50

    :param tvlambda: (np.float64)
        For algorithms that make use of a tvdenoising step in their
        iterations. Default (OSSART_TV) : 50

    :param hyper: (np.float64)
        For FISTA algorithm, proportional to the largest eigenvalue of the
        matrix A in the equations Ax-b and ATb. Default: 2.e4
    :param COR: (np.float64)
        Center of rotation correction for projections.

    :param regularisation:
        regularisation methods to use. choose: minimizeTV, AwminimizeTV,
        Default: minimizeTV
    :param dataminimizing:
        dataminimizing method. Choose: art_data_minimizing
        Default: art_data_minimizing (Otherwise hardcoded, for now.)
    """

    def __init__(self):
        super(TigreRecon, self).__init__("TigreRecon")

    def _shift(self, sinogram, centre_of_rotation):
        centre_of_rotation_shift = (sinogram.shape[0] / 2) - centre_of_rotation
        result = ndimage.interpolation.shift(sinogram,
                                             (centre_of_rotation_shift, 0))
        return result

    def pre_process(self):
        # extract given parameters and make them 'self'
        self.recon_method = self.parameters['recon_method']
        self.iterations = self.parameters['iterations']
        # DEFINE GEOMETRY AND VOLUME etc. 
        geo = tigre.geometry()

        for key in self.parameters:
            if self.parameters[key] is not None:
                if key is 'COR':
                    geo.COR = self.parameters.pop('COR')
                else:
                    self.tigre_kwargs.update({key: self.parameters[key]})

    def process_frames(self, data):
        centre_of_rotations, angles, self.vol_shape, init = self.get_frame_params()
        sino = data[0].astype(np.float32)  # get a 2D sinogram
        anglesTot, self.DetectorsDimH = np.shape(sino)  # get dimensions out of it
        self.anglesRAD = np.deg2rad(angles.astype(np.float32))  # convert to radians

        # Reconstruct 2D data (sinogram) with TIGRE
        geo = tigre.geometry(mode='parallel', nVoxel=np.array([1, self.vol_shape[0], self.vol_shape[1]]), default=True)
        geo.nDetector = np.array([1, self.DetectorsDimH])
        geo.sDetector = geo.nDetector
        __sino__ = np.float32(np.expand_dims(sino, axis=1))
        recon = getattr(algs, self.recon_method)(__sino__, geo, self.anglesRAD, self.iterations)

        return np.swapaxes(recon, 0, 1)

    def get_max_frames(self):
        return 'single'

    def get_citation_information(self):
        cite_info1 = CitationInformation()
        cite_info1.name = 'citation1'
        cite_info1.description = \
            ("First-order optimisation algorithm for linear inverse problems.")
        cite_info1.bibtex = \
            ("@article{TIGRE,\n" +
             "  author={Ander Biguri and Manjit Dosanjh and Steven Hancock and Manuchehr Soleimani},\n" +
             "  title={TIGRE: a MATLAB-GPU toolbox for CBCT image reconstruction},\n" +
             "  journal={Biomedical Physics & Engineering Express},\n" +
             "  volume={2},\n" +
             "  number={5},\n" +
             "  pages={055010},\n" +
             "  url={http://stacks.iop.org/2057-1976/2/i=5/a=055010},\n" +
             "  year={2016},\n" +
             "  abstract={In this article the Tomographic Iterative GPU-based Reconstruction (TIGRE) Toolbox, a MATLAB/CUDA toolbox for fast and accurate 3D x-ray image reconstruction, is presented. One of the key features is the implementation of a wide variety of iterative algorithms as well as FDK, including a range of algorithms in the SART family, the Krylov subspace family and a range of methods using total variation regularization. Additionally, the toolbox has GPU-accelerated projection and back projection using the latest techniques and it has a modular design that facilitates the implementation of new algorithms. We present an overview of the structure and techniques used in the creation of the toolbox, together with two usage examples. The TIGRE Toolbox is released under an open source licence, encouraging people to contribute.}\n" +
             "}")
        cite_info1.endnote = \
            ("%0 Journal Article\n" +
             "%T TIGRE: a MATLAB-GPU toolbox for CBCT image reconstruction\n" +
             "%A Ander Biguri and Manjit Dosanjh and Steven Hancock and Manuchehr Soleimani\n" +
             "%J Biomedical Physics & Engineering Express\n" +
             "%V 2\n" +
             "%N 5\n" +
             "%P 055010\n" +
             "%@ --\n" +
             "%D 2016\n" +
             "%I --\n")
        cite_info1.doi = "doi: "
        return cite_info1


cite_info1_bibtex = ()
