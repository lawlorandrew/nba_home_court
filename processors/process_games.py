import pandas as pd
import datetime
import numpy as np
import math

years = [
  # '2021',
  '2020',
  '2019',
  '2018',
  '2017',
  '2016',
  '2015',
  '2014',
  '2013',
  '2012',
  '2011',
  '2010'
]

def get_distance(lat1, lat2, long1, long2):
  return np.sqrt(np.square(lat1*69 - lat2*69) + np.square(long1*54.6 - long2*54.6))

def isNaN(string):
    return string != string

def recursive_trip_finder(row, game_number):
  if (game_number > 11):
    return 11
  if ((row['team1_name'] != row[f'{game_number}prev_game_location']) & (~isNaN(row[f'{game_number}prev_game_location']))):
    return recursive_trip_finder(row, game_number + 1)
  else:
    return game_number

def find_game_number_of_trip(row):
  if (row['home'] == 'Y' or row['location'] == 'Bubble'):
    return np.nan
  elif row['prev_game_location'] == row['team1_name']:
    return 1
  else:
    return recursive_trip_finder(row, 2)

def recursive_distance_finder(row, distance, game_number):
  prev_game_number = game_number - 1
  if (prev_game_number == 1):
    prev_game_number = ''
  if (game_number > 11):
    return distance
  if ((row['team1_name'] != row[f'{game_number}prev_game_location']) & (~isNaN(row[f'{game_number}prev_game_location']))):
    distance += get_distance(row[f'{game_number}prev_game_lat'], row[f'{prev_game_number}prev_game_lat'], row[f'{game_number}prev_game_long'], row[f'{prev_game_number}prev_game_long'])
    return recursive_distance_finder(row, distance, game_number + 1)
  else:
    return distance + get_distance(row[f'{game_number}prev_game_lat'], row[f'{prev_game_number}prev_game_lat'], row[f'{game_number}prev_game_long'], row[f'{prev_game_number}prev_game_long'])

def find_total_trip_distance(row):
  if (row['home'] == 'Y' or row['location'] == 'Bubble'):
    return np.nan
  elif row['prev_game_location'] == row['team1_name']:
    return get_distance(row['Lat'], row['prev_game_lat'], row['Long'], row['prev_game_long'])
  else:
    distance = get_distance(row['Lat'], row['prev_game_lat'], row['Long'], row['prev_game_long'])
    return recursive_distance_finder(row, distance, 2)


