#!venv/bin/python
# 
# Copyright 2013 Jeremy Hall
# 
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
# 
#      http://www.apache.org/licenses/LICENSE-2.0
# 
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
# 

from flask import Flask
from flask import jsonify
from flask import make_response
from flask import request
from flask import abort
from werkzeug.exceptions import BadRequest

import stellarnet
import time
import json

app = Flask(__name__)

class Spectrometers(object):
    _map = None

    def _get_map(self):
        global _map

        if not Spectrometers._map:
            Spectrometers._map = {d.get_device_id():{'device':d,'config_id':0} \
                                      for d in stellarnet.find_devices()}
            
        return Spectrometers._map

    def __getitem__(self, device_id):
        try:
            return self._get_map()[device_id]
        except KeyError:
            abort(404)

    def get_device_ids(self):
        return self._get_map().keys()

spectrometers = Spectrometers()

@app.route('/spectrometers', methods = ['GET'])
def get_spectrometers():
    return jsonify({'device_ids':spectrometers.get_device_ids()})

@app.route('/spectrometers/<device_id>/config', methods = ['GET', 'PUT'])
def handle_config(device_id):
    spectro = spectrometers[device_id]
    device = spectro['device']
    if request.method == 'GET':
        return jsonify(device.get_config())
    else:
        try:
            config = request.get_json(force=True)
            device.set_config(**config)
        except BadRequest:
            return make_response(jsonify({'error':'json formatting'}), 400)
        except stellarnet.ArgRangeError as e:
            return make_response(jsonify({'error':'out of range: {}'.format(e.message)}), 400)
        else:
            config_id = spectro['config_id'] + 1
            spectro['config_id'] = config_id
            return jsonify({'config_id':config_id})

@app.route('/spectrometers/<device_id>/spectrum', methods = ['GET'])
def get_spectrum(device_id):
    spectro = spectrometers[device_id]
    return jsonify({'data':spectro['device'].read_spectrum(), 
                    'timestamp':int(time.time()*1000),
                    'config_id':spectro['config_id']})
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
