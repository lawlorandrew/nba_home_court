import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('./data/2021_combined_scores.csv')
series_df = df[df['is_series_game2'] == True]
series_df['same_winner'] = series_df['won'] == series_df['won_prev_game']
print(series_df.loc[:,['team1_name', 'team2_name', 'same_winner', 'rest']])
print(series_df['same_winner'].mean())
print(series_df.groupby('rest')['same_winner'].mean())
print(series_df.groupby('home')['won'].mean())