#
#import Live
import sys
from collections import OrderedDict
from functools import partial
from live_rpyc import client

import requests

connections = []

class Carmine:
    __module__ = __name__
    def __init__(self, the_song, the_app):
        #self.instance = c_instance
        self.slisten = {}
        self.clisten = {}
        self.song = the_song
        self.app = the_app
        self.actions = []
        
        print("adding listeners!")
        if self.song.visible_tracks_has_listener(self.addListeners) != 1:
           self.song.add_visible_tracks_listener(self.addListeners)
        
        self.addListeners()
        #self.instance.show_message("CARMINE")

    def refresh_state(self):
        pass

    def add_slotlistener(self, slot, tid, cid):
        cb = lambda :self.slot_changestate(slot, tid, cid)

        if self.slisten.has_key(slot) != 1:
            slot.add_has_clip_listener(cb)
            self.slisten[slot] = cb   
    
    def rem_clip_listeners(self):
        for slot in self.slisten:
            if slot != None:
                if slot.has_clip_has_listener(self.slisten[slot]) == 1:
                    slot.remove_has_clip_listener(self.slisten[slot])
    
        self.slisten = {}

    def slot_changestate(self, slot, tid, cid):
        
        # Added new clip
        if slot.clip != None:
            self.add_cliplistener(slot.clip, tid, cid)
    

    def add_cliplistener(self, clip, tid, cid):
        cb = lambda :self.clip_changestate(clip, tid, cid)
        
        if self.clisten.has_key(clip) != 1:
            clip.add_playing_status_listener(cb)
            self.clisten[clip] = cb
 
    def clip_changestate(self, clip, x, y):
        print("xxxxListener: x: " + str(x) + " y: " + str(y))

        
        state = 1
        if clip.is_playing == 1:
            state = 2
        if clip.is_triggered == 1:
            state = 3
        print(str(clip.name) + " > state:" + str(state))
        
        url = 'http://0.0.0.0:1949/cliphook'
        myobj = {'track': x, 'clip': y, 'state' : state}

        x = requests.post(url, json=(myobj))
        print('past')
          # skip this if names of loaded device is already same as clip we are launching

    def addListeners(self):
        self.rem_clip_listeners()
        
        tracks = self.song.visible_tracks
        clipSlots = []
        for track in tracks:
            clipSlots.append(track.clip_slots)
        tracks = clipSlots
        for track in range(len(tracks)):
            for clip in range(len(tracks[track])):
                c = tracks[track][clip]            
                if c.clip != None:
                    pass
                    self.add_cliplistener(c.clip, track, clip)
                
                self.add_slotlistener(c, track, clip)
   
    ######################## ABLETON STUFF @@@@@@@@@@@@
    def update_display(self):

        for action in self.actions:
            action()
            self.actions.remove(action)
        server.serve()

    def refresh_state(self):
        pass
    def build_midi_map(self, midi_map_handle):
        self.refresh_state()            
            
    def disconnect(self):
        _("Closing session...")
        server.close()
        
    def connect_script_instances(self, instanciated_scripts):
        """
        Called by the Application as soon as all scripts are initialized.
        You can connect yourself to other running scripts here, as we do it
        connect the extension modules
        """
        return

        def send_midi(self, midi_event_bytes):
            pass

    def receive_midi(self, midi_bytes):
        return

    def can_lock_to_devices(self):
        return False

    def suggest_input_port(self):
        return ''

    def suggest_output_port(self):
        return ''

if __name__ == "__main__":


    def current_song_time_listener():
        return
    
    Live = client.connect()
    live_app = Live.Application.get_application()
    song = live_app.get_document()

    print('Connected to Ableton Live {}.{}.{}'.format(live_app.get_major_version(),
        live_app.get_minor_version(), live_app.get_bugfix_version()))
    x = Carmine(song,live_app)
    client.bind(song.add_current_song_time_listener, song.remove_current_song_time_listener,
        current_song_time_listener)

    client.start_thread()

    try:
        input('Try playing/pausing Live or press Enter to exit\n')
    except:
        pass

    client.disconnect()