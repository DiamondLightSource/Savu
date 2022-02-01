import matplotlib.pyplot as plt
import pandas as pd
import h5py as h5
import numpy as np

class StatsUtils(object):

    _pattern_dict = {"projection": ["SINOGRAM", "PROJECTION", "TANGENTOGRAM", "4D_SCAN", "SINOMOVIE"],
                     "reconstruction": ["VOLUME_YZ", "VOLUME_XZ", "VOLUME_XY", "VOLUME_3D"]}
    _stats_list = ["max", "min", "mean", "mean_std_dev", "median_std_dev", "RMSD"]

    def generate_figures(self, filepath, savepath):
        f = h5.File(filepath, 'r')
        stats_dict, index_dict = self._get_dicts_for_graphs(f)
        f.close()
        p_stats = pd.DataFrame(stats_dict["projection"], index_dict["projection"]["max"])
        r_stats = pd.DataFrame(stats_dict["reconstruction"], index_dict["reconstruction"]["max"])
        all_stats = pd.concat([p_stats, r_stats], keys=["Projection", "Reconstruction"])
        all_stats.to_html(f"{savepath}/stats_table.html")  # create table of all stats for all plugins

        stats_dict, array_plugins = self._remove_arrays(stats_dict, index_dict)

        p_stats_new = pd.DataFrame(stats_dict["projection"], index_dict["projection"]["max"])
        r_stats_new = pd.DataFrame(stats_dict["reconstruction"], index_dict["reconstruction"]["max"])

        colours = ["red", "blue", "green", "black", "purple", "brown"]
        # creating projection stats figure
        new_p_index = []
        p_legend = ""
        for ind in p_stats_new.index:
            new_p_index.append(ind[0])  # change x ticks to only be plugin numbers rather than names (for space)
            p_legend += f"{ind}\n"
        p_stats_new.index = new_p_index
        fig, ax = plt.subplots(3, 2, figsize=(11, 9), dpi=320, facecolor="azure")
        i = 0
        for row in ax:
            for axis in row:
                stat = self._stats_list[i]
                axis.plot(p_stats_new[stat], "x-", color=colours[i])
                for plugin in array_plugins["projection"]:  # adding 'error' bars for plugins with different values due to parameter changes
                    my_max = max(p_stats[stat][plugin])
                    my_min = min(p_stats[stat][plugin])
                    middle = (my_max + my_min) / 2
                    my_range = my_max - my_min
                    axis.errorbar(int(plugin[0]) - len(p_stats_new) + 1, middle, yerr=[my_range], capsize=5)
                if i == 1:
                    maxx = len(p_stats_new[stat]) * 1.08 - 1
                    maxy = max(p_stats_new[stat])
                    axis.text(maxx, maxy, p_legend, ha="left", va="top",
                              bbox=dict(boxstyle="round", facecolor="red", alpha=0.4))
                stat.replace("_", " ")
                axis.set_title(stat)
                axis.grid(True)
                i += 1
        fig.suptitle("Projection Stats", fontsize="x-large")
        plt.savefig(f"{savepath}/projection_stats.png", bbox_inches="tight")

        # creating reconstruction stats figure
        new_r_index = []
        r_legend = ""
        for ind in r_stats_new.index:
            new_r_index.append(ind[0])  # change x ticks to only be plugin numbers rather than names (for space)
            r_legend += f"{ind}\n"
        r_stats_new.index = new_r_index

        fig, ax = plt.subplots(3, 2, figsize=(11, 9), dpi=320, facecolor="lavender")
        i = 0
        for row in ax:
            for axis in row:
                stat = self._stats_list[i]
                axis.plot(r_stats_new[stat], "x-", color=colours[i])
                for plugin in array_plugins["reconstruction"]:  # adding 'error' bars for plugins with different values due to parameter changes
                    my_max = max(r_stats[stat][plugin])
                    my_min = min(r_stats[stat][plugin])
                    middle = (my_max + my_min) / 2
                    my_range = my_max - my_min
                    axis.errorbar(int(plugin[0]) - len(r_stats_new) + 1, middle, yerr=[my_range], capsize=5)
                if i == 1:
                    maxx = len(r_stats_new[stat]) * 1.08 - 1
                    maxy = max(r_stats_new[stat])
                    axis.text(maxx, maxy, r_legend, ha="left", va="top",
                              bbox=dict(boxstyle="round", facecolor="red", alpha=0.4))
                stat = stat.replace("_", " ")
                axis.set_title(stat)
                axis.grid(True)
                i += 1

        fig.suptitle("Reconstruction Stats", fontsize="x-large")
        plt.savefig(f"{savepath}/reconstruction_stats.png", bbox_inches="tight")

    @staticmethod
    def _get_dicts_for_graphs(file):
        stats_dict = {}
        index_dict = {}
        stats_dict["projection"] = {"max": [], "min": [], "mean": [], "mean_std_dev": [], "median_std_dev": [],
                                    "RMSD": []}
        stats_dict["reconstruction"] = {"max": [], "min": [], "mean": [], "mean_std_dev": [], "median_std_dev": [],
                                        "RMSD": []}
        index_dict["projection"] = {"max": [], "min": [], "mean": [], "mean_std_dev": [], "median_std_dev": [],
                                    "RMSD": []}
        index_dict["reconstruction"] = {"max": [], "min": [], "mean": [], "mean_std_dev": [], "median_std_dev": [],
                                        "RMSD": []}

        group = file["stats"]
        for space in ("projection", "reconstruction"):
            for index, stat in enumerate(["max", "min", "mean", "mean_std_dev", "median_std_dev", "RMSD"]):
                for key in list(group.keys()):
                    if group[key].attrs.get("pattern") in StatsUtils._pattern_dict[space]:
                        index_dict[space][stat].append(f"{key}: {group[key].attrs.get('plugin_name')}")
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
        return stats_dict, index_dict


    @staticmethod
    def _remove_arrays(stats_dict, index_dict):
        array_plugins = {"projection": set(()), "reconstruction": set(())}
        for space in list(stats_dict.keys()):
            for stat in list(stats_dict[space].keys()):
                for index, value in enumerate(stats_dict[space][stat]):
                    if isinstance(value, np.ndarray):
                        stats_dict[space][stat][index] = stats_dict[space][stat][index][0]
                        array_plugins[space].add(index_dict[space][stat][index])
        return stats_dict, array_plugins


