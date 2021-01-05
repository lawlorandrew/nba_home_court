import pandas as pd
import numpy as np

df = pd.read_csv('./data/2021_combined_scores.csv')

# df.loc[df['rest'] >= 5, 'rest'] = 5
rest_df1 = df.groupby(['rest', 'home'])[['won']].count()
print(rest_df1)

road_trip_df = df.groupby(['game_of_trip'])[['won']].count()
road_trip_df['num_trips'] = road_trip_df['won'] - road_trip_df['won'].shift(-1)
road_trip_df.loc[road_trip_df['num_trips'].isnull(), 'num_trips'] = road_trip_df['won']
road_trip_df['pct'] = road_trip_df['num_trips'] / road_trip_df['num_trips'].sum()
road_trip_df['sum_of_sums'] = road_trip_df['num_trips']*road_trip_df.index
print('avg trip length')
print(road_trip_df['sum_of_sums'].sum()/road_trip_df['num_trips'].sum())
print(road_trip_df)