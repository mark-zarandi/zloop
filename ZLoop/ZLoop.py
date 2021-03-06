import Live
import sys
import os
import json
from collections import OrderedDict
from functools import partial
from _Framework.CompoundComponent import CompoundComponent
from _Framework.ControlSurface import ControlSurface
from _Framework.SubjectSlot import Subject
from ableton.v2.control_surface import ControlSurface as CS
import requests

# from SimpleWebSocketServer import *

# connections = []
# class MessageHandler(WebSocket):

#     def handleMessage(self):
#         self.sendMessage(self.data)

#     def handleConnected(self):
#         connections.append(self)
#         self.sendMessage(u"CARMINE Connected")

#     def handleClose(self):
#         connections.remove(self)


# server = SimpleWebSocketServer('', 8000, MessageHandler, 0.016)

the_url = 'http://localhost'
the_port = 1949
clip_hook = "/cliphook"
time_hook = "/timehook"
newHeaders = {'Content-type': 'application/json', 'Accept': 'text/plain'}
current_beat = 0



class ZLoop():
    __module__ = __name__
    def __init__(self, c_instance):


        self.the_url = 'http://localhost'
        self.the_port = 1949
        self.clip_hook = "/cliphook"
        self.time_hook = "/timehook"
        self.newHeaders = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        self.current_beat = 0

        self.instance = c_instance
        self.slisten = {}
        self.clisten = {}
        self.song = self.instance.song()
        self.app = Live.Application.get_application()
        self.actions = []
        self.current_beat = 0
        self.instance.log_message("adding listeners!")
        if self.song.visible_tracks_has_listener(self.addListeners) != 1:
           self.song.add_visible_tracks_listener(self.addListeners)
        
        self.addListeners()
        self.instance.show_message("ZLOOP-client connected")

        try:
            newHeaders = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            myobj = {'Message': 'Connected Successfully'}
            the_url = 'http://localhost:1949/livecheck'
            x = requests.post(the_url, data=json.dumps(myobj), json=json.dumps(myobj), headers=newHeaders)
            self.instance.show_message("ZLOOP-client connected")
        except:
            self.instance.show_message("ZLOOP: Connection Timed out")

    def refresh_state(self):
        pass

    def add_slotlistener(self, slot, tid, cid):
        cb = lambda :self.slot_changestate(slot, tid, cid)

        if self.slisten.has_key(slot) != 1:
            slot.add_has_clip_listener(cb)
            self.slisten[slot] = cb   
    
    def rem_clip_listeners(self):
        tracks = self.song.visible_tracks
        #new
        for track in tracks:
            if track.name_has_listener(self.track_name_change(track)):
                self.instance.show_message('Something here')
        for slot in self.slisten:
            if slot != None:
                if slot.has_clip_has_listener(self.slisten[slot]) == 1:
                    slot.remove_has_clip_listener(self.slisten[slot])
    
        self.slisten = {}

    def slot_changestate(self, slot, tid, cid):
        
        # Added new clip
        if slot.clip != None:
            self.add_cliplistener(slot.clip, tid, cid)
    

    def loadDevice(self,name):
        self.instance.log_message("Loadig device " + str(name))
        projectFolder = self.app.browser.current_project
        inneritems = [item for item in projectFolder.iter_children]
        for item in inneritems:
            if item.name == "presets":
                presets = [preset for preset in item.iter_children]
                if self.folderSearch(presets, name, 1):
                    return True

        self.instance.log_message("cound not find preset " + name)
        return False

    def folderSearch(self, presets, name, iterCounter):
        if(iterCounter > 5):
            self.instance.log_message("reached max recursion level, exiting..")
            return False
        for preset in presets:
            if(preset.is_folder):
                folder_presets = [p for p in preset.iter_children]
                if self.folderSearch(folder_presets,name, iterCounter+1):
                    return True

            if(preset.name == name + ".adg"):
                self.instance.log_message("found item " + name + "-> attempt to load!")
                self.app.browser.load_item(preset)
                return True

        return False


    def add_cliplistener(self, clip, tid, cid):
        cb = lambda :self.clip_changestate(clip, tid, cid)
        
        if self.clisten.has_key(clip) != 1:
            clip.add_playing_status_listener(cb)
            self.clisten[clip] = cb

    def clip_changestate(self, clip, x, y):
        self.instance.log_message("Listener: x: " + str(x) + " y: " + str(y))

        state = 1
        mz_state = "stopped"
        if clip.is_playing == 1:
            state = 2
            mz_state = "playing"
        if clip.is_triggered == 1:
            state = 3
            mz_state = "triggered"
        self.instance.log_message(str(clip.name) + " > state:" + str(state))
        
        
        #notify of state change
        time_break_up = (str(self.song.get_current_beats_song_time())).split(".")
        myobj = {'track':x,'scene':y,'length':clip.length,'song_state':mz_state,'clip_state':mz_state,'start_time': [int(numeric_string) for numeric_string in time_break_up[:2]]}

        #consider adding try except here.
        x = requests.post(self.the_url + ":" + str(self.the_port) + self.clip_hook, data=json.dumps(myobj), json=json.dumps(myobj), headers=self.newHeaders)




        # if(state == 2 and clip.name != ""):
        #     if(clip.canonical_parent.canonical_parent.devices[0].name != clip.name):
        #         load_success = self.loadDevice(clip.name)
        #         if(load_success != True):
        #             self.actions.append(lambda: self.loading_failed(clip))

    def loading_failed(self, clip):
        clip.color_index = 14

    def time_notify(self):
        new_time = (str(self.song.get_current_beats_song_time())).split(".")
        y = [int(numeric_string) for numeric_string in new_time[:2]]
        if y[1] > 5:
            self.instance.log_message("spilled!")
        if (y[1] > self.current_beat) or ((y[1] == 1) and (self.current_beat!=1)):
            #self.instance.log_message("beat is " + str(y[1]))
            #myobj = {'time':str(new_time)}
            myobj = {'time':str(y)}
            x = requests.post(self.the_url + ":" + str(self.the_port) + self.time_hook, data=json.dumps(myobj), json=json.dumps(myobj), headers=self.newHeaders)
            self.current_beat = y[1]
    #new
    def track_name_change(self, track):
        self.instance.show_message("changed track name " + str(track))


    def setup_song_time_listener(self):
        if self.song.current_song_time_has_listener(self.time_notify):
            self.song.remove_current_song_time_listener(self.time_notify)


    def addListeners(self):
        self.rem_clip_listeners()
        self.setup_song_time_listener()
        tracks = self.song.visible_tracks
        clipSlots = []
        #new
        for track in tracks:
            track.add_name_listener(self.track_name_change)
            clipSlots.append(track.clip_slots)
        tracks = clipSlots
        for track in range(len(tracks)):
            for clip in range(len(tracks[track])):
                c = tracks[track][clip]            
                if c.clip != None:
                    pass
                    self.add_cliplistener(c.clip, track, clip)
                
                self.add_slotlistener(c, track, clip)
    ##############HOOK Transmitters@@@@@@@@@@@@@@@

   
    ######################## ABLETON STUFF @@@@@@@@@@@@
    def update_display(self):

        for action in self.actions:
            action()
            self.actions.remove(action)
        # server.serve()

    def refresh_state(self):
        pass
    def build_midi_map(self, midi_map_handle):
        self.refresh_state()            
            
    def disconnect(self):

        self.instance.log_message("Closing session...")
        #server.close()
        
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
