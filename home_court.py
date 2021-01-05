import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

np.random.seed(42)


def rand_jitter(arr):
    stdev = .01 * (max(arr) - min(arr))
    return arr + np.random.randn(len(arr)) * stdev


df = pd.read_csv('./data/combined_scores.csv')
df2 = pd.read_csv('./data/2021_combined_scores.csv')
df2 = df2.drop(columns=['is_series_game2'])
df = df.append(df2)
df['score_diff'] = df['team1_pts'] - df['team2_pts']
team_colors_df = pd.read_csv('./data/nba_team_colors.csv')
team_df = df.groupby(['team1_name', 'home'])[['won']].mean()
bubble_df = df[df['location'] == 'Bubble']
bubble_grouped = bubble_df.groupby(['home'])[['won', 'score_diff']].mean()
bubble_grouped['count'] = bubble_df.groupby(['home'])['won'].count()
print(bubble_grouped)
df = df[df['location'] != 'Bubble']
df = df[df['playoffs'] == 'N']
# df.loc[df['rest'] >= 3, 'rest'] = 3
# df['timezone_change'] = np.abs(df['timezone_change'])

# df = df[df['season'] == 2020]
home_df = df.groupby(['home'])[['won', 'score_diff']].mean()
home_df['count'] = df.groupby(['home'])['won'].count()
print(home_df)

team_df = df.groupby(['team1_name', 'home'])[['won', 'score_diff']].mean()
team_df['count'] = df.groupby(['team1_name', 'home'])['won'].count()
team_df = team_df.reset_index()
home_court_df = team_df[team_df['home'] == 'Y']
home_court_df = home_court_df.set_index('team1_name')
away_court_df = team_df[team_df['home'] == 'N']
away_court_df = away_court_df.set_index('team1_name')
team_df = df.groupby(['team1_name'])[['score_diff']].mean()
home_court_df['overall_wp'] = team_df['score_diff']
home_court_df['away_diff'] = away_court_df['score_diff']
home_court_df['diff'] = home_court_df['score_diff'] - home_court_df['away_diff']
away_court_df['overall_wp'] = team_df['score_diff']
away_court_df['diff'] = away_court_df['score_diff'] - away_court_df['overall_wp']
hca_df = pd.merge(home_court_df, team_colors_df,
                  left_on='team1_name', right_on='Full')
hca_df = hca_df.sort_values(by='diff', ascending=False)
fig, ax = plt.subplots(figsize=(10, 6), dpi=400)
x = np.arange(hca_df.shape[0])
width = 0.5
ax.grid(True, axis='y', zorder=5)
rects = ax.bar(x, hca_df['diff'], width, color=hca_df['Primary'], zorder=10)
ax.set_ylabel('Home Court Advantage')
ax.set_xlabel('Team')
ax.set_xticks(x)
ax.set_xticklabels(hca_df['NBA_Abbr'], rotation=45)
ax.set_title('Home Court Advantage in the NBA, 2010-2020')
fig.text(
  0.99,
  0.01,
  'Graph: Andrew Lawlor, Data: Basketball Reference',
  horizontalalignment='right',
  verticalalignment='bottom',
  fontsize=6,
)
plt.savefig('./output/Home Court Advantages.png')

baldwin_df = df[df['home'] == 'Y']
away_df = df[df['home'] == 'N']
baldwin_df = baldwin_df.groupby(['team1_name', 'season'])[
    ['score_diff']].mean()
away_df = away_df.groupby(['team1_name', 'season'])[
    ['score_diff']].mean()
baldwin_df['away_score_diff'] = away_df['score_diff']
baldwin_df = baldwin_df.reset_index()
baldwin_df['home_court_adv'] = baldwin_df['score_diff'] - baldwin_df['away_score_diff']
baldwin_df = pd.merge(baldwin_df, team_colors_df,
                      left_on='team1_name', right_on='Full')
fig, ax = plt.subplots(figsize=(8, 4), dpi=400)
ax.axhline(0, ls='dotted', color='black')
ax.scatter(rand_jitter(
    baldwin_df['season']), baldwin_df['home_court_adv'], c=baldwin_df['Primary'], alpha=0.3)
# years_df = df[df['home'] == 'Y'].groupby('season')[['score_diff']].mean()
years_df = baldwin_df.groupby('season')[['home_court_adv']].mean()
years_df = years_df.reset_index()
print(baldwin_df[baldwin_df['season'] == 2021].loc[:,['team1_name', 'score_diff']])
ax.plot(years_df['season'], years_df['home_court_adv'], color='black', marker='o')
# team_home_df = baldwin_df[baldwin_df['team1_name'] == 'Chicago Bulls']
# ax.plot(team_home_df['season'], team_home_df['score_diff'], color=team_home_df['Primary'].iloc[0], marker='o')
seasons = years_df['season'].tolist()
ax.set_xticks(seasons)
ax.grid(True, axis='y')
labels = [f'{x-1}-{x % 1000}' for x in seasons]
ax.set_xticklabels(labels, fontsize=8)
ax.set_title('Home Court Advantage in the NBA', y=1.05)
ax.set_ylabel('Home Court Advantage')
ax.set_xlabel('Season')
fig.text(
    0.5,
    0.9,
    '2009-10 to 2020-21 Regular Seasons, Bubble Games Removed',
    horizontalalignment='center',
    verticalalignment='bottom',
    fontsize=10,
)
fig.text(
  0.99,
  0.02,
  'Graph: Andrew Lawlor, Data: Basketball Reference',
  horizontalalignment='right',
  verticalalignment='bottom',
  fontsize=6,
)
fig.text(
  0.99,
  0.01,
  'h/t Ben Baldwin',
  horizontalalignment='right',
  verticalalignment='center',
  fontsize=6,
)
plt.savefig('./output/Baldwin NBA.png')

