import logging
from savu.plugins.filter import Filter
from savu.data.process_data import CitationInfomration
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.data import structures

from scipy import ndimage
from scipy import optimize
from scipy.optimize import curve_fit

import numpy as np

from savu.plugins.utils import register_plugin


@register_plugin
class SinogramAlignment(Filter, CpuPlugin):
    """
    A plugin to determine the centre of rotation of a sinogram and to align the
    rows of a sinogram, e.g. in the case of motor backlash.  The centre of mass
    of each row is determined and then a sine function fit through these to
    determine the centre of rotation.  The residual between each centre of mass
    and the sine function is then used to align each row.
    """

    def __init__(self):
        logging.debug("initialising Sinogram Alignment")
        logging.debug("Calling super to make sure that all superclasses are " +
                      " initialised")
        super(SinogramAlignment,
              self).__init__("SinogramAlignment")

    def get_filter_frame_type(self):
        """
        get_filter_frame_type tells the pass through plugin which direction to
        slice through the data before passing it on

         :returns:  the savu.structure core_direction describing the frames to
                    filter
        """
        return structures.CD_SINOGRAM

    def get_max_frames(self):
        """
        Should be overridden to define the max number of frames to process at 
        a time

        :returns:  an integer of the number of frames
        """
        return 1

    def _sinfunc(self, data, a, b, c):
        return (a*np.sin(np.deg2rad(data-b)))+c

    def _shift(self, sinogram, com_x, com_y):
        fitpars, covmat = curve_fit(self._sinfunc, com_x, com_y,
                                    p0=(1.0, 0.2, 20))
        variances = covmat.diagonal()
        std_devs = np.sqrt(variances)
        residual = com_y - self._sinfunc(com_x, *fitpars)
        centre_of_rotation_shift = residual
        np.array_split(sinogram, sinogram.shape[0], axis=0)
        n = 0
        shifted_sinogram = []
        for row in sinogram:
            shifted_sinogram_row = \
                ndimage.interpolation.shift(row, [centre_of_rotation_shift[n]],
                                            mode='nearest')
            shifted_sinogram.append(shifted_sinogram_row)
            n += 1
            output = np.vstack(shifted_sinogram)
        return output

    def _com_y(self, sinogram):
        com_y = []
        np.array_split(sinogram, sinogram.shape[0], axis=0)
        for row in sinogram:
            com = ndimage.measurements.center_of_mass(row)
            com_y.append(com)
        ydata = [y[0] for y in com_y]
        return ydata

    def _com_x(self, sinogram):
        rotation = []
        rotation_step = 2   # needs defining from data
        for i in range(sinogram.shape[0]):
            rotation.append(i*rotation_step)
        xdata = rotation
        return xdata

    def filter_frame(self, sinogram):
        """
        Should be overloaded by filter classes extending this one

        :param data: The data to filter
        :type data: ndarray
        :returns:  The filtered image
        """
        # as dealing with one slice we can squeeze
        sino = sinogram.squeeze()
        sino = np.nan_to_num(sino)
        com_x = self._com_x(sino)
        com_y = self._com_y(sino)
        result = self._shift(sino, com_x, com_y)
        result = result.reshape(result.shape[0], 1, result.shape[1])
        return result

    def required_data_type(self):
        """
        The input for this plugin is RawTimeseriesData

        :returns:  Data
        """
        return structures.ProjectionData

    def output_data_type(self):
        """
        The output of this plugin is ProjectionData

        :returns:  Data
        """
        return structures.ProjectionData

    def get_citation_inforamtion(self):
        cite_info = CitationInfomration()
        cite_info.description = \
            ("The Tomographic filtering performed in this processing " +
             "chain is derived from this work.")
        cite_info.bibtex = \
            ("@Article{C4CP04488F, \n" +
             "author ={Price, S. W. T. and Ignatyev, K. and Geraki, K. and \
             Basham, M. and Filik, J. and Vo, N. T. and Witte, P. T. and \
             Beale, A. M. and Mosselmans, J. F. W.}, \n" +
             "title  ={Chemical imaging of single catalyst particles with \
             scanning [small mu ]-XANES-CT and [small mu ]-XRF-CT}, \n" +
             "journal  ={Phys. Chem. Chem. Phys.}, \n" +
             "year  ={2015}, \n" +
             "volume  ={17}, \n" +
             "issue  ={1}, \n" +
             "pages  ={521-529}, \n" +
             "publisher  ={The Royal Society of Chemistry}, \n" +
             "doi  ={10.1039/C4CP04488F}, \n" +
             "url  ={http://dx.doi.org/10.1039/C4CP04488F}, \n" +
             "}")
        cite_info.endnote = \
            ("%0 Journal Article\n" +
             "%T Chemical imaging of single catalyst particles with scanning \
            [small mu ]-XANES-CT and [small mu ]-XRF-CT\n" +
             "%A Price, Stephen W.T.\n" +
             "%A Ignatyev, Konstantin\n" +
             "%A Geraki, Kalotina\n" +
             "%A Basham, Mark\n" +
             "%A Filik, Jacob\n" +
             "%A Vo, Nghia T.\n" +
             "%A Witte, Peter T.\n" +
             "%A Beale, Andrew M.\n" +
             "%A Mosselmans, J. Fred W.\n" +
             "%J Physical Chemistry Chemical Physics\n" +
             "%V 17\n" +
             "%N 1\n" +
             "%P 521-529\n" +
             "%@ 1094-4087\n" +
             "%D 2015\n" +
             "%I Royal Society of Chemistry")
        cite_info.doi = "doi: 10.1039/c4cp04488f"
        return cite_info
