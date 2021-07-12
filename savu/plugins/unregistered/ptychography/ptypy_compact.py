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
.. module:: ptypy_compact
   :platform: Unix
   :synopsis: A plugin to perform ptychography using ptypy

.. moduleauthor:: Aaron Parsons <scientificsoftware@diamond.ac.uk>

"""

from savu.plugins.utils import register_plugin
from savu.plugins.unregistered.ptychography.base_ptycho import BasePtycho
import numpy as np
from ptypy.core import Ptycho
from ptypy import utils as u


#@register_plugin
class PtypyCompact(BasePtycho):
    def __init__(self):
        super(PtypyCompact, self).__init__("PtypyCompact")

    def pre_process(self):
        in_dataset, out_datasets = self.get_datasets()
        in_d1 = in_dataset[0]
        sh = in_d1.get_shape()[-1]

        p, r = self.parse_params()
        ###
        #self.get
        self.p = p
        self.r = r

    def process_frames(self, data):
        self.r.data = data[0]
        self.p.scans.savu.data.recipe = self.r
        # reconstruct
        P = Ptycho(self.p,level=5)
        # now post process
        object_stack = P.obj.storages['S00G00'].data.astype(np.float)
        probe_stack = P.probe.storages['S00G00'].data.astype(np.float)
        positions = self.get_positions()
        return [probe_stack, object_stack, positions]#] add fourier error, realspace error

    def parse_params(self):
        p = u.Param()
        p.scan = u.Param()
        p.scan.data = u.Param()
        p.scan.data.center = self.parameters['data_center']
        p.scan.data.orientation = tuple(self.parameters['data_orientation'])
        p.scan.data.auto_center = self.parameters['data_auto_center']
        p.scan.illumination = u.Param()
        p.scan.illumination.photons = self.parameters['illumination_photons']
        p.scan.illumination.diversity = u.Param()
        p.scan.illumination.diversity.noise = self.parameters['illumination_diversity_noise']
        p.scan.illumination.diversity.power = self.parameters['illumination_diversity_power']
        p.scan.illumination.diversity.shift = self.parameters['illumination_diversity_shift']
        p.scan.sample = u.Param()
        p.scan.sample.model = self.parameters['sample_model']
        p.scan.sample.fill = self.parameters['sample_fill']
        p.scan.sample.recon = u.Param()
        p.scan.sample.diversity = u.Param()
        p.scan.sample.diversity.noise = self.parameters['sample_diversity_noise']
        p.scan.sample.diversity.power = self.parameters['sample_diversity_power']
        p.scan.sample.diversity.shift = self.parameters['sample_diversity_shift']
        p.scan.coherence = u.Param()
        p.scan.coherence.num_probe_modes = self.parameters['coherence_num_probe_modes']
        p.scan.coherence.num_object_modes = self.parameters['coherence_num_object_modes']
        p.scan.coherence.spectrum = self.parameters['coherence_spectrum']
        p.scan.coherence.object_dispersion = self.parameters['coherence_object_dispersion']
        p.scan.coherence.probe_dispersion = self.parameters['coherence_probe_dispersion']
        p.scan.geometry = u.Param()
        p.scan.geometry.shape = self.parameters['geometry_shape']
        p.engine = u.Param()
        p.engine.common = u.Param()
        p.engine.common.probe_support = self.parameters['common_probe_support']
        p.engine.common.clip_object = self.parameters['common_clip_object'] #     turn off all of the output things
        p.io = u.Param()
        p.io.home = "./" ## (05) Base directory for all I/O
        p.io.rfile = False ## (06) Reconstruction file name (or format string)
        p.io.autosave = u.Param()
        p.io.autosave.active = False ## (08) Activation switch
        p.io.autosave.interval = -1 ## (09) Auto-save interval
    # p.io.autosave.rfile = "dumps/%(run)s/%(run)s_%(engine)s_%(iterations)04d.ptyr" ## (10) Auto-save file name (or format string)
    ## (11) Server / Client parameters
        p.io.interaction = u.Param()
        p.io.interaction.active = True
        p.io.autoplot = u.Param()
        p.io.autoplot.imfile = "./" ## (17) Plot images file name (or format string)
        p.io.autoplot.interval = 5 ## (18) Number of iterations between plot updates
        p.io.autoplot.threaded = True ## (19) Live plotting switch
        p.io.autoplot.layout = u.Param() ## (20) Options for default plotter or template name
        p.io.autoplot.dump = False ## (21) Switch to dump plots as image files
        p.io.autoplot.make_movie = False
        if self.parameters['DM_num_iter'] is not None:
            p.engine.DM = u.Param()
            p.engine.DM.name = "DM"
            p.engine.DM.alpha = self.parameters['DM_alpha']
            p.engine.DM.probe_update_start = self.parameters['DM_probe_update_start']
            p.engine.DM.update_object_first = self.parameters['DM_update_object_first']
            p.engine.DM.overlap_converge_factor = self.parameters['DM_overlap_converge_factor']
            p.engine.DM.overlap_max_iterations = self.parameters['DM_overlap_max_iterations']
            p.engine.DM.probe_inertia = self.parameters['DM_probe_inertia']
            p.engine.DM.object_inertia = self.parameters['DM_object_inertia']
            p.engine.DM.fourier_relax_factor = self.parameters['DM_fourier_relax_factor']
            p.engine.DM.obj_smooth_std = self.parameters['DM_obj_smooth_std']
            p.engines = u.Param()
            p.engines.engine_00 = u.Param()
            p.engines.engine_00.name = 'DM'
            p.engines.engine_00.numiter = self.parameters['DM_num_iter']
        if self.parameters['ML_num_iter'] is not None:
            p.engine.ML = u.Param()
            p.engine.ML.name = "ML"
            p.engine.ML.type = self.parameters['ML_type']
            p.engine.ML.floating_intensities = self.parameters['ML_floating_intensities']
            p.engine.ML.intensity_renormalization = self.parameters['ML_intensity_renormalization']
            p.engine.ML.reg_del2 = self.parameters['ML_reg_del2']
            p.engine.ML.reg_del2_amplitude = self.parameters['ML_reg_del2_amplitude']
            p.engine.ML.smooth_gradient = self.parameters['ML_smooth_gradient']
            p.engine.ML.scale_precond = self.parameters['ML_scale_precond']
            p.engine.ML.scale_probe_object = self.parameters['ML_scale_probe_object']
            p.engine.ML.probe_update_start = self.parameters['ML_probe_update_start'] #             p.engines = u.Param()
            p.engines.engine_01 = u.Param()
            p.engines.engine_01.name = 'ML'
            p.engines.engine_01.numiter = self.parameters['ML_num_iter']
        p.scans = u.Param()
        p.scans.savu = u.Param()
        p.scans.savu.if_conflict_use_meta = True
        p.scans.savu.data = u.Param()
        p.scans.savu.data.source = 'savu'
        p.scans.savu.data.dfile = None
        p.scans.savu.data.shape = self.parameters['geometry_shape']
        p.scans.savu.data.save = None
        p.ipython_kernel = False
        r = u.Param()
        r.positions = self.get_positions().T ### this stuff can come out of the nexus file
        p.scans.savu.data.psize = 55e-6
        p.scans.savu.data.distance = 1.59
        p.scans.savu.data.orientation = 2
        p.scans.savu.data.energy = 9.1
        p.scan.illumination = u.Param()
        p.scan.illumination.model = None
        p.scan.illumination.photons = 1e8
        p.scan.illumination.aperture = u.Param()
        p.scan.illumination.aperture.form = "circ"
        p.scan.illumination.aperture.size = 400e-6
        p.scan.illumination.propagation = u.Param()
        p.scan.illumination.propagation.focussed = 440.5e-3
        p.scan.illumination.propagation.parallel = 2.3e-3
        r.mask = np.ones((p.scans.savu.data.shape, p.scans.savu.data.shape))
#         probe_size = tuple(u.expect2(p.scan.geometry.shape)) + (p.scan.coherence.num_probe_modes, )

#         self.set_size_probe(probe_size)
        return p, r

    def get_num_probe_modes(self):
        return self.p.scan.coherence.num_probe_modes

    def set_size_object(self, in_d1, positions, pobj):
        positions = self.get_positions()
        p, r = self.parse_params()
        sh = p.scans.savu.data.shape
        r.data = np.ones((positions.shape[-1],sh,sh))
        p.scans.savu.data.recipe = r
        P = Ptycho(p,level=2)
        object_shape = P.obj.storages['S00G00'].data[0].shape
        self.obj_shape = object_shape + (self.get_num_object_modes(),)
        #print "object shape is" + str(self.obj_shape)

    def set_size_probe(self, probe_shape):
        self.p, self.r = self.parse_params()
        sh = self.p.scans.savu.data.shape
        self.probe_size = (1,)+tuple(u.expect2(sh)) + (self.get_num_probe_modes(),)
        #print "probe size is" + str(self.probe_size)
