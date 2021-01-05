from bs4 import BeautifulSoup
import requests
import pandas as pd
import time

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
months = [
  'october',
  'november',
  'december',
  'january',
  'february',
  'march',
  'april',
  'may',
  'june',
  'july',
  'august',
  'september'
]
for year in years:
  totals_df = pd.DataFrame()
  for month in months:
    url = (f"https://www.basketball-reference.com/leagues/NBA_{year}_games-{month}.html")
    req = requests.get(url)
    soup = BeautifulSoup(req.content, "html.parser")
    body = soup.find('tbody')
    if (body):
      rows = body.find_all('tr', class_=lambda x: x is None)
      for row in rows:
        row_data = pd.Series()
        tds = row.find_all('td')
        for td in tds:
          row_data[td['data-stat']] = td.get_text()
        date_el = row.find('th')
        row_data['game_date'] = date_el.get_text()
        totals_df = totals_df.append(row_data, ignore_index=True)
      time.sleep(1)
  totals_df = totals_df[(totals_df['visitor_pts'].notnull()) & (totals_df['visitor_pts'] != '')]
  totals_df = totals_df.reset_index()
  totals_df = totals_df.drop(['index'], axis=1)
  if (year == '2020'):
    totals_df['playoffs'] = 'N'
    totals_df.loc[totals_df.index > 1063, 'playoffs'] = 'Y'
  else:
    totals_df['playoffs'] = 'N'
    totals_df.loc[totals_df.index > 1230, 'playoffs'] = 'Y'
  totals_df.to_csv(f'./data/scores_{year}.csv')
