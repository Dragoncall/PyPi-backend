from flask import request, jsonify

import song_endpoint.song_endpoints_v2
from PyPiBackend import app


class BluetoothStore:
    _instance = None

    def __init__(self):
        self.bluetooth = False

    def toggle_bluetooth(self):
        self.set_bluetooth(not self.bluetooth)

    def get_bluetooth(self):
        return self.bluetooth

    def set_bluetooth(self, active):
        self.bluetooth = active
        song_endpoint.SongRepository.get_instance().set_pause(int(active))
        # TODO: Setup bluetooth connection here

    @staticmethod
    def get_instance():
        if BluetoothStore._instance is None:
            BluetoothStore._instance = BluetoothStore()
        return BluetoothStore._instance


@app.route('/songs/bluetooth', methods=['POST'])
def set_bluetooth():
    x = request.json['bluetooth']
    BluetoothStore.get_instance().set_bluetooth(x)
    return jsonify({'success': True})

@app.route('/songs/bluetooth', methods=['GET'])
def get_bluetooth():
    return jsonify({'bluetooth': BluetoothStore.get_instance().get_bluetooth()})
