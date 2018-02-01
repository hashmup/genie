
# coding: utf-8

# In[ ]:

import pandas as pd
import numpy as np
import math
from os.path import join
from collections import defaultdict
from collections import OrderedDict
from matplotlib import pyplot as plt
from matplotlib import colors
from matplotlib.ticker import MaxNLocator
plt.rcParams['font.family'] = 'IPAPGothic'

def gen_graph(dfs, filename):
    y = defaultdict()
    y["MPI process"] = defaultdict()
    y["OpenMP thread"] = defaultdict()
#     y["SIMD"] = defaultdict()
    y["SIMD and RoA"] = defaultdict()
    for title in dfs:
        df = dfs[title]
        time_bench = df['time_avg'].values
        bench_bench = df['bench'].values
        macro_bench = df['macro'].values
        ppn_bench = [int(x) for x in df['ppn'].values]
        omp_bench = [int(x) for x in df['omp_num_threads'].values]
        y["MPI process"][title] = defaultdict()
        y["OpenMP thread"][title] = defaultdict()
#         y["SIMD"][title] = defaultdict()
        y["SIMD and RoA"][title] = defaultdict()
#         y["SIMD"][title]['Default'] = []
#         y["SIMD"][title]['SIMD'] = []
        y["SIMD and RoA"][title]['Default'] = []
        y["SIMD and RoA"][title]['SIMD'] = []
        y["SIMD and RoA"][title]['Restructure of Array'] = []
        for i in range(len(time_bench)):
            # ppn
            if ppn_bench[i] not in y["MPI process"][title]:
                y["MPI process"][title][ppn_bench[i]] = [time_bench[i]]
            else:
                y["MPI process"][title][ppn_bench[i]].append(time_bench[i])
            # omp
            if omp_bench[i] not in y["OpenMP thread"][title]:
                y["OpenMP thread"][title][omp_bench[i]] = [time_bench[i]]
            else:
                y["OpenMP thread"][title][omp_bench[i]].append(time_bench[i])

            if bench_bench[i]:
#                 y["SIMD"][title]["Default"].append(time_bench[i])
                y["SIMD and RoA"][title]["Default"].append(time_bench[i])
            elif macro_bench[i]:
#                 y["SIMD"][title]["SIMD"].append(time_bench[i])
                y["SIMD and RoA"][title]["Restructure of Array"].append(time_bench[i])
            else:
#                 y["SIMD"][title]["SIMD"].append(time_bench[i])
                y["SIMD and RoA"][title]["SIMD"].append(time_bench[i])

    cmap = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
    marker = ['o', 'x', '^', '*']
    for title in y:
        legend_table = defaultdict()
        row = 0
        col = 0
        fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(20, 20), dpi=900)
        for key in y[title]:
            cnt1 = 0
            cnt2 = 0
            for k, v in sorted(y[title][key].items()):
                _cnt1 = cnt1
                _cnt2 = cnt2
                if k in legend_table:
                    _cnt1 = legend_table[k][1]
                    _cnt2 = legend_table[k][2]
                x = [i for i in range(len(v))]
                if title == "OpenMP thread":
                    a = axes[row, col].plot(x[:], y[title][key][k][:], c=cmap[_cnt1], marker=marker[_cnt2], label=k)[0]
        #         ax.scatter(x[:], y[key][k][:], c=cmap[cnt1], marker=marker[cnt2], label=k)
                else:
                    print(row, col, title, key, k, _cnt1, _cnt2)
                    a = axes[row, col].scatter(x[:], y[title][key][k][:], c=cmap[_cnt1], marker=marker[_cnt2], label=k)
                if a.get_label().isdigit():
                    legend_table[int(a.get_label())] = [a, _cnt1, _cnt2]
                else:
                    legend_table[a.get_label()] = [a, _cnt1, _cnt2]
                if cnt1 == len(cmap) - 1:
                    cnt1 = 0
                    cnt2 += 1
                else:
                    cnt1 += 1
            axes[row, col].set_title(key, fontsize=20)
            box = axes[row, col].get_position()
            axes[row, col].set_position([box.x0, box.y0, box.width * 0.8, box.height])
            axes[row, col].set_xlabel("順序", fontsize=18)
            axes[row, col].set_ylabel("実行時間(ms)", fontsize=18)
            axes[row, col].tick_params(axis='both', which='major', labelsize=15)
            axes[row, col].tick_params(axis='both', which='minor', labelsize=15)
            axes[row, col].xaxis.set_major_locator(MaxNLocator(integer=True))
            axes[row, col].yaxis.set_major_locator(MaxNLocator(integer=True))
            if col == 2:
                row += 1
                col = 0
            else:
                col += 1
        axes[1, 2].axis('off')
        plt.suptitle(title, fontsize=30)
        key = []
        val = []
        for k, v in sorted(legend_table.items()):
            key.append(k)
            val.append(v[0])
        lg = fig.legend(tuple(val), tuple(key), 'center right', title=title, fontsize=25)
        lg.get_title().set_fontsize(28)
        fig.savefig(join("/Users/hashmup/Dropbox/研究室/卒業論文/thesis/images", "{0}-{1}.pdf".format(filename, title.replace(' ', '-'))))
