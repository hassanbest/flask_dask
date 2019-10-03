from collections import Counter

import pandas as pd
import requests
import json


class DataContainer:

    def __init__(self, file):
        """

        :param file:
        """

        self.df = pd.read_csv(file)
        self.df['date'] = pd.to_datetime(self.df.date)
        self.df.sort_values(by=['date'], inplace=True)
        self.df['year'] = pd.to_datetime(self.df['date'], errors='ignore').dt.strftime('%Y')
        yr_mon = self.df['year'].unique()
        self.dates_range = [yr_mon[i] for i in range(0, len(yr_mon))]

    def tweets_by_date(self, dt1=None, dt2=None, col_name='year'):
        """
        This method returns data by date groups and filters data between two dates if dt1 and dt2 are passed.
        :param dt1: (str) date 1
        :param dt2: (str) date 2
        :return:(tuple) dates,freq
        """

        df = self.df
        if dt1 is not None and dt2 is not None:
            df = self.df[(self.df[col_name] >= str(dt1)) & (self.df[col_name] <= str(dt2))]
        df_grps = df.groupby('date')
        date_freq = df_grps['tweet'].count()

        return list(date_freq.index), date_freq.tolist()

    def tweets_by_geo(self):
        """
        This method return frequency of tweets by locations. It groups data by lat long coordinates
        :return: (DataFrame)
        """

        df_grps = self.df.groupby('geo')
        gps_twt_counts = df_grps['tweet'].count()

        lat = pd.Series(gps_twt_counts.index).map(
            lambda x: float(x.split(',')[0].replace('[', '').replace("\'", '').replace(' ', '')))
        long = pd.Series(gps_twt_counts.index).map(
            lambda x: float(x.split(',')[1].replace(']', '').replace("\'", '').replace(' ', '')))

        # gps_twt_text = "Tweets Count: " + df_grps['tweet'].count().astype(str)
        locations = list()
        rev_geocoding_url = 'https://api.opencagedata.com/geocode/v1/json?q={lat}+{long}&key=da805e6ab0df4593bb3310b1aea33809'
        for idx in range(len(lat)):
            try:
                result = json.loads(requests.get(rev_geocoding_url.format(lat=str(lat[idx]), long=str(long[idx]))).text)
                locations.append(str(result['results'][0]['formatted']))
            except:
                locations.append('Not-Fetched')

        return pd.DataFrame(data={'lat':lat, 'long': long, 'number_of_tweets': gps_twt_counts.tolist(),
                                  'location': locations})

    def get_Top_hashtags(self, top_n=20):
        """
        This method returns top_n hashtags in the tweets data
        :param top_n: (int) select top N
        :return: list of tuples [(word, count), ...]
        """
        ls_hashtags = self.df[self.df['hashtags'] != '[]']['hashtags'].sum()
        ls_hashtags = ls_hashtags.replace('[', '', ).replace("\'", '').replace(']', ',').replace(' ', '').split(',')

        # top 20 hashtags
        tokens_with_counts = Counter(ls_hashtags)
        return tokens_with_counts.most_common(top_n)

    def hashtag_freq_by_geo(self, most_common):
        """
        This method returns hashtags by locations. It groups data by lat long coordinates
        :return: (DataFrame)
        """
        ls_top_hashtags = [item[0] for item in most_common]

        geo_groups = self.df.groupby('geo')
        gps_twt_hashs = geo_groups['hashtags'].apply(lambda x: x[x != '[]'].sum().replace('[', '', ).replace("\'", '').replace(']', ',').replace(' ', '').split(','))

        df_data = pd.DataFrame(columns=['location'] + ls_top_hashtags)
        df_data['location'] = gps_twt_hashs.index.tolist()

        for idx in range(0, len(df_data['location'])):
            for tag in ls_top_hashtags:
                df_data.loc[idx, tag] = gps_twt_hashs[idx].count(tag)

        return df_data

    def get_Top_mentions(self, top_n=20):
        """
        This method returns top_n mentions in the tweets data
        :param top_n: (int) select top N
        :return: list of tuples [(word, count), ...]
        """
        ls_mentions = self.df[self.df['mentions'] != '[]']['mentions'].sum()
        ls_mentions = ls_mentions.replace('[', '', ).replace("\'", '').replace(']', ',').replace(' ', '').split(',')

        tokens_with_counts = Counter(ls_mentions)
        return tokens_with_counts.most_common(top_n)
