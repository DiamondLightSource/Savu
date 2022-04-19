import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import pandas as pd
import h5py as h5
import numpy as np

class StatsUtils(object):

    _pattern_dict = {"projection": ["SINOGRAM", "PROJECTION", "TANGENTOGRAM", "4D_SCAN", "SINOMOVIE"],
                     "reconstruction": ["VOLUME_YZ", "VOLUME_XZ", "VOLUME_XY", "VOLUME_3D"]}
    _stats_list = ["max", "min", "mean", "mean_std_dev", "median_std_dev", "NRMSD"]

    plt.set_loglevel('WARNING')

    def generate_figures(self, filepath, savepath):
        f = h5.File(filepath, 'r')
        stats_dict, index_list, times_dict = self._get_dicts_for_graphs(f)
        loop_stats, loop_plugins = self._get_dicts_for_loops(f)
        f.close()

        #self.make_loop_graphs(loop_stats, loop_plugins, savepath)

        table_index_list = index_list
        for i in range(len(loop_plugins)):
            for space in list(table_index_list.keys()):
                for j, plugin in enumerate(table_index_list[space]):
                    for loop_plugin in loop_plugins[i]:
                        if loop_plugin == plugin[3::]:
                            table_index_list[space][j] = f"{table_index_list[space][j]} (loop{i})"

        self.make_stats_table(stats_dict, table_index_list, f"{savepath}/stats_table.html")

        for p_num in list(times_dict.keys()):
            for p_name in index_list["projection"] + index_list["reconstruction"]:
                if p_num == p_name[0]:
                    times_dict[p_name] = times_dict.pop(p_num)

        self.make_times_figure(times_dict, f"{savepath}/times_chart.png")

        if len(stats_dict["projection"]["max"]):
            self.make_stats_graphs(stats_dict["projection"], index_list["projection"], "Projection Stats",
                                   f"{savepath}/projection_stats.png")
        if len(stats_dict["reconstruction"]["max"]):
            self.make_stats_graphs(stats_dict["reconstruction"], index_list["reconstruction"], "Reconstruction Stats",
                                   f"{savepath}/reconstruction_stats.png")




    @staticmethod
    def make_stats_table(stats_dict, index_list, savepath):
        stats_dict_copy = {}
        for space, value in stats_dict.items():
            stats_dict_copy[space] = value.copy()
        for stat in list(stats_dict["projection"].keys()):
            if all(value is None for value in stats_dict["projection"][stat]) and all(value is None for value in stats_dict["reconstruction"][stat]):
                del stats_dict_copy["projection"][stat]
                del stats_dict_copy["reconstruction"][stat]
        p_stats = pd.DataFrame(stats_dict_copy["projection"], index_list["projection"])
        r_stats = pd.DataFrame(stats_dict_copy["reconstruction"], index_list["reconstruction"])
        all_stats = pd.concat([p_stats, r_stats], keys=["Projection", "Reconstruction"])
        all_stats.to_html(savepath)  # create table of stats for all plugins

    def make_loop_graphs(self, loop_stats, loop_plugins, savepath):
        for i in range(len(loop_stats)):
            y = loop_stats[i]["NRMSD"]

            #x = list(range(1, len(loop_stats[i]["RMSD"]) + 1))
            x = [None]*len(y)
            for j in range(len(loop_stats[i]["NRMSD"])):
                x[j] = f"{j}-{j+1}"
            ax = plt.figure(figsize=(11, 9), dpi=320).gca()
            ax.xaxis.set_major_locator(MaxNLocator(integer=True))
            #ax.locator_params(axis='x', nbins=j + 1)
            ax.grid(True)
            plt.plot(x, y)
            maxx = j
            maxy = max(y)
            plt.title("NRMSD over loop 0")
            text = f"Loop 0 iterates {maxx + 2} times over:\n"
            for plugin in loop_plugins[i]:
                text += f"{plugin}\n"
            plt.xlabel("Iteration")
            plt.ylabel("NRMSD")

            plt.text(maxx, maxy, text, ha="right", va="top", bbox=dict(boxstyle="round", facecolor="red", alpha=0.4))
            plt.savefig(f"{savepath}/loop_stats{i}.png", bbox_inches="tight")


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
                for plugin in array_plugins:  # adding 'error' bars for plugins with multiple values
                    if stats_df[stat][plugin] is not None:
                        if not np.isnan(stats_df[stat][plugin]).any():
                            my_max = max(stats_df[stat][plugin])
                            my_min = min(stats_df[stat][plugin])
                            middle = (my_max + my_min) / 2
                            my_range = my_max - my_min
                            axis.errorbar(list(stats_df_new.index).index(plugin[0]), middle, yerr=[my_range / 2], capsize=5)
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


    def make_times_figure(self, times_dict, savepath):
        colors = plt.get_cmap('Blues')(np.linspace(0.2, 0.7, len(list(times_dict.keys()))))
        fig, ax = plt.subplots()
        total = sum(list(times_dict.values()))
        ax.pie(list(times_dict.values()), labels=list(times_dict.keys()), autopct=lambda pct: self._get_times_pct(pct, total),
               counterclock=False, startangle=90, colors=colors, radius=3, center=(4, 4), wedgeprops={"linewidth": 1, "edgecolor": "white"})
        fig.suptitle("Plugin Times", x=0.1, y=1.4, horizontalalignment="right", fontsize="x-large")
        plt.savefig(savepath, bbox_inches="tight")

    @staticmethod
    def _get_times_pct(pct, total):
        absolute = (pct/100)*total
        return f"{round(pct, 1)}%\n{round(absolute, 1)} (s)"

    @staticmethod
    def _get_dicts_for_graphs(file):
        stats_dict = {}
        stats_dict["projection"] = {"max": [], "min": [], "mean": [], "mean_std_dev": [], "median_std_dev": [],
                                    "NRMSD": [], "zeros": [], "zeros%": [], "time (s)": []}
        stats_dict["reconstruction"] = {"max": [], "min": [], "mean": [], "mean_std_dev": [], "median_std_dev": [],
                                        "NRMSD": [], "zeros": [], "zeros%": [], "time (s)": []}

        index_list = {"projection": [], "reconstruction": []}

        times_dict = {}

        group = file["stats"]
        for space in ("projection", "reconstruction"):
            for index, stat in enumerate(["max", "min", "mean", "mean_std_dev", "median_std_dev", "NRMSD", "zeros", "zeros%"]):
                for p_num in list(group.keys()):
                    if group[p_num].attrs.get("pattern") in StatsUtils._pattern_dict[space]:
                        if f"{p_num}: {group[p_num].attrs.get('plugin_name')}" not in index_list[space]:
                            index_list[space].append(f"{p_num}: {group[p_num].attrs.get('plugin_name')}")
                        if group[p_num].ndim == 1:
                            stats_list = list(group[p_num].attrs.get("stats_list"))
                            if stat in stats_list:
                                stats_dict[space][stat].append(group[p_num][stats_list.index(stat)])
                            else:
                                stats_dict[space][stat].append(None)
                        elif group[p_num].ndim == 2:
                            stats_list = list(group[p_num].attrs.get("stats_list"))
                            if stat in stats_list:
                                stats_dict[space][stat].append(group[p_num][:, stats_list.index(stat)])
                            else:
                                stats_dict[space][stat].append(None)
            for p_num in list(group.keys()):
                if group[p_num].attrs.get("pattern") in StatsUtils._pattern_dict[space]:
                    stats_dict[space]["time (s)"].append(group[p_num].attrs.get("time"))

        for plugin in list(group.keys()):
            if group[plugin].attrs.get("time") is not None:
                times_dict[plugin] = group[plugin].attrs.get("time")

        return stats_dict, index_list, times_dict

    @staticmethod
    def _get_dicts_for_loops(file):
        if "iterative" in list(file.keys()):
            group = file["iterative"]
            loop_stats = []
            loop_plugins = []
            for key in list(group.keys()):
                loop_stats.append({"NRMSD": list(group[key])})
                loop_plugins.append(group[key].attrs.get("loop_plugins"))
            return loop_stats, loop_plugins
        else:
            return [], []

    @staticmethod
    def _remove_arrays(stats_dict, index_list):
        array_plugins = set(())
        for stat in list(stats_dict.keys()):
            for index, value in enumerate(stats_dict[stat]):
                if isinstance(value, np.ndarray):
                    stats_dict[stat][index] = stats_dict[stat][index][0]
                    array_plugins.add(index_list[index])
        return stats_dict, array_plugins


