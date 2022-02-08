import matplotlib.pyplot as plt
import pandas as pd
import h5py as h5
import numpy as np

class StatsUtils(object):

    _pattern_dict = {"projection": ["SINOGRAM", "PROJECTION", "TANGENTOGRAM", "4D_SCAN", "SINOMOVIE"],
                     "reconstruction": ["VOLUME_YZ", "VOLUME_XZ", "VOLUME_XY", "VOLUME_3D"]}
    _stats_list = ["max", "min", "mean", "mean_std_dev", "median_std_dev", "NRMSD"]

    def generate_figures(self, filepath, savepath):
        f = h5.File(filepath, 'r')
        stats_dict, index_list = self._get_dicts_for_graphs(f)
        f.close()

        self.make_stats_table(stats_dict, index_list, f"{savepath}/stats_table.html")

        if len(stats_dict["projection"]["max"]):
            self.make_stats_graphs(stats_dict["projection"], index_list["projection"], "Projection Stats",
                                   f"{savepath}/projection_stats.png")
        if len(stats_dict["reconstruction"]["max"]):
            self.make_stats_graphs(stats_dict["reconstruction"], index_list["reconstruction"], "Reconstruction Stats",
                                   f"{savepath}/reconstruction_stats.png")

    @staticmethod
    def make_stats_table(stats_dict, index_list, savepath):
        p_stats = pd.DataFrame(stats_dict["projection"], index_list["projection"])
        r_stats = pd.DataFrame(stats_dict["reconstruction"], index_list["reconstruction"])
        all_stats = pd.concat([p_stats, r_stats], keys=["Projection", "Reconstruction"])
        all_stats.to_html(savepath)  # create table of stats for all plugins

    def make_stats_graphs(self, stats_dict, index_list, title, savepath):
        stats_df = pd.DataFrame(stats_dict, index_list)
        stats_dict, array_plugins = self._remove_arrays(stats_dict, index_list)

        stats_df_new = pd.DataFrame(stats_dict, index_list)

        colours = ["red", "blue", "green", "black", "purple", "brown"]  #max, min, mean, mean std dev, median std dev, NRMSD

        new_index = []
        legend = ""
        for ind in stats_df_new.index:
            new_index.append(ind[0])  # change x ticks to only be plugin numbers rather than names (for space)
            legend += f"{ind}\n"  # This will form a key showing the plugin names corresponding to plugin numbers
        stats_df_new.index = new_index
        fig, ax = plt.subplots(3, 2, figsize=(11, 9), dpi=320, facecolor="lavender")
        i = 0
        for row in ax:
            for axis in row:
                stat = self._stats_list[i]
                axis.plot(stats_df_new[stat], "x-", color=colours[i])
                for plugin in array_plugins:  # adding 'error' bars for plugins with multiple values due to parameter changes
                    my_max = max(stats_df[stat][plugin])
                    my_min = min(stats_df[stat][plugin])
                    middle = (my_max + my_min) / 2
                    my_range = my_max - my_min
                    axis.errorbar(int(plugin[0]) - int(stats_df_new.index[0]), middle, yerr=[my_range / 2], capsize=5)
                if i == 1:
                    maxx = len(stats_df_new[stat]) * 1.08 - 1
                    maxy = max(stats_df_new[stat])
                    axis.text(maxx, maxy, legend, ha="left", va="top",
                              bbox=dict(boxstyle="round", facecolor="red", alpha=0.4))
                stat = stat.replace("_", " ")
                axis.set_title(stat)
                axis.grid(True)
                i += 1
        fig.suptitle(title, fontsize="x-large")
        plt.savefig(savepath, bbox_inches="tight")

    @staticmethod
    def _get_dicts_for_graphs(file):
        stats_dict = {}
        stats_dict["projection"] = {"max": [], "min": [], "mean": [], "mean_std_dev": [], "median_std_dev": [],
                                    "NRMSD": []}
        stats_dict["reconstruction"] = {"max": [], "min": [], "mean": [], "mean_std_dev": [], "median_std_dev": [],
                                        "NRMSD": []}

        index_list = {"projection": [], "reconstruction": []}

        group = file["stats"]
        for space in ("projection", "reconstruction"):
            for index, stat in enumerate(["max", "min", "mean", "mean_std_dev", "median_std_dev", "NRMSD"]):
                for key in list(group.keys()):
                    if group[key].attrs.get("pattern") in StatsUtils._pattern_dict[space]:
                        if f"{key}: {group[key].attrs.get('plugin_name')}" not in index_list[space]:
                            index_list[space].append(f"{key}: {group[key].attrs.get('plugin_name')}")
                        if group[key].ndim == 1:
                            if len(group[key]) > index:
                                stats_dict[space][stat].append(group[key][index])
                            else:
                                stats_dict[space][stat].append(None)
                        elif group[key].ndim == 2:
                            if len(group[key][0]) > index:
                                stats_dict[space][stat].append(group[key][:, index])
                            else:
                                stats_dict[space][stat].append(None)
        return stats_dict, index_list


    @staticmethod
    def _remove_arrays(stats_dict, index_list):
        array_plugins = set(())
        for stat in list(stats_dict.keys()):
            for index, value in enumerate(stats_dict[stat]):
                if isinstance(value, np.ndarray):
                    stats_dict[stat][index] = stats_dict[stat][index][0]
                    array_plugins.add(index_list[index])
        return stats_dict, array_plugins


