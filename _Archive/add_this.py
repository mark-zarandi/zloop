    def time_notify(self):
        self.instance.show_message(str(self.song.get_current_beats_song_time()))


    def setup_song_time_listener(self):
        if self.song.current_song_time_has_listener(self.time_notify):
            self.song.remove_current_song_time_listener(self.time_notify)
        self.song.add_current_song_time_listener(self.time_notify)