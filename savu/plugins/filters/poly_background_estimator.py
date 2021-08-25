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
.. module:: poly_background_estimator
   :platform: Unix
   :synopsis: A plugin to find peaks in spectra

.. moduleauthor:: Aaron Parsons <scientificsoftware@diamond.ac.uk>

"""

from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin
from savu.plugins.filters.base_filter import BaseFilter
import numpy as np
np.seterr(divide='ignore', invalid='ignore')

def division_zero(x,y):
    try:
        return x/y
    except ZeroDivisionError:
        return 0

@register_plugin
class PolyBackgroundEstimator(BaseFilter, CpuPlugin):

    def __init__(self):
        super(PolyBackgroundEstimator,
              self).__init__("PolyBackgroundEstimator")

    def process_frames(self, data):
        data = data[0]
        x = self.axis
        n = self.parameters['n']
        if self.parameters['weights'] == '1/data':
            weights = division_zero(1.0, data)
        elif self.parameters['weights'] == '1/data^2':
            weights =  division_zero(1.0,data**2)
        pvalue = self.parameters['pvalue']
        MaxIterations = self.parameters['MaxIterations']
        zu, _c, _poly, _weight, _index = \
            self.poly_background_estimator(x, data, n, weights, MaxIterations,
                                           pvalue, fixed=True)

        #print "The shape of zu is:"+str(zu.shape)
        return zu

    def setup(self):
        in_dataset, out_datasets = self.get_datasets()
        out = out_datasets[0]
        out.create_dataset(in_dataset[0])
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('SPECTRUM', self.get_max_frames())
        out_pData[0].plugin_data_setup('SPECTRUM', self.get_max_frames())
        in_meta = self.get_in_meta_data()[0]
        # get the axis
        alabel = \
            list(in_dataset[0].data_info.get('axis_labels')[-1].keys())[0]
        self.axis = in_meta.get(alabel)

    def get_max_frames(self):
        return 'single'

    def __generate_parameters(self, n, weight, xdata, ydata):
        """
        generates polynomials based on
        S. Steenstrup J. Appl. Cryst. (1981). 14, 226--229
        "A Simple Procedure for Fitting a Background to a Certain Class of \
        Measured Spectra". The polynomial parameters are based on weights \
        supplied as part of the fitting fit.
        """
        Npoints = xdata.size
        poly = np.zeros((n, Npoints), dtype=np.float64, order='F')
        gamma = np.zeros(n, dtype=np.float64, order='F')
        alpha = np.zeros(n, dtype=np.float64, order='F')
        beta = np.zeros(n, dtype=np.float64, order='F')
        a = np.zeros(n, dtype=np.float64, order='F')

        alpha[0] = (weight * xdata).sum() / weight.sum()
        beta[0] = 0.0
        poly[0] = 1.0
        poly[1] = xdata - alpha[0]
        for j in range(n):
            if j > 1:
                poly[j] = (xdata - alpha[j - 1]) * \
                    poly[j - 1] - beta[j - 1] * poly[j - 2]

            p = poly[j]
            g = (weight * p * p).sum()
            gamma[j] = g
            a[j] = (weight * ydata * p / g).sum()

            if j > 0:
                alpha[j] = (weight * xdata * p * p).sum() / g
                beta[j] = \
                    (weight * xdata * p * poly[j - 1]).sum() / gamma[j - 1]

        return alpha, gamma, beta, a, poly

    def poly_background_estimator(self, xdata, ydata, n=2, weights=None,
                                  maxIterations=12, pvalue=0.9, fixed=False):
        """
        Background estimator based on orthogonal polynomials

        Input:
        xdata,ydata (numpy arrays of same length)
        pvalue  :   ratio of variance in poly to poly value at which to stop.
        0.9 default

        Output:
                background,polynomial weights, polynomials

        S. Steenstrup J. Appl. Cryst. (1981). 14, 226--229
        "A Simple Procedure for Fitting a Background to a Certain Class of \
        Measured Spectra"

        """
        m = 0
        ud = False
        Npoints = xdata.size
        ydata = np.clip(ydata, 0.0001, ydata.max())
        weight = 1.0 / ydata
    #     zu = np.zeros(Npoints, dtype=np.float64)
        myiter = 0
        vartest = True
        c_old = []
        if(fixed):
            maxIterations = n+1
            n = 2
            myiter = 2
        AIC_OLD = 1.0e34
        while myiter < maxIterations:
            myiter += 1
            _alpha, gamma, _beta, c, poly = \
                self.__generate_parameters(n, weight, xdata, ydata)
            zu = (c[:, np.newaxis] * poly).sum(axis=0)
            y_diff = ydata - zu
            rss = (y_diff*y_diff).sum()
            Eu = (weight * y_diff * y_diff).sum()
            f = Npoints - n - m
            if (Eu < (f + m + np.sqrt(2.0 * f))):
                break
            sigma = np.sqrt(Eu / (f * gamma))
            m = 0.0
            index = ydata > (zu + 2.0 * np.sqrt(np.abs(zu)))
            weight = 1.0 / np.abs(zu)
            tw = ydata[index] - zu[index]
            weight[index] = 1.0 / (tw * tw)
            m = Npoints - index.sum()
            if(fixed):
                n += 1
            else:
                if myiter > 1:
                    clen = min(len(c_old), len(c))
                    vartest = True
                    for i in range(clen):
                        if((c[i]-sigma[i]) < c_old[i] and c_old[i] < (c[i] + sigma[i])):
                            vartest = True
                        else:
                            vartest = False
                            break
                if vartest:
                    if abs(sigma[n-1] / c[n-1]) < pvalue:
                        if ud:
                            break
                        n = n + 1
                    else:
                        if n > 3:
                            n = n - 1
                            ud = True
            c_old = c
        #print "finished", index.sum(), len(zu), Npoints, n, m
        return zu, c, poly, weight, index
