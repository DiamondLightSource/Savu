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
.. module:: framework_citations_tools
   :platform: Unix
   :synopsis: Contains all framework citations.

.. moduleauthor:: Jessica Verschoyle <scientificsoftware@diamond.ac.uk>

"""
from savu.plugins.plugin_tools import PluginTools

class FrameworkCitationsTools(PluginTools):
    """Framework citation text"""

    def citation(self):
        """
        The Savu online repository
        bibtex:
            @software{nicola_wadeson_2021_5095360,
            author={Nicola Wadeson and
                      Jessica Verschoyle and
                      Daniil Kazantsev and
                      Mark Basham and
                      Dimitar Tasev and
                      Nghia T. Vo and
                      Tom Schoonjans and
                      Emilio PJ and
                      mjn19172 and
                      Srikanth Nagella and
                      Dan Nixon and
                      mstorm and
                      Matthew Frost and
                      cgowling and
                      Robert C Atwood and
                      Gabryel Mason-Williams and
                      Jacob Filik and
                      Katrin Leinweber and
                      Making GitHub Delicious. and
                      The Gitter Badger and
                      Willem Jan Palenstijn and
                      Zdenek},
            title={DiamondLightSource/Savu: Version 4.0},
            month=jul,
            year=2021,
            publisher={Zenodo},
            version={v4.0},
            doi={10.5281/zenodo.5095360},
            url={https://doi.org/10.5281/zenodo.5095360}
            }
        short_name_article: Savu repository
        doi: 10.5281/zenodo.5095360
        """

    def citation1(self):
        """
        The Savu framework design is described in this paper.
        bibtex:
                @article{wadeson2016savu,
                title={Savu: A Python-based, MPI Framework for Simultaneous
                Processing of Multiple, N-dimensional, Large Tomography
                Datasets},
                author={Wadeson, Nicola and Basham, Mark},
                journal={arXiv preprint arXiv:1610.08015},
                year={2016}
                }
        endnote:
                %0 Journal Article
                %T Savu: A Python-based, MPI Framework for Simultaneous Processing
                of Multiple, N-dimensional, Large Tomography Datasets
                %A Wadeson, Nicola
                %A Basham, Mark
                %J arXiv preprint arXiv:1610.08015
                %D 2016
        short_name_article: Savu

        """

    def citation2(self):
        """
        Savu uses parallel HDF5 as a backend.
        bibtex:
                @ONLINE{hdf5,
                author = {{The HDF Group}},
                title = '{Hierarchical Data Format, version 5}',
                year = {1997-2016},
                note = {/HDF5/},
                }
        endnote:
                %0 Journal Article
                %T {Hierarchical Data Format, version 5}
                %A HDF Group
                %D 2014
        short_name_article: Hdf5
        """

    def citation3(self):
        """
        HDF5 uses the Message Passing Interface standard for interprocess
         communication
        bibtex:
                @article{walker1996mpi,
                title={MPI: a standard message passing interface},
                author={Walker, David W and Dongarra, Jack J},
                journal={Supercomputer},
                volume={12},
                pages={56--68},
                year={1996},
                publisher={ASFRA BV}
                }
        endnote:
                %0 Journal Article
                %T MPI: a standard message passing interface
                %A Walker, David W
                %A Dongarra, Jack J
                %J Supercomputer
                %V 12
                %P 56-68
                %@ 0168-7875
                %D 1996
                %I ASFRA BV
        short_name_article: MPI

        """