# df = df[(df['rest'] <= 50) & (df['prev_game_date'].notnull())]
df.loc[df['rest'] >= 5, 'rest'] = 5
rest_df1 = df.groupby(['rest'])[['won']].mean()
rest_df1['count'] = df.groupby(['rest'])['won'].count()


rest_df = df.groupby(['home', 'rest'])[['won']].mean()
rest_df['count'] = df.groupby(['home', 'rest'])['won'].count()
print(rest_df)
fig, ax = plt.subplots(dpi=400)
ax.grid(True, axis='y', zorder=5)
ax.plot(rest_df1.index, rest_df1['won'], marker='o',
        color='black', linestyle='solid', label='Overall')
ax.plot(rest_df.loc['Y', :].index, rest_df.loc['Y', :]['won'],
        marker='o', color='black', linestyle='dashed', label='Home Teams')
ax.plot(rest_df.loc['N', :].index, rest_df.loc['N', :]['won'],
        marker='o', color='black', linestyle='dotted', label='Away Teams')
ax.set_xlabel('Days Rest')
ax.set_ylabel('Win Percentage')
ax.set_ylim([.3, .7])
ax.set_xticks([1, 2, 3, 4, 5])
ax.set_xticklabels(['1', '2', '3', '4', '>= 5'])
ax.legend()
ax.set_title('Impact of Rest in the NBA, 2010-2020')
fig.text(
  0.99,
  0.01,
  'Graph: Andrew Lawlor, Data: Basketball Reference',
  horizontalalignment='right',
  verticalalignment='bottom',
  fontsize=6,
)
plt.savefig('./output/Rest vs WP.png')

df.loc[df['rest_diff'] <= -2, 'rest_diff'] = -2
df.loc[df['rest_diff'] >= 2, 'rest_diff'] = 2
rest_diff_df1 = df.groupby(['rest_diff'])[['won']].mean()
rest_diff_df = df.groupby(['home', 'rest_diff'])[['won']].mean()
rest_diff_df['count'] = df.groupby(['home', 'rest_diff'])['won'].count()
fig, ax = plt.subplots(dpi=400)
ax.grid(True, axis='y', zorder=5)
ax.plot(rest_diff_df1.index, rest_diff_df1['won'], marker='o',
        color='black', linestyle='solid', label='Overall')
ax.plot(rest_diff_df.loc['Y', :].index, rest_diff_df.loc['Y', :]['won'],
        marker='o', color='black', linestyle='dashed', label='Home Teams')
ax.plot(rest_diff_df.loc['N', :].index, rest_diff_df.loc['N', :]['won'],
        marker='o', color='black', linestyle='dotted', label='Away Teams')
ax.set_xlabel('Difference in Days Rest')
ax.set_ylabel('Win Percentage')
ax.set_ylim([.3, .7])
ax.legend()
ax.set_xticks([-2, -1, 0, 1, 2])
ax.set_xticklabels(['<= -2', '-1', '0', '1', '>= 2'])
ax.set_title('Impact of Rest Differences in the NBA, 2010-2020')
fig.text(
  0.99,
  0.01,
  'Graph: Andrew Lawlor, Data: Basketball Reference',
  horizontalalignment='right',
  verticalalignment='bottom',
  fontsize=6,
)
plt.savefig('./output/Rest Diff vs WP.png')
print(rest_diff_df)

df.loc[df['game_of_trip'] >= 7, 'game_of_trip'] = 7
game_of_trip_df = df.groupby(['game_of_trip'])[['won']].mean()
game_of_trip_df['count'] = df.groupby(['game_of_trip'])[['won']].count()
game_of_trip_df['num_trips'] = game_of_trip_df['count'] - game_of_trip_df['count'].shift(-1)
game_of_trip_df.loc[game_of_trip_df['num_trips'].isnull(), 'num_trips'] = game_of_trip_df['count']
game_of_trip_df['pct'] = game_of_trip_df['num_trips'] / game_of_trip_df['num_trips'].sum()
game_of_trip_df['sum_of_sums'] = game_of_trip_df['num_trips']*game_of_trip_df.index
print(game_of_trip_df['sum_of_sums'].sum() / game_of_trip_df['num_trips'].sum())
print(game_of_trip_df)
fig, ax = plt.subplots(dpi=400)
ax.grid(True, axis='y', zorder=5)
ax.plot(game_of_trip_df.index,
        game_of_trip_df['won'], marker='o', color='black', linestyle='solid')
