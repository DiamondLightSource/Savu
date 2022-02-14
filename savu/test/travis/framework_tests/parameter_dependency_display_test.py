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

    def initial_setup(self,
        ppath="savu.plugins.reconstructions.tomobar.tomobar_recon"):
        content = Content()
        plugin = pu.load_class(ppath)()
        tools = plugin.get_plugin_tools()
        tools._populate_default_parameters()
        pdefs = tools.get_param_definitions()
        return plugin, tools, pdefs, content

    def test_dependent_param_not_present(self):
        # Do not display the regularisation_methodTV
        """
        regularisation_methodTV:
             visibility: advanced
             dtype: int
             description: 0/1 - TV specific isotropic/anisotropic choice.
             default: 0
             dependency:
               regularisation_method: [ROF_TV, FGP_TV, PD_TV, SB_TV, NLTV]
        """
        plugin, tools, pdefs, content = self.initial_setup()
        key = "regularisation_method"
        value = "LLT_ROF"

        valid_modification = content.modify_main(
            key, value, tools, plugin.parameters, False, 1
        )
        self.assertTrue(valid_modification)

        # Check display list
        display_value = pdefs["regularisation_methodTV"]["display"]
        self.assertTrue(display_value == "off")

    def test_dependent_param_present(self):
        # Do display regularisation_methodTV
        """
        regularisation_methodTV:
             visibility: advanced
             dtype: int
             description: 0/1 - TV specific isotropic/anisotropic choice.
             default: 0
             dependency:
               regularisation_method: [ROF_TV, FGP_TV, PD_TV, SB_TV, NLTV]
        """
        plugin, tools, pdefs, content = self.initial_setup()
        key = "regularisation_method"
        value = "ROF_TV"

        display_value_before = \
            pdefs["regularisation_methodTV"]["display"]
        valid_modification = content.modify_main(
            key, value, tools, plugin.parameters, False, 1
        )
        self.assertTrue(valid_modification)

        # Check display list
        display_value = pdefs["regularisation_methodTV"]["display"]
        self.assertTrue(display_value == "on")

    def test_dependent_param_none(self):
        # Do NOT display regularisation_device
        """
        regularisation_parameter:
             visibility: basic
             dtype: float
             description:
               summary: Regularisation parameter could control the level
                 of smoothing or denoising.
               verbose: Higher regularisation values lead to stronger smoothing
                 effect. If the value is too high, you will obtain a very blurry
                 reconstructed image.
               range: Recommended between 0.0001 and 0.1
             example: 'A good value to start with is {default}, {range}'
             default: 0.0001
             dependency:
                regularisation_method
        """
        plugin, tools, pdefs, content = self.initial_setup()
        key = "regularisation_method"
        value = "None"

        valid_modification = content.modify_main(
            key, value, tools, plugin.parameters, False, 1
        )
        self.assertTrue(valid_modification)

        # Check display list
        display_value = pdefs["regularisation_parameter"]["display"]
        self.assertTrue(display_value == "off")

    def test_dependent_param_not_none(self):
        # DO display regularisation_device
        """
        regularisation_parameter:
             visibility: basic
             dtype: float
             description:
               summary: Regularisation parameter could control the level
                 of smoothing or denoising.
               verbose: Higher regularisation values lead to stronger smoothing
                 effect. If the value is too high, you will obtain a very blurry
                 reconstructed image.
               range: Recommended between 0.0001 and 0.1
             example: 'A good value to start with is {default}, {range}'
             default: 0.0001
             dependency:
                regularisation_method
        """
        plugin, tools, pdefs, content = self.initial_setup()
        key = "regularisation_method"
        value = "FGP_TV"

        valid_modification = content.modify_main(
            key, value, tools, plugin.parameters, False, 1
        )
        self.assertTrue(valid_modification)

        # Check display list
        display_value = pdefs["regularisation_parameter"]["display"]
        self.assertTrue(display_value == "on")

    def test_default_choices(self):
        # DO change reg iterations to 100
        """
        max_iterations:
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
                   SB_TV: 100
                   LLT_ROF: 1000
                   NDF: 1000
                   Diff4th: 1000
                   TGV: 80
                   NLTV: 80
             dependency:
                regularisation_method: [ROF_TV,FGP_TV,SB_TV,LLT_ROF,NDF,Diff4th,TGV,NLTV]
        """
        plugin, tools, pdefs, content = \
            self.initial_setup(ppath="savu.test.travis.framework_tests.no_process")
        key = "regularisation_method"
        value = "SB_TV"

        valid_modification = content.modify_main(
            key, value, plugin.tools, plugin.parameters, False, 1
        )
        self.assertTrue(valid_modification)

        # Check display list
        display_value = pdefs["max_iterations"]["display"]
        self.assertTrue(display_value == "on")

    def test_default_choices2(self):
        # Do not display max_iterations
        """
        max_iterations:
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
                   SB_TV: 100
                   LLT_ROF: 1000
                   NDF: 1000
                   Diff4th: 1000
                   TGV: 80
                   NLTV: 80
             dependency:
                regularisation_method: [ROF_TV,FGP_TV,SB_TV,LLT_ROF,NDF,Diff4th,TGV,NLTV]
        """
        plugin, tools, pdefs, content = self.initial_setup(
            ppath="savu.test.travis.framework_tests.no_process"
        )
        key = "regularisation_method"
        value = "None"

        valid_modification = content.modify_main(
            key, value, tools, plugin.parameters, False, 1
        )
        self.assertTrue(valid_modification)

        # Check display list
        display_value = pdefs["max_iterations"]["display"]
        self.assertTrue(display_value == "off")


if __name__ == "__main__":
    unittest.main()
