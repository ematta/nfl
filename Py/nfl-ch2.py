import pandas as pd
import numpy as np
import nfl_data_py as nfl  # type: ignore
import matplotlib.pyplot as plt
import seaborn as sns  # type: ignore

sns.set_theme(style="whitegrid", palette="colorblind")

seasons = range(2016, 2023)
pbp_py = nfl.import_pbp_data(seasons)

pbp_py_p = pbp_py.query("play_type == 'pass' & air_yards.notnull()").reset_index()

pbp_py_p["pass_length_air_yards"] = np.where(
    pbp_py_p["air_yards"] >= 20, "long", "short"
)

pbp_py_p["passing_yards"] = np.where(
    pbp_py_p['passing_yards'].isnull(), 0, pbp_py_p['passing_yards']
)

print(pbp_py_p['passing_yards'].describe())

short = pbp_py_p[pbp_py_p['pass_length_air_yards'] == 'short']['passing_yards'].describe()
print(short)

long = pbp_py_p[pbp_py_p['pass_length_air_yards'] == 'short']['passing_yards'].describe()
print(long)

epa_short = pbp_py_p[pbp_py_p['pass_length_air_yards'] == 'short']['epa'].describe()
print(epa_short)

epa_long = pbp_py_p[pbp_py_p['pass_length_air_yards'] == 'long']['epa'].describe()
print(epa_long)

sns.displot(data=pbp_py, x='passing_yards')
# plt.show()

pbp_py_p__short = pbp_py_p.query("pass_length_air_yards == 'short'")
pbp_py_hist_short = sns.displot(data=pbp_py_p__short, x='passing_yards', binwidth=1) \
    .set(title='Short Passes')
pbp_py_hist_short.set_axis_labels("Yargs gained (or logs) during a passing play", "Count")
# plt.show()

pass_boxplot = sns.boxplot(data=pbp_py_p, x='pass_length_air_yards', y='passing_yards')
pass_boxplot.set(
    title='Passing Yards by Pass Length',
    xlabel='Pass Length',
    ylabel='Yards Gained (or Lost) on a Passing Play'
)
# plt.show()

pbp_py_p_s = pbp_py_p.groupby(['passer_id', 'passer', 'season']).agg({"passing_yards": ["mean", "count"]})
pbp_py_p_s.columns = list(map("_".join, pbp_py_p_s.columns.values))
pbp_py_p_s.rename(
    columns={
        "passing_yards_mean": "ypa",
        "passing_yards_count": "n"
    },
    inplace=True
)
print(pbp_py_p_s.sort_values(by=["ypa"], ascending=False).head())

pbp_py_p_s_100 = pbp_py_p_s.query("n >= 100").sort_values(by=["ypa"], ascending=False)
print(pbp_py_p_s_100.head())

pbp_py_p_s_pl = pbp_py_p.groupby(['passer_id', 'passer', 'season', 'pass_length_air_yards']).agg({"passing_yards": ["mean", "count"]})
pbp_py_p_s_pl.columns = list(map("_".join, pbp_py_p_s_pl.columns.values))
pbp_py_p_s_pl.rename(columns={"passing_yards_mean": "ypa", "passing_yards_count": "n"}, inplace=True)
pbp_py_p_s_pl.reset_index(inplace=True)
q_value = (
    '(n >= 100 & pass_length_air_yards == "short") | (n >=30 & pass_length_air_yards == "long")'
)
pbp_py_p_s_pl = pbp_py_p_s_pl.query(q_value).reset_index()
cols_save = ["passer_id", "passer", "season", "pass_length_air_yards", "ypa"]
air_yards_py = pbp_py_p_s_pl[cols_save].copy()
air_yards_lag_py = air_yards_py.copy()
air_yards_lag_py["season"] += 1
air_yards_lag_py.rename(columns={"ypa": "ypa_last"}, inplace=True)
pbp_py_p_s_pl = air_yards_py.merge(air_yards_lag_py, how="inner", on=["passer_id", "passer", "season", "pass_length_air_yards"])
res = pbp_py_p_s_pl[['pass_length_air_yards', 'passer', 'season', 'ypa', 'ypa_last']] \
    .query("passer == 'T.Brady' | passer == 'A.Rodgers'") \
    .sort_values(by=["passer", "pass_length_air_yards", "season"]) \
    .to_string()
print(res)

print(len(pbp_py_p_s_pl.passer_id.unique()))

sns.lmplot(data=pbp_py_p_s_pl, x='ypa', y='ypa_last', col='pass_length_air_yards')
plt.show()

cor = pbp_py_p_s_pl.query("ypa.notnull() & ypa_last.notnull()").groupby("pass_length_air_yards")[["ypa", "ypa_last"]].corr()
print(cor)

leader_board_2017 = pbp_py_p_s_pl \
    .query(
        'pass_length_air_yards == "long" & season == 2017'
    )[['passer_id', 'passer', 'ypa']] \
    .sort_values(by=["ypa"], ascending=False)

print(leader_board_2017.head())