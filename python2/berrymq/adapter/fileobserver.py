from .. import berrymq
import os
import glob
import time
import threading

class FileObserver(object):
    def __init__(self, target_dir, id_name, interval=5):
        self.id_name = id_name
        self.target_dir = target_dir
        self.interval = interval
        self.fileinfo = self._get_fileinfo()
        self.thread = threading.Thread(target=self._checkdir)
        self.thread.setDaemon(True)
        self.running = True
        self.thread.start()
        
    def stop(self):
        self.running = False

    def _checkdir(self):
        while self.running:
            time.sleep(self.interval)
            new_info = self._get_fileinfo()
            old_info = self.fileinfo
            newfiles = set(new_info.keys())
            oldfiles = set(old_info.keys())
            for created_file in (newfiles - oldfiles):
                berrymq.twitter("%s:created" % self.id_name, created_file)
            for remove_file in (oldfiles - newfiles):
                berrymq.twitter("%s:removed" % self.id_name, remove_file)
            for remain_file in (oldfiles & newfiles):
                if new_info[remain_file] != old_info[remain_file]:
                    berrymq.twitter("%s:modified" % self.id_name, remain_file)
            self.fileinfo = new_info

    def _get_fileinfo(self):
        result = {}
        for filename in glob.glob(self.target_dir):
            result[filename] = os.path.getmtime(filename)
        return result

        
