import argparse
import h5py
import sys
import os

from savu.version import __version__


class NXcitation(object):
    def __init__(self, description, doi, endnote, bibtex):
        self.description = description.decode('UTF-8')
        self.doi = doi.decode('UTF-8')
        self.endnote = endnote.decode('UTF-8')
        self.bibtex = bibtex.decode('UTF-8')

    def get_bibtex_ref(self):
        return self.bibtex.split(',')[0].split('{')[1] \
            if self.bibtex else ""

    def get_first_author(self):
        parts = self.endnote.split('\n')
        for part in parts:
            if part.startswith("%A"):
                return part.replace("%A", "").strip()

    def get_date(self):
        parts = self.endnote.split('\n')
        for part in parts:
            if part.startswith("%D"):
                return part.replace("%D", "").strip()

    def get_description_with_author(self):
        return "%s \\ref{%s}(%s, %s)" % (self.description,
                                         self.get_bibtex_ref(),
                                         self.get_first_author(),
                                         self.get_date())


class NXcitation_manager(object):
    def __init__(self):
        self.NXcite_list = []

    def add_citation(self, citation):
        self.NXcite_list.append(citation)

    def get_full_endnote(self):
        return "\n\n".join([cite.endnote for cite in self.NXcite_list])

    def get_full_bibtex(self):
        return "\n".join([cite.bibtex for cite in self.NXcite_list])

    def get_description_with_citations(self):
        return ".  ".join([cite.get_description_with_author() for cite in
                           self.NXcite_list])

    def __str__(self):
        return "\nDESCRIPTION\n%s\n\nBIBTEX\n%s\n\nENDNOTE\n%s" % \
            (self.get_description_with_citations(), self.get_full_bibtex(),
             self.get_full_endnote())


class NXciteVisitor(object):

    def __init__(self):
        self.citation_manager = NXcitation_manager()

    def _visit_NXcite(self, name, obj):
        if "NX_class" in list(obj.attrs.keys()):
            if obj.attrs["NX_class"] in ["NXcite"]:
                citation = NXcitation(obj['description'][0],
                                      obj['doi'][0],
                                      obj['endnote'][0],
                                      obj['bibtex'][0])
                self.citation_manager.add_citation(citation)

    def get_citation_manager(self, nx_file, entry):
        nx_file[entry].visititems(self._visit_NXcite)
        return self.citation_manager


def __check_input_params(args):
    """ Check for required input arguments.
    """
    if len(args) != 2:
        print("Input and output filename need to be specified")
        print("Exiting with error code 1 - incorrect number of inputs")
        sys.exit(1)

    if not os.path.exists(args[0]):
        print(("Input file '%s' does not exist" % args[0]))
        print("Exiting with error code 2 - Input file missing")
        sys.exit(2)


def __option_parser(doc=True):
    """ Option parser for command line arguments.
    """
    version = "%(prog)s " + __version__
    parser = argparse.ArgumentParser()
    parser.add_argument('in_file', help='Input data file.')
    parser.add_argument('out_file', help='Output file to extract citation \
                        information to.')
    parser.add_argument('--version', action='version', version=version)
    return parser if doc==True else parser.parse_args()


def main(in_file=None, quiet=False):
    # when calling directly from tomo_recon.py
    if in_file:
        out_file = os.path.join(os.path.dirname(in_file), 'citations.txt')
    else:
        args = __option_parser(doc=False)
        in_file = args.in_file
        out_file = args.out_file
        
    infile = h5py.File(in_file, 'r')
    citation_manager = NXciteVisitor().get_citation_manager(infile, '/')
    if citation_manager is not None:
        with open(out_file, 'w') as outfile:
            outfile.write(citation_manager.__str__())
    
    if not quiet:
        print("Extraction complete")

if __name__ == '__main__':
    main()
