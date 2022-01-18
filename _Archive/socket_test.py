import urllib
import json


class MZ_request:

    def __init__(self, the_url, the_port):
        self.destination = the_url #needs to be a string
        self.send_port = the_port

    def send_this(self):
        r = requests.post('http://localhost:1949/cliphook', json={"key": "value"})