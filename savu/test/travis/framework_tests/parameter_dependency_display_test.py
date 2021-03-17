# -*- coding: utf-8 -*-
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
.. module:: parameter_dependency_display_test
   :platform: Unix
   :synopsis: unittest test for plugin parameter dependencies
.. moduleauthor:: Jessica Verschoyle <jessica.verschoyle@diamond.ac.uk>

"""

import unittest

import savu.plugins.utils as pu
from scripts.config_generator.content import Content


class ParameterDependencyDisplayTest(unittest.TestCase):
    """Test the display 'on' settings for dependent parameters.
    I have included the dependency text in the docstring for clarity
    """

    def initial_setup(self):
        content = Content()
        ppath = "savu.plugins.reconstructions.tomobar.tomobar_recon"
        plugin = pu.load_class(ppath)()
        plugin._populate_default_parameters()
        return plugin, content

    def test_dependent_param_not_present(self):
        # Do not display the regularisation_methodTV
        """
        regularisation_methodTV:
             visibility: advanced
             dtype: str
             description: 0/1 - TV specific isotropic/anisotropic choice.
             default: 0
             dependency:
               regularisation_method: [ROF_TV, FGP_TV, PD_TV, SB_TV, NLTV]
        """
        plugin, content = self.initial_setup()
        key = "regularisation_method"
        value = "LLT_ROF"

        valid_modification = content.modify_main(
            key, value, plugin.tools, plugin.parameters
        )
        self.assertTrue(valid_modification)

        # Check display list
        display_value = plugin.p_dict["regularisation_methodTV"]["display"]
        self.assertTrue(display_value == "off")

    def test_dependent_param_present(self):
        # Do display regularisation_methodTV
        """
        regularisation_methodTV:
             visibility: advanced
             dtype: str
             description: 0/1 - TV specific isotropic/anisotropic choice.
             default: 0
             dependency:
               regularisation_method: [ROF_TV, FGP_TV, PD_TV, SB_TV, NLTV]
        """
        plugin, content = self.initial_setup()
        key = "regularisation_method"
        value = "ROF_TV"

        display_value_before = \
            plugin.p_dict["regularisation_methodTV"]["display"]
        valid_modification = content.modify_main(
            key, value, plugin.tools, plugin.parameters
        )
        self.assertTrue(valid_modification)

        # Check display list
        display_value = plugin.p_dict["regularisation_methodTV"]["display"]
        self.assertTrue(display_value == "on")

    def test_dependent_param_none(self):
        # Do NOT display regularisation_device
        """
        regularisation_device:
             visibility: advanced
             dtype: str
             description: The device for regularisation
             default: gpu
             dependency:
                regularisation_method: not None
        """
        plugin, content = self.initial_setup()
        key = "regularisation_method"
        value = "None"

        valid_modification = content.modify_main(
            key, value, plugin.tools, plugin.parameters
        )
        self.assertTrue(valid_modification)

        # Check display list
        display_value = plugin.p_dict["regularisation_device"]["display"]
        self.assertTrue(display_value == "off")

    def test_dependent_param_not_none(self):
        # DO display regularisation_device
        """
        regularisation_device:
             visibility: advanced
             dtype: str
             description: The device for regularisation
             default: gpu
             dependency:
                regularisation_method: not None
        """
        plugin, content = self.initial_setup()
        key = "regularisation_method"
        value = "FGP_TV"

        valid_modification = content.modify_main(
            key, value, plugin.tools, plugin.parameters
        )
        self.assertTrue(valid_modification)

        # Check display list
        display_value = plugin.p_dict["regularisation_device"]["display"]
        self.assertTrue(display_value == "on")

    def test_default_choices(self):
        # DO change reg iterations to 100
        """
        regularisation_iterations:
                 visibility: basic
                 dtype: int
                 description:
                   summary: Total number of regularisation iterations.
                     The smaller the number of iterations, the smaller the effect
                     of the filtering is. A larger number will affect the speed
                     of the algorithm.
                   range: Recommended value dependent upon method.
                 default:
                     regularisation_method:
                       ROF_TV: 1000
                       FGP_TV: 500
                       PD_TV: 100
                       SB_TV: 100
                       LLT_ROF: 1000
                       NDF: 1000
                       Diff4th: 1000
                       TGV: 80
                       NLTV: 80
                 dependency:
                    regularisation_method: not None
        """
        plugin, content = self.initial_setup()
        key = "regularisation_method"
        value = "PD_TV"

        # TODO try on load in comparison to modify_main as modify_main does not change default..
        valid_modification = content.modify_main(
            key, value, plugin.tools, plugin.parameters
        )
        self.assertTrue(valid_modification)

        # Check display list
        display_value = plugin.p_dict["regularisation_iterations"]["display"]
        self.assertTrue(display_value == "on")

    def test_default_choices2(self):
        # Do not display regularisation_iterations
        """
        regularisation_iterations:
                 visibility: basic
                 dtype: int
                 description:
                   summary: Total number of regularisation iterations.
                     The smaller the number of iterations, the smaller the effect
                     of the filtering is. A larger number will affect the speed
                     of the algorithm.
                   range: Recommended value dependent upon method.
                 default:
                     regularisation_method:
                       ROF_TV: 1000
                       FGP_TV: 500
                       PD_TV: 100
                       SB_TV: 100
                       LLT_ROF: 1000
                       NDF: 1000
                       Diff4th: 1000
                       TGV: 80
                       NLTV: 80
                 dependency:
                    regularisation_method: not None
        """
        plugin, content = self.initial_setup()
        key = "regularisation_method"
        value = "None"

        valid_modification = content.modify_main(
            key, value, plugin.tools, plugin.parameters
        )
        self.assertTrue(valid_modification)

        # Check display list
        display_value = plugin.p_dict["regularisation_iterations"]["display"]
        self.assertTrue(display_value == "off")


if __name__ == "__main__":
    unittest.main()
