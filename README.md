Spotify metadata downloader  
====

## Requirement  
python 3.7.3  
Spotipy 2.9.0 https://spotipy.readthedocs.io/en/2.9.0/   
$pip install spotipy -upgrade


## Usage  
config.iniファイルにSpotifyのユーザー情報を書き込んでください。  
下記のサイトが参考になります。  
https://dev.classmethod.jp/etc/about-using-of-spotify-api/

書き込みが終わったら  
$python3 test.py  
で実行できます。



### メタデータのダウンロード  
get_audio_featuresメソッドでcsvファイルに保存できます。  
csvファイルはdatasetsディレクトリに保存されます。    
start_yearとend_yearで、何年分のデータを取得するか指定できます。  
marketsでどの国のデータを取得するか指定できます。  
ISO_3166-1_alpha-2で指定してください。https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2  
1ヶ国1年分で約2000曲取得できます。取得に5分ほどかかります。  

### メタデータのフィルタリング  
filter_metadataメソッドで指定したcsvファイルのフィルタリングを行います。  
フィルタリング後、"filtered_指定したファイル名"というcsvファイルが生成されます。  
フィルタ条件を指定しないとDEFAULT_FILTERが適応されます。
フィルタ条件は以下のサイトが参考になります。  
https://developer.spotify.com/documentation/web-api/reference/tracks/get-audio-features/  

  
### プレイリストの作成  
make_playlistメソッドで、指定したcsvファイルを使ってプレイリストを作成できます。  
  
### プレイリストの削除  
delete_playlistメソッドでユーザーのプレイリストを全て削除します。  
  
### プレイリストの表示  
display_playlistメソッドでユーザーのプレイリストを全て表示します。  
  
### プレイリストの再生  
play_musicメソッドで指定したプレイリストが再生できるが、あまり使わないかも。  

  
## Author  
Takato Matsumoto  # collect_spotify_data
