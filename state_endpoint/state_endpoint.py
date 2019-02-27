import os

from flask import jsonify

from PyPiBackend import app


######################
## PHYSICAL ACTIONS ##
######################

###################
###### OTHERS #####
###################

@app.route('/state')
def get_current_state():
    p = os.popen(
        "ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1' | grep '192.*'")
    lines = p.read()
    return jsonify({'ip': lines.rstrip()})

