import os

from flask import jsonify

from PyPiBackend import app

from song_endpoint import SongRepository, BluetoothStore


######################
## PHYSICAL ACTIONS ##
######################

###################
###### OTHERS #####
###################

@app.route('/info')
def get_current_state():
    p = os.popen(
        "ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1'")
    lines = p.read()
    return jsonify({'tracks': not BluetoothStore.get_instance().get_bluetooth(), 'songs': SongRepository.get_instance().song_list, 'ip': lines.rstrip()})

