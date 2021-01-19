import configparser
import os
import logging
import sys
import json
from json.decoder import JSONDecodeError

import pandas as pd
import spotipy
import spotipy.util as util

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)


SEARCH_LIMIT = 50
MAX_NUM_SONG_PER_YEAR = 2000
FILE_NAME = "./datasets/2010_2019.csv"
#DEFAULT_FILTER = '0.9 > danceability > 0.5 & 0.8 > energy > 0.6 & speechiness < 0.05 & acousticness < 0.2 & instrumentalness > 0.8 & 0.5 < valence & 130 > tempo > 95 & mode == 1'
DEFAULT_FILTER  = 'key == 5 & 0.3 < danceability < 0.6 & 120> tempo > 100 & speechiness < 0.1 & instrumentalness > 0.8  & valence < 0.6 &acousticness < 0.3'
PLAYLIST_NAME = DEFAULT_FILTER

SCOPE = "user-read-private user-read-playback-state " \
        "user-modify-playback-state playlist-modify-private " \
        "playlist-read-collaborative playlist-read-private"
USERNAME = "TakatoMatsumoto"
USER = '31r7nzies564uss4curuj46b6idm'


class Spotify(object):
    def __init__(self, username=USERNAME, scope=SCOPE, user=USER):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.client_id = config['DEFAULT']['SPOTIPY_CLIENT_ID']
        self.client_secret = config['DEFAULT']['SPOTIPY_CLIENT_SECRET']
        self.redirect_uri = config['DEFAULT']['SPOTIPY_REDIRECT_URI']

        self.user = user
        self.scope = scope
        self.username = username

        self.authorize()

    def authorize(self):
        # The tokens expire after 1 hour
        try:
            token = util.prompt_for_user_token(self.username, self.scope,
                                               client_id=self.client_id,
                                               client_secret=self.client_secret,
                                               redirect_uri=self.redirect_uri)
        except (AttributeError, JSONDecodeError):
            os.remove(f".cache-{self.username}")
            token = util.prompt_for_user_token(self.username, self.scope,
                                               client_id=self.client_id,
                                               client_secret=self.client_secret,
                                               redirect_uri=self.redirect_uri)
        self.sp = spotipy.Spotify(auth=token)

    def get_audio_features(self, file_name=FILE_NAME, start_year=2010, end_year=2010):

        audio_features = []
        #markets = ['US', 'JP', 'GB', 'AU', 'BR', 'DE', 'DK', 'IT']
        markets = ['JP']
        for market in markets:
            year = start_year

            while year <= end_year:
                q = 'year:' + str(year)
                offset = 0
                logger.info(f'{market}: {year}')

                while offset < MAX_NUM_SONG_PER_YEAR:
                    try:
                        results = self.sp.search(q=q,
                                           type='track',
                                           market=market,
                                           limit=SEARCH_LIMIT,
                                           offset=offset)
                    except:
                        self.authorize()
                        break

                    for r in results['tracks']['items']:
                        try:
                            audio_feature = self.sp.audio_features(r['id'])
                            if audio_feature[0] is None:
                                continue
                            audio_feature[0]['name'] = r['name']
                            audio_feature[0]['year'] = year
                            audio_feature[0]['market'] = market
                            audio_features += audio_feature

                        except:
                            self.authorize()
                            audio_feature = self.sp.audio_features(r['id'])
                            if audio_feature[0] is None:
                                continue
                            audio_feature[0]['name'] = r['name']
                            audio_feature[0]['year'] = year
                            audio_feature[0]['market'] = market
                            audio_features += audio_feature
                        logger.info(audio_feature)
                    offset += 50

                year += 1

        self.df = pd.DataFrame(audio_features)
        self.df.to_csv(file_name, index=False)

    def display_playlists(self):
        playlists = self.sp.user_playlists(self.user)
        while playlists:
            for i, playlist in enumerate(playlists['items']):
                print("%4d %s %s" % (
                i + 1 + playlists['offset'], playlist['uri'], playlist['name']))
            if playlists['next']:
                playlists = self.sp.next(playlists)
            else:
                playlists = None

    def get_playlist_uri(self, playlist_name=PLAYLIST_NAME):
        playlists = self.sp.user_playlists(self.user)
        while playlists:
            for playlist in playlists['items']:
                if playlist['name'] == playlist_name:
                    return playlist['uri']
            if playlists['next']:
                playlists = self.sp.next(playlists)
            else:
                playlists = None
        return None

    def make_playlist(self, file_name=FILE_NAME, playlist_name=PLAYLIST_NAME):
        self.authorize()
        self.df = pd.read_csv(file_name)
        tracks_list = list(set(self.df['uri'].to_list()))

        playlist_id = self.get_playlist_uri()
        if playlist_id is None:
            self.sp.user_playlist_create(user=self.user,
                                         name=playlist_name,
                                         public=False,
                                         description="")
            playlist_id = self.get_playlist_uri()

        offset = 100
        for i in range(0, len(tracks_list), offset):
            tracks = tracks_list[i:i + offset]
            self.sp.user_playlist_add_tracks(user=self.user,
                                             playlist_id=playlist_id,
                                             tracks=tracks)

    def delete_playlists(self):
        playlists = self.sp.user_playlists(self.user)
        while playlists:
            for i, playlist in enumerate(playlists['items']):
                playlist_id = playlist['uri'][17:]
                self.sp.user_playlist_unfollow(user=self.user,
                                               playlist_id=playlist_id)
            if playlists['next']:
                playlists = self.sp.next(playlists)
            else:
                playlists = None

    def filter_metadata(self, file_name=FILE_NAME, filter=DEFAULT_FILTER):
        df = pd.read_csv(file_name)
        df = df.query(filter)
        df.to_csv('./datasets/' + 'filtered_' + file_name[11:], index=False)

    def play_music(self):
        devices = self.sp.devices()
        print(json.dumps(devices, sort_keys=True, indent=4))
        device_id = devices['devices'][0]['id']
        self.sp.start_playback(context_uri=self.get_playlist_uri(),
                               device_id=device_id)

    def get_audio_features_from_playlist(self,
                                         file_name='./datasets/playlist.csv',
                                         playlist_id='spotify:playlist:2ToOpjk7FkW2GeFnYgPQtZ'):
        audio_features = []
        results = self.sp.playlist(playlist_id=playlist_id)
        results = results['tracks']['items']
        print(json.dumps(results, sort_keys=True, indent=4))
        results = [r.get('track') for r in results]
        results = [r.get('uri') for r in results]

        # get song name from json file

        for i, r in enumerate(results):
            try:
                audio_feature = self.sp.audio_features(r)

                if audio_feature[0] is None:
                    continue
                audio_features += audio_feature

            except:
                self.authorize()
                audio_feature = self.sp.audio_features(r)
                audio_feature[0]['name'] = r['name']
                if audio_feature[0] is None:
                    continue
                audio_features += audio_feature
            logger.info(audio_feature)
        self.df = pd.DataFrame(audio_features)
        self.df.to_csv(file_name, index=False)

    def get_current_playback(self):
        print(self.sp.current_playback(market=None))


if __name__ == "__main__":
    spotify = Spotify()
    spotify.get_current_playback()

    #spotify.get_audio_features()
    #spotify.get_audio_features_from_playlist(file_name='./datasets/vivaldi_radio.csv',
                                             #playlist_id='spotify:playlist:37i9dQZF1E8PjwpUAwTsiG')
    #spotify.filter_metadata(file_name='./datasets/2010_2019_backup.csv')
    #spotify.make_playlist(file_name='./datasets/filtered_2010_2019_backup.csv')
    #spotify.delete_playlists()
    #spotify.display_playlists()
    #spotify.play_music()

