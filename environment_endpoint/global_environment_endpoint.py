import geoip2.database
import requests
from flask import jsonify, request

from Helpers import get_credential
from PyPiBackend import app


def get_location(ip):
    reader = geoip2.database.Reader('./GeoLite2-City.mmdb')
    response = reader.city(ip)
    location = response.location
    return location.latitude, location.longitude


@app.route('/weather')
def get_weather():
    # Will not work currently
    # location = get_location(request.remote_addr)
    url = "https://api.darksky.net/forecast/{key}/{latitude},{longitude}".format(
        key=get_credential('darksky'),
        latitude='51.0538185',
        longitude='3.7222718'
    )
    params = {
        "units": "ca"
    }
    resp = requests.get(url=url, params=params)
    data = resp.json()
    return jsonify(data)
