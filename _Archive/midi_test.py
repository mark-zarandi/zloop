import isobar as iso
import logging
import time

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")

midi_in = iso.MidiInputDevice(device_name="zarandi Bus 1")
timeline = iso.Timeline(clock_source=midi_in)
notes = []
durations = []
last_note_time = None

print("Listening for notes on %s. Press Ctrl-C to stop." % midi_in.device_name)

def print_time():
    print(1)

timeline.schedule({"duration":1,"action": print_time})
timeline.run()