#         plt.show()


df_50 = pd.read_csv("k/data/2018-01-31_15-19/result_candidate.csv")
df_50['time_avg'] = (df_50['time'] + df_50['time0'] + df_50['time1'] + df_50['time2'] + df_50['time3'] + df_50['time4']) / 6.0
df_50 = df_50.sort_values(by=["time_avg"]).reset_index(drop=True)
df_100 = pd.read_csv("k/data/2018-01-31_11-09/result_candidate.csv")
df_100['time_avg'] = (df_100['time'] + df_100['time0'] + df_100['time1'] + df_100['time2'] + df_100['time3'] + df_100['time4']) / 6.0
df_100 = df_100.sort_values(by="time_avg").reset_index(drop=True)
df_250 = pd.read_csv("k/data/2018-01-31_00-04/result_candidate.csv")
df_250['time_avg'] = (df_250['time'] + df_250['time0'] + df_250['time1'] + df_250['time2'] + df_250['time3'] + df_250['time4']) / 6.0
df_250 = df_250.sort_values(by="time_avg").reset_index(drop=True)
df_500 = pd.read_csv("k/data/2018-01-30_07-53/result_candidate.csv")
df_500['time_avg'] = (df_500['time'] + df_500['time0'] + df_500['time1'] + df_500['time2'] + df_500['time3'] + df_500['time4']) / 6.0
df_500 = df_500.sort_values(by="time_avg").reset_index(drop=True)
df_1000 = pd.read_csv("k/data/2018-01-31_07-04/result_candidate.csv")
df_1000['time_avg'] = (df_1000['time'] + df_1000['time0'] + df_1000['time1'] + df_1000['time2'] + df_1000['time3'] + df_1000['time4']) / 6.0
df_1000 = df_1000.sort_values(by="time_avg").reset_index(drop=True)
print(df_1000.loc[0])
gen_graph({"シミュレーション時間 50": df_50, "シミュレーション時間 100": df_100, "シミュレーション時間 250": df_250, "シミュレーション時間 500": df_500, "シミュレーション時間 1000": df_1000}, "k")


# In[ ]:

df_50 = pd.read_csv("k/data/2018-01-31_15-19/result_candidate.csv")
df_50['time_avg'] = (df_50['time'] + df_50['time0'] + df_50['time1'] + df_50['time2'] + df_50['time3'] + df_50['time4']) / 6.0
df_100 = pd.read_csv("k/data/2018-01-31_11-09/result_candidate.csv")
df_100['time_avg'] = (df_100['time'] + df_100['time0'] + df_100['time1'] + df_100['time2'] + df_100['time3'] + df_100['time4']) / 6.0
df_250 = pd.read_csv("k/data/2018-01-31_00-04/result_candidate.csv")
df_250['time_avg'] = (df_250['time'] + df_250['time0'] + df_250['time1'] + df_250['time2'] + df_250['time3'] + df_250['time4']) / 6.0
df_500 = pd.read_csv("k/data/2018-01-30_07-53/result_candidate.csv")
df_500['time_avg'] = (df_500['time'] + df_500['time0'] + df_500['time1'] + df_500['time2'] + df_500['time3'] + df_500['time4']) / 6.0
df_1000 = pd.read_csv("k/data/2018-01-31_07-04/result_candidate.csv")
df_1000['time_avg'] = (df_1000['time'] + df_1000['time0'] + df_1000['time1'] + df_1000['time2'] + df_1000['time3'] + df_1000['time4']) / 6.0
df_50 = df_50.sort_values(by=["time_avg"]).reset_index(drop=True)
df_100 = df_100.sort_values(by="time_avg").reset_index(drop=True)
df_250 = df_250.sort_values(by="time_avg").reset_index(drop=True)
df_500 = df_500.sort_values(by="time_avg").reset_index(drop=True)
df_1000 = df_1000.sort_values(by="time_avg").reset_index(drop=True)
gen_graph({"シミュレーション時間 50": df_50, "シミュレーション時間 100": df_100, "シミュレーション時間 250": df_250, "シミュレーション時間 500": df_500, "シミュレーション時間 1000": df_1000}, "k-top50")
