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
.. module:: framework_citations
   :platform: Unix
   :synopsis: Contains all framework citations.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""


def get_framework_citations():
    """ return a list of NXcite objects """

    cite_info = []

    cite_info.append({'short_name_article': 'Savu'})
    cite_info[0]['description'] = \
        ("The Savu framework design is described in this paper.")
    cite_info[0]['bibtex'] = \
        ("@article{wadeson2016savu,\n" +
         "title={Savu: A Python-based, MPI Framework for Simultaneous\n" +
         "Processing of Multiple, N-dimensional, Large Tomography\n" +
         "Datasets},\n" +
         "author={Wadeson, Nicola and Basham, Mark},\n" +
         "journal={arXiv preprint arXiv:1610.08015},\n" +
         "year={2016}\n" +
         "}")
    cite_info[0]['endnote'] = \
        ("%0 Journal Article\n" +
         "%T Savu: A Python-based, MPI Framework for Simultaneous Processing\n" +
         "of Multiple, N-dimensional, Large Tomography Datasets\n" +
         "%A Wadeson, Nicola\n" +
         "%A Basham, Mark\n" +
         "%J arXiv preprint arXiv:1610.08015\n" +
         "%D 2016")

    cite_info.append({'short_name_article': 'HDF5'})
    cite_info[1]['description'] = \
        ("Savu uses parallel HDF5 as a backend.")
    cite_info[1]['bibtex'] = \
        ("@ONLINE{hdf5, \n" +
         "author = {{The HDF Group}}, \n" +
         "title = '{Hierarchical Data Format, version 5}', \n" +
         "year = {1997-2016}, \n" +
         "note = {/HDF5/}, \n" +
         "}")
    cite_info[1]['endnote'] = \
        ("%0 Journal Article\n" +
         "%T {Hierarchical Data Format, version 5}\n" +
         "%A HDF Group\n" +
         "%D 2014\n")

    cite_info.append({'short_name_article': 'MPI'})
    cite_info[2]['description'] = ("HDF5 uses the Message Passing Interface\n" +
        "standard for interprocess communication")
    cite_info[2]['bibtex'] = \
        ("@article{walker1996mpi, \n" +
         "title={MPI: a standard message passing interface}, \n" +
         "author={Walker, David W and Dongarra, Jack J}, \n" +
         "journal={Supercomputer}, \n" +
         "volume={12}, \n" +
         "pages={56--68}, \n" +
         "year={1996}, \n" +
         "publisher={ASFRA BV} \n" +
         "}")
    cite_info[2]['endnote'] = \
        ("%0 Journal Article\n" +
         "%T MPI: a standard message passing interface\n" +
         "%A Walker, David W\n" +
         "%A Dongarra, Jack J\n" +
         "%J Supercomputer\n" +
         "%V 12\n" +
         "%P 56-68\n" +
         "%@ 0168-7875\n" +
         "%D 1996\n" +
         "%I ASFRA BV\n")

    return cite_info
