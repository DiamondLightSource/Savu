# Copyright 2019 Diamond Light Source Ltd.
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
.. module:: otsu_thresh
   :platform: Unix
   :synopsis: Segmentation by thresholding based on Otsu's method.
              Optionally calculate cropping values based on the segmented image

.. moduleauthor:: Jacob Williamson <scientificsoftware@diamond.ac.uk>
"""


from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin

import itertools
import numpy as np
from skimage.filters import threshold_otsu
from PIL import Image
import h5py as h5
import os

@register_plugin
class OtsuThresh(Plugin, CpuPlugin):

    def __init__(self):
        super(OtsuThresh, self).__init__("OtsuThresh")

    def setup(self):

        in_dataset, out_dataset = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup(self.parameters['pattern'], 'single')

        for i in range(len(out_dataset)):
            out_dataset[0].create_dataset(in_dataset[0], dtype=np.uint8)
            out_pData[0].plugin_data_setup(self.parameters['pattern'], 'single')

        self.cropping = self.parameters["cropping"]
        self.buffer = self.parameters["buffer"]
        self.directions = self.parameters["directions"]

        self.shape = in_dataset[0].data_info.get("shape")
        self.fully_right, self.fully_below = self.shape[2] - 1, self.shape[1] - 1
        self.volume_crop = {"left": 0, "above": 0, "right": self.fully_right, "below": self.fully_below}
        self.orig_edges = {"left": 0, "above": 0, "right": self.fully_right, "below": self.fully_below}
        self.gap_size = 20

    def pre_process(self):

        if "left" in self.directions:
            self.volume_crop["left"] = self.fully_right
        if "above" in self.directions:
            self.volume_crop["above"] = self.fully_below
        if "right" in self.directions:
            self.volume_crop["right"] = 0
        if "below" in self.directions:
            self.volume_crop["below"] = 0

    def process_frames(self, data):
        threshold = threshold_otsu(data[0])
        thresh_result = (data[0] > threshold) * 1
        if self.cropping:
            cropped_slice = self._crop(thresh_result, ["left", "above", "right", "below"])
            #if self.pcount % (self.shape[0]//10) == 0:
            #    self.__save_image(cropped_slice, f"cropped_slices/slice{self.pcount}-cropped")
        if self.exp.meta_data.get("pre_run"):
            return None
        else:
            return thresh_result

    def post_process(self):
        if self.cropping:
            preview = self._cropping_post_process()
            if self.exp.meta_data.get("pre_run"):
                self._write_preview_to_file(preview)

    def nInput_datasets(self):
        return 1

    def nOutput_datasets(self):
        if self.exp.meta_data.get("pre_run"):
            return 0
        else:
            return 1

    def _crop(self, binary_slice, directions, buffer=0):
        # For 3 dimensional volume and 2 dimensional slices

        total_crop = {"left": 0, "above": 0, "right": self.fully_right, "below": self.fully_below}
        total_counter = 0
        reset_counter = 0
        dir_cycle = itertools.cycle(directions)
        while reset_counter < 4:
            direction = next(dir_cycle)
            crops = {"left": 0, "above": 0, "right": binary_slice.shape[1], "below": binary_slice.shape[0]}
            if direction in ["above", "below"]:
                axis = 1
            elif direction in ["left", "right"]:
                axis = 0

            non_zeros_list = np.count_nonzero(binary_slice, axis=axis)
            previous = None
            fills = []
            gaps = []
            for i, non_zeros in enumerate(non_zeros_list):
                if non_zeros + buffer < binary_slice.shape[axis]:  # check if some zeros (indicating sample)
                    if previous != "fill":
                        fills.append([])
                    fills[-1].append(i)
                    previous = "fill"
                else:
                    if previous != "gap":
                        gaps.append([])
                    gaps[-1].append(i)
                    previous = "gap"

            #  find largest area of zeros (assume this is where sample is)
            largest_fill = []
            for fill in fills:
                if len(fill) > len(largest_fill):
                    largest_fill = fill

            #  find a reasonably sized gap closest to the sample
            if direction in ["left", "above"]:
                for gap in gaps:
                    if gap[-1] < largest_fill[0]:
                        if len(gap) > self.gap_size:
                            crops[direction] = gap[-1]
                            reset_counter = 0
                total_crop[direction] += crops[direction]

            elif direction in ["right", "below"]:
                for gap in gaps[::-1]:
                    if gap[0] > largest_fill[-1]:
                        if len(gap) > self.gap_size:
                            crops[direction] = gap[0] + 1
                            reset_counter = 0
                total_crop[direction] -= (binary_slice.shape[1 - axis] - crops[direction])

            #if self.pcount == 0:
            #    self.__save_image(binary_slice, f"{total_counter}-{reset_counter}-{direction}")

            reset_counter += 1
            total_counter += 1

            binary_slice = binary_slice[crops["above"]: crops["below"], crops["left"]: crops["right"]]

        for direction in self.directions:
            if direction in ["left", "above"]:
                if total_crop[direction] < self.volume_crop[direction]:
                    self.volume_crop[direction] = total_crop[direction]
            if direction in ["right", "below"]:
                if total_crop[direction] > self.volume_crop[direction]:
                    self.volume_crop[direction] = total_crop[direction]
        return binary_slice

    def _cropping_post_process(self):
        for direction in self.directions:
            if direction in ["left", "above"]:
                self.volume_crop[direction] = int(self.volume_crop[direction] - self.buffer)
                if self.volume_crop[direction] < self.orig_edges[direction]:
                    self.volume_crop[direction] = self.orig_edges[direction]
            if direction in ["right", "below"]:
                self.volume_crop[direction] = int(self.volume_crop[direction] + self.buffer)
                if self.volume_crop[direction] > self.orig_edges[direction]:
                    self.volume_crop[direction] = self.orig_edges[direction]
        preview = f":, {self.volume_crop['above']}:{self.volume_crop['below']}, {self.volume_crop['left']}:{self.volume_crop['right']}"
        self.exp.meta_data.set("pre_run_preview", preview)

        return preview

    def _write_preview_to_file(self, preview):
        if self.exp.meta_data.get("pre_run"):
            folder = self.exp.meta_data['out_path']
            fname = self.exp.meta_data.get('datafile_name') + '_pre_run.nxs'
            filename = os.path.join(folder, fname)
            comm = self.get_communicator()
            if comm.rank == 0:
                with h5.File(filename, "a") as h5file:
                    fsplit = self.exp.meta_data["data_path"].split("/")
                    fsplit[-1] = ""
                    stats_path = "/".join(fsplit)
                    preview_group = h5file.require_group(stats_path)
                    preview_group.create_dataset("preview", data=preview)

    def __save_image(self, binary_slice, name):
        #  just used for testing
        binary_slice = binary_slice.astype(np.uint8)*150
        im = Image.fromarray(binary_slice)

        im.save(f"/scratch/Savu/images/{name}.jpeg")