total_df = pd.DataFrame()
location_df = pd.read_csv('./data/locations.csv')
for year in years:
  df = pd.read_csv(f'./data/scores_{year}.csv')
  df['season'] = year
  df['location'] = df['home_team_name']
  df['date'] = pd.to_datetime(df['game_date'])
  df = df[df['date'] < datetime.datetime(year=2021, month=1,day=3)]
  df['attendance'] = df['attendance'].fillna(0)
  df.loc[df['date'] > datetime.datetime(year=2020,month=7, day=1) , 'location'] = 'Bubble'
  home_df = pd.DataFrame(df)
  home_df = home_df.rename(columns={
    'home_team_name': 'team1_name',
    'visitor_team_name': 'team2_name',
    'home_pts': 'team1_pts',
    'visitor_pts': 'team2_pts'
  })
  home_df['home'] = 'Y'
  away_df = pd.DataFrame(df)
  away_df = away_df.rename(columns={
    'home_team_name': 'team2_name',
    'visitor_team_name': 'team1_name',
    'home_pts': 'team2_pts',
    'visitor_pts': 'team1_pts'
  })
  away_df['home'] = 'N'
  print(year)
  combined_df = home_df.append(away_df, ignore_index=True)
  combined_df = pd.merge(combined_df, location_df, left_on='location', right_on='Location')
  combined_df = combined_df.drop(columns='Location')
  combined_df = pd.merge(combined_df, location_df, left_on='team1_name', right_on='Location', suffixes=['', '_home'])
  combined_df = combined_df.sort_values(by='date', ascending=True)
  combined_df['prev_game_date'] = combined_df.groupby('team1_name')['date'].shift(1)
  combined_df['prev_game_location'] = combined_df.groupby('team1_name')['location'].shift(1)
  combined_df['prev_game_lat'] = combined_df.groupby('team1_name')['Lat'].shift(1)
  combined_df['prev_game_long'] = combined_df.groupby('team1_name')['Long'].shift(1)
  combined_df['prev_opponent'] = combined_df.groupby('team1_name')['team2_name'].shift(1)
  combined_df['opp_prev_game_date'] = combined_df.groupby('team2_name')['date'].shift(1)
  combined_df['opp_prev_game_location'] = combined_df.groupby('team2_name')['location'].shift(1)
  combined_df['opp_prev_game_lat'] = combined_df.groupby('team2_name')['Lat'].shift(1)
  combined_df['opp_prev_game_long'] = combined_df.groupby('team2_name')['Long'].shift(1)
  for i in range(10):
    combined_df[f'{i+2}prev_game_location'] = combined_df.groupby('team1_name')['location'].shift(i+2)
    combined_df[f'{i+2}prev_game_lat'] = combined_df.groupby('team1_name')['Lat'].shift(i+2)
    combined_df[f'{i+2}prev_game_long'] = combined_df.groupby('team1_name')['Long'].shift(i+2)
  combined_df['game_of_trip'] = combined_df.apply(lambda x: find_game_number_of_trip(x), axis=1)
  combined_df['total_trip_distance'] = combined_df.apply(lambda x: find_total_trip_distance(x), axis=1)
  combined_df['prev_game_timezone'] = combined_df.groupby('team1_name')['Timezone'].shift(1)
  # remove the first games of the season
  combined_df['rest'] = (combined_df['date'] - combined_df['prev_game_date']).dt.days
  combined_df['opp_rest'] = (combined_df['date'] - combined_df['opp_prev_game_date']).dt.days
  combined_df['rest_diff'] = combined_df['rest'] - combined_df['opp_rest']
  combined_df['timezone_change'] = combined_df['Timezone'] - combined_df['prev_game_timezone']
  combined_df['home_timezone_change'] = combined_df['Timezone'] - combined_df['Timezone_home']
  combined_df['travel_distance'] = np.sqrt(np.square(combined_df['Lat']*69 - combined_df['prev_game_lat']*69) + np.square(combined_df['Long']*54.6 - combined_df['prev_game_long']*54.6))
  combined_df['is_series_game2'] = (combined_df['prev_game_location'] == combined_df['location']) & (combined_df['team2_name'] == combined_df['prev_opponent'])
  combined_df['won'] = combined_df['team1_pts'] > combined_df['team2_pts']
  combined_df['won_prev_game'] = combined_df.groupby('team1_name')['won'].shift(1)
  total_df = total_df.append(combined_df, ignore_index=True)
teams = [
  ('New Jersey Nets', 'Brooklyn Nets'),
  ('Charlotte Bobcats', 'Charlotte Hornets'),
  ('New Orleans Hornets', 'New Orleans Pelicans')
]
for team in teams:
  total_df.loc[total_df['team1_name'] == team[0], ['team1_name']] = team[1]
  total_df.loc[total_df['team2_name'] == team[0], ['team2_name']] = team[1]
total_df = total_df.drop('Unnamed: 0', axis=1)
print(total_df.groupby(['home'])[['won']].count())
total_df['attendance'] = total_df['attendance'].str.replace(',','').astype(float)
print(total_df['attendance'])
location_grouped = total_df.groupby('location')['attendance'].max()
total_df = pd.merge(total_df, location_grouped, left_on='location', right_on='location', suffixes=['', '_capacity'])
total_df.to_csv('./data/combined_scores.csv')