import logging
from logging import handlers
from flask import Flask,render_template, request, g
from flask import Flask, request, flash, url_for, redirect, \
     render_template, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_socketio import SocketIO, send, emit
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
import threading
import urllib
import requests
import json
import math
import os
import time
from datetime import datetime, timedelta
#import numpy as np
import sys
import random
import io
import dateutil.parser
from random import randrange
from werkzeug.datastructures import MultiDict
from queue import Queue, LifoQueue
import isobar as iso
from itertools import count
level    = logging.NOTSET
format   = '%(asctime)-8s %(levelname)-8s %(message)s'
formatter = logging.Formatter(format,"%Y-%m-%d %H:%M:%S")
writer = logging.StreamHandler()
writer.setFormatter(formatter)
handlers = [writer,logging.handlers.TimedRotatingFileHandler('thermo',when="D",interval=1,backupCount=5,encoding=None,delay=False,utc=False,atTime=None)]
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("isobar").setLevel(logging.INFO)
#some good info here, remove to debug better.
# logging.getLogger('socketio').setLevel(logging.ERROR)
# logging.getLogger('engineio').setLevel(logging.ERROR)

thread_stop_event = threading.Event()
socket_thread = threading.Thread()
#bus = smbus2.SMBus(port)

logging.basicConfig(level = level, format = format, handlers = handlers)


def beat_logger():
    midi_in = iso.MidiInputDevice(device_name="zarandi Bus 1")
    timeline = iso.Timeline(clock_source=midi_in)
    notes = []
    durations = []
    last_note_time = None
    print(song_time)

    print("Listening for notes on %s. Press Ctrl-C to stop." % midi_in.device_name)

    timeline.schedule({"duration":1,"action": try_it, "args":{"timeline":timeline}})#lambda: print(timeline.current_time)})
    timeline.run()
#(self, t_name, t_num, state, start_time, length)
class MyFlaskApp(SocketIO):

  def run(self, app, host=None, port=None, debug=None, load_dotenv=True, **options):

    start_BEAT = threading.Thread(name="BEAT_unit",target=beat_logger, daemon=True)
    start_BEAT.start()


    super(MyFlaskApp, self).run(app=app,host=host, port=port, debug=True, use_reloader=False,**options)

class Track:

    def __init__(self, t_name, t_num, state, start_time, length):

        self.t_name = t_name
        self.t_num = t_num
        self.state = state
        self.start_time = start_time
        self.length = length

    def make_json(self):
        to_pass = {"t_name": self.t_name, "t_num":self.t_num,"state":self.state,"start_time":self.start_time,"length":self.length}

        return to_pass



app = Flask(__name__)
app.config.from_pyfile(os.path.abspath('pod_db.cfg'))
global db
db = SQLAlchemy(app)
song_time = LifoQueue(maxsize=10)
current_time = (0,0)
migrate = Migrate(app,db)
track_list = []

for x in range(8):
    HUMAN_track_num = x+1
    track_list.append(Track("Track " + str(HUMAN_track_num),x,"stopped",(1,1),4))


def try_it(timeline):
    global current_time
    zero_beat = (int(round(timeline.current_time)))
    time_tup = (int((zero_beat//4)+1),int((zero_beat%4)+1))
    song_time.put(time_tup)
    current_time = time_tup

    logging.info(time_tup)
    if song_time.full():
        song_time.queue.clear()

socketio = MyFlaskApp(app)


@app.route('/')
def index():

    
    return render_template('index.html')



def start_over():
    db.reflect()
    db.drop_all()
#(self, t_name, t_num, state, start_time, length)
@app.route('/cliphook', methods=['POST'])
def clip_state():
    
    x = (json.loads(request.data))
    HUMAN_track_num = int(x['track'])+1
    track_list[x['track']] = Track("Track " + str(HUMAN_track_num), x['track'], x['song_state'],x['start_time'],x['length'])
    logging.info('Track ' + str(HUMAN_track_num) + ": " + x['song_state'])
    logging.info(track_list[x['track']])
    for x in range(8):
        socketio.emit('state_change', track_list[x].make_json(), namespace='/thermostat')
    return Response(status=200)

@app.route('/time', methods=['GET'])
def get_time():
    
    socketio.emit('current_time', {'time': current_time}, namespace='/thermostat')
    logging.info("here it is " + str(current_time))
    time.sleep(10)
    return Response(status=200)

@app.route('/livecheck', methods=['POST'])
def live_check():
    x = (json.loads(request.data))

    logging.info("**LIVE: " + str(x))

    return Response(status=200)


@socketio.on('time', namespace='/thermostat')
def get_time_sock():
    socketio.emit('time', {'time': current_time}, namespace='/thermostat')
    
# def temp_sender_thread():
#     """
#     Generate a random number every 1 second and emit to a socketio instance (broadcast)
#     Ideally to be run in a separate thread?
#     """
    
#     logging.info("Sending Number Updates")
#     while not thread_stop_event.isSet():
#         number = int(randrange(100))
#         logging.info(number)
#         socketio.emit('newnumber', {'number': number, 'track_1_text': 'Track 1'}, namespace='/thermostat')
#         socketio.sleep(20)

@socketio.on('connect', namespace='/thermostat')
def temperature_connect():
    # need visibility of the global thread object
    global socket_thread
    print('Client connected')
    thread_stop_event.clear()
    #Start the random number generator thread only if the thread has not been started before.
    # if not socket_thread.isAlive():
    #     print("Starting Thread")
    #     socket_thread = socketio.start_background_task(temp_sender_thread)

@socketio.on('disconnect', namespace='/thermostat')
def temperature_disconnect():

    print('Client disconnected')
    if socket_thread.isAlive():
        global thread_stop_event
        thread_stop_event.set()
        print('Disconected & thread stopped')



if __name__ == "__main__":

    #start_over()
    db.create_all()
    try:
        bootstrap = Bootstrap(app)
        socketio.run(app,host='0.0.0.0',port=1949)
    except:
        sys.exit(0)
