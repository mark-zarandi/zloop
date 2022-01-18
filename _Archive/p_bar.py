try:
    import Tkinter as tk
    import tkFont
    import ttk
except ImportError:  # Python 3
    import tkinter as tk
    import tkinter.font as tkFont
    import tkinter.ttk as ttk

from http.server import BaseHTTPRequestHandler, HTTPServer
import queue
import threading
import json
# --- classes ---

class HttpHandler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        f = open("index.html", "r")
        self.wfile.write(f.read())

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        self._set_headers()
        print "in post method"
        self.data_string = self.rfile.read(int(self.headers['Content-Length']))

        self.send_response(200)
        self.end_headers()

        data = simplejson.loads(self.data_string)

        print "{}".format(data)
        return


class CircularProgressbar(object):
    def __init__(self, canvas, x0, y0, x1, y1, width=2, start_ang=0, full_extent=360):
        self.custom_font = tkFont.Font(family="Helvetica", size=12, weight='bold')
        self.canvas = canvas
        self.x0, self.y0, self.x1, self.y1 = x0+width, y0+width, x1-width, y1-width
        self.tx, self.ty = (x1-x0) / 2, (y1-y0) / 2
        self.width = width
        self.start_ang, self.full_extent = start_ang, full_extent
        # draw static bar outline
        w2 = width / 2
        self.oval_id1 = self.canvas.create_oval(self.x0-w2, self.y0-w2,
                                                self.x1+w2, self.y1+w2)
        self.oval_id2 = self.canvas.create_oval(self.x0+w2, self.y0+w2,
                                                self.x1-w2, self.y1-w2)
        self.running = False

    def start(self, interval=100):
        self.interval = interval
        self.increment = self.full_extent / interval
        self.extent = 0
        self.arc_id = self.canvas.create_arc(self.x0, self.y0, self.x1, self.y1,
                                             start=self.start_ang, extent=self.extent,
                                             width=self.width, style='arc')
        percent = '0%'
        self.label_id = self.canvas.create_text(self.tx, self.ty, text=percent,
                                                font=self.custom_font)
        self.running = True
        self.canvas.after(interval, self.step, self.increment)

    def step(self, delta):
        """Increment extent and update arc and label displaying how much completed."""
        if self.running:
            self.extent = (self.extent + delta) % 360
            self.cur_extent = (self.extent + delta) % 360
            self.canvas.itemconfigure(self.arc_id, extent=self.cur_extent)
            percent = '{:.0f}%'.format(round(float(self.cur_extent) / self.full_extent * 100))
            self.canvas.itemconfigure(self.label_id, text=percent)

        self.after_id = self.canvas.after(self.interval, self.step, delta)

    def toggle_pause(self):
        self.running = not self.running

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()


    def check_queue():
        if not q.empty():
            text.insert('end', q.get()+'\n') # get from `queue` and put in `Text`
        window.after(100, check_queue)  # check again after 100ms
    

    def createWidgets(self):
        self.canvas = tk.Canvas(self, width=200, height=200, bg='white')
        self.canvas.grid(row=0, column=0, columnspan=2)

        self.progressbar = CircularProgressbar(self.canvas, 0, 0, 200, 200, 20)

        self.pauseButton = tk.Button(self, text='Pause', command=self.pause)
        self.pauseButton.grid(row=1, column=0)
        self.quitButton = tk.Button(self, text='Quit', command=self.quit)
        self.quitButton.grid(row=1, column=1)

    def start(self):
        q = queue.Queue()

        webServer = HTTPServer(('localhost', 9080), HttpHandler)
        print('running http server: http://localhost:9080')  # some consoles will display URL as clickable so it is easier to run browser
        t = threading.Thread(target=webServer.serve_forever)
        t.daemon = True
        self.progressbar.start()
        self.mainloop()

    def pause(self):
        self.progressbar.toggle_pause()

if __name__ == '__main__':
    app = Application()
    app.master.title('Sample application')
    app.start()