from .. import berrymq
import os
import time
import threading

class IntervalTimer(object):
    def __init__(self, id_name, interval):
        self.id_name = id_name
        self.interval = interval
        self.thread = threading.Thread(target=self._notify)
        self.thread.setDaemon(True)
        self.running = True
        self.thread.start()

    def _checkdir(self):
        while self.running:
            time.sleep(self.interval)
            berrymq.twitter("%s:tick" % self.id_name)

    def stop(self):
        self.running = False