ax.set_xticks([1, 2, 3, 4, 5, 6, 7])
ax.set_xticklabels(['1', '2', '3', '4', '5', '6', '>= 7'])
ax.set_xlabel('Game # on Trip')
ax.set_ylabel('Win Percentage')
ax.set_ylim([.35, .55])
ax.set_title('Impact of Trip Length in the NBA, 2010-2020')
fig.text(
  0.99,
  0.01,
  'Graph: Andrew Lawlor, Data: Basketball Reference',
  horizontalalignment='right',
  verticalalignment='bottom',
  fontsize=6,
)
plt.savefig('./output/Game on Trip vs WP.png')

# df[(df['game_of_trip'].notnull()) & (
#     df['game_of_trip'] > 10)].to_csv('long_road_trip.csv')

df['had_timezone_change'] = np.abs(df['timezone_change']) > 0
df.loc[df['home_timezone_change'] >= 2, 'home_timezone_change'] = 2
df.loc[df['home_timezone_change'] <= -2, 'home_timezone_change'] = -2
df['home_timezone_change'] = df['home_timezone_change'] * -1
print(df.loc[df['home_timezone_change'] ==
             2, ['team1_name', 'location']].head())
home_timezone_change_df = df[df['home'] == 'N'].groupby(
    ['home_timezone_change'])[['won']].mean()
home_timezone_change_df['count'] = df[df['home'] == 'N'].groupby(
    ['home_timezone_change'])[['won']].count()
fig, ax = plt.subplots(dpi=400)
x = [-2, -1, 0, 1, 2]
ax.bar(x,
      home_timezone_change_df['won'], color='#1d428a')
ax.set_xlabel('Difference From Home Timezone')
ax.set_ylabel('Win Percentage')
ax.set_xticks(x)
ax.set_xticklabels(['<= -2', '-1', '0', '1', '>= 2'], fontsize=8)
ax.set_ylim([.3, .5])
ax.set_title('Impact of Timezone Changes on NBA Road Games, 2010-2020')
fig.text(
  0.99,
  0.0,
  'Graph: Andrew Lawlor, Data: Basketball Reference',
  horizontalalignment='right',
  verticalalignment='bottom',
  fontsize=8,
)
plt.savefig('./output/Timezone Change vs WP.png')
print(home_timezone_change_df)

timezone_change_df = df.groupby(['home', 'timezone_change'])[['won']].mean()
timezone_change_df['count'] = df.groupby(
    ['home', 'timezone_change'])[['won']].count()
print(timezone_change_df)

df['travel_distance_binned'] = pd.cut(
    df['travel_distance'], [0, 500, 1000, 1500, 2000, 2500, 3000])
travel_df = df.groupby(['home', 'travel_distance_binned'])[['won']].mean()
travel_df['count'] = df.groupby(['home', 'travel_distance_binned'])[
    ['won']].count()
print(travel_df)

df['trip_distance_binned'] = pd.cut(df['total_trip_distance'], [
                                    0, 1000, 2000, 3000, 4000, 5000, 6000])
travel_df = df.groupby(['home', 'trip_distance_binned'])[['won']].mean()
travel_df['count'] = df.groupby(['home', 'trip_distance_binned'])[
    ['won']].count()
print(travel_df)

df['attendance_pct'] = df['attendance'] / df['attendance_capacity']
df['attendance_pct_bin'] = pd.cut(
    df['attendance_pct'], [0, .80, .85, .90, .95, 1])
attendance_df = df.groupby(['home', 'attendance_pct_bin'])[['won']].mean()
attendance_df['count'] = df.groupby(
    ['home', 'attendance_pct_bin'])[['won']].count()
attendance_df = attendance_df.reset_index()
home_attendance_df = attendance_df[attendance_df['home'] == 'Y']
away_attendance_df = attendance_df[attendance_df['home'] == 'N']
fig, ax = plt.subplots(figsize=(10, 6), dpi=400)
x = np.arange(home_attendance_df.shape[0])
width = 0.35
ax.grid(True, axis='y', zorder=5)
rects = ax.bar(x - width/2, home_attendance_df['won'], width, color='#1d428a', zorder=10, label='Home')
rects = ax.bar(x + width/2, away_attendance_df['won'], width, color='#c8102e', zorder=10, label='Away')
ax.set_ylabel('Win Percentage')
ax.set_xlabel('Percentage of Capacity')
ax.set_xticks(x)
ax.set_xticklabels(['<= 80%', '80-85%', '85-90%', '90-95%', ' >= 95%'])
ax.set_title('The Impact of Home Attendance in the NBA, 2010-2020')
ax.legend()
fig.text(
  0.99,
  0.01,
  'Graph: Andrew Lawlor, Data: Basketball Reference',
  horizontalalignment='right',
  verticalalignment='bottom',
  fontsize=8,
)
plt.savefig('./output/Attendance vs WP.png')