import json

import soundcloud
from youtube_dl import DownloadError

import vlc
from flask import jsonify, request
import youtube_dl

from PyPiBackend import app

vlc_instance = vlc.Instance()
client = soundcloud.Client(client_id='61ce54eef3c8639b05a95bb03af632d8')


class SongRepository:
    _instance = None

    def __init__(self):
        self.song_list = []
        self.init()

    def reset(self):
        self.pause()
        self.song_list = []
        self.media_list_player.release()
        self.init()

    def init(self):
        self.media_list_player = vlc_instance.media_list_player_new()
        self.media_list_player.set_media_player(vlc_instance.media_player_new())
        self.media_list = vlc_instance.media_list_new()
        self.media_list_player.set_media_list(self.media_list)

    def current_song(self):
        media = self.media_list_player.get_media_player().get_media()
        index = self.media_list.index_of_item(media)
        return index

    def set_index(self, index):
        self.media_list_player.play_item_at_index(index)

    def get_songs(self):
        return self.song_list

    def add_songs(self, song):
        self.song_list.append(song)
        media = vlc_instance.media_new(song['url'])
        self.media_list.add_media(media)
        if not self.is_playing():
            self.media_list_player.play()

    def has_songs(self):
        return len(self.song_list) != 0

    def next_song(self):
        self.media_list_player.next()

    def previous_song(self):
        self.media_list_player.previous()

    def is_playing(self):
        return bool(self.media_list_player.is_playing())

    def pause(self):
        self.media_list_player.pause()

    def length_song(self, index):
        return self.media_list.item_at_index(index).get_duration()

    def time_current_song(self):
        return self.media_list.get_media_player().get_time()

    @staticmethod
    def get_instance():
        if SongRepository._instance is None:
            SongRepository._instance = SongRepository()
        return SongRepository._instance


@app.route('/songs/current_time', methods=['POST'])
def get_time_song():
    return jsonify({'time': SongRepository.get_instance().time_current_song()})


@app.route('/songs/length', methods=['POST'])
def get_length_song():
    repo = SongRepository.get_instance()
    return jsonify({'time': repo.length_song(repo.current_song())})


# TODO: this does not work for some alien reason
@app.route('/pause', methods=['POST'])
def pause_song():
    repo = SongRepository.get_instance()
    repo.pause()
    return jsonify({'success': True, 'playing': repo.is_playing()})


@app.route('/next', methods=['POST'])
def play_next():
    SongRepository.get_instance().next_song()
    return jsonify({'success': True})


@app.route('/previous', methods=['POST'])
def play_previous():
    SongRepository.get_instance().previous_song()
    return jsonify({'success': True})


@app.route('/playsong', methods=['POST'])
def play_at_index():
    index = request.json['index']
    SongRepository.get_instance().set_index(index)
    return jsonify({'success': True})


# Song should be of the format: {url:..., image:..., title: ..., length: ...}
@app.route('/addsong', methods=['POST'])
def add_song():
    song = request.json['song']
    SongRepository.get_instance().add_songs(song)
    return jsonify({'success': True})


# TODO: this shouldn't be a POST
#@app.route('/song', methods=['POST'])
#def delete_song():
#    repo = SongRepository.get_instance()
#    title = request.json['title']
#    repo.remove_songs_by_title(title)
#    return jsonify({'success': True})


@app.route('/songs')
def all_songs():
    repo = SongRepository.get_instance()
    return jsonify({"index": repo.current_song(), "songs": {i: value for i, value in enumerate(repo.get_songs())}})


@app.route('/reset', methods=['POST'])
def reset():
    repo = SongRepository.get_instance()
    repo.reset()
    return jsonify({"index": repo.current_song(), "songs": {i: value for i, value in enumerate(repo.get_songs())}})


@app.route('/addsong/soundcloud', methods=['POST'])
def add_soundcloud_song():
    result_song = {}
    track = client.get('/resolve', url=request.json['song'])
    if not track:
        return jsonify({'error': 'Invalid Track'})
    result_song['image'] = track.artwork_url
    result_song['title'] = track.title
    result_song['length'] = track.duration
    result_song['url'] = client.get(track.stream_url, allow_redirects=False).location
    repo = SongRepository.get_instance()
    repo.add_songs(result_song)
    return jsonify(result_song)


@app.route('/search-soundcloud', methods=['GET'])
def soundcloudSearch():
    query = request.args.get('query', default='test', type=str)
    tracks = client.get('/tracks', q=query, limit=20)
    track_list = []
    for track in tracks:
        track_list.append(
            {'image': track.artwork_url, 'title': track.title, 'length': track.duration, 'url': track.uri})
    print(track_list)
    return jsonify(track_list)


@app.route('/search-youtube', methods=['GET'])
def youtubeSearch():
    query = request.args.get('query', default='test', type=str)

    ydl_opts = {
        'verbose': True,
        'skip_download': True,
        'forcetitle': True,
        'forceurl': True,
        'forcethumbnail': True,
        'forceduration': True,
        'ignoreerrors': True,
        'default_search': "ytsearch5",
        'no_check_certificate': True
    }

    format_whitelist = ['249', '250', '251']

    def get_format(format_list):
        for format in format_list:
            if format['format_id'] in format_whitelist:
                return format['url']

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url=query)
            return jsonify([
                {
                    'image': track['thumbnail'],
                    'title': track['title'],
                    'length': track['duration'],
                    'url': get_format(track['formats'])
                } for track in info['entries'] if track is not None
            ])
    except DownloadError as e:
        return jsonify([])
