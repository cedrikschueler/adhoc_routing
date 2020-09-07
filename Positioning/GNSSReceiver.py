import threading
import time
from gps import *


class GNSSReceiver(threading.Thread):

    def __init__(self, updateInterval):
        threading.Thread.__init__(self)
        self.session = gps(mode=WATCH_ENABLE)
        self.updateInterval = updateInterval
        self.found_initial_fix = False
        while not self.found_initial_fix:
            tmpData = self.session.next()
            if tmpData["class"] == "TPV":
                self.currentData = tmpData
            if self.session.fix.status == 0:
                print("Waiting for fix!")
            else:
                self.found_initial_fix = True
        print("Found fix. GNSSReceiver is ready to use.")

    def run(self) -> None:
        try:
            while True:
                tmpData = self.session.next()
                if tmpData["class"] == "TPV":
                    self.currentData = tmpData
                time.sleep(self.updateInterval)
        except StopIteration:
            pass

    def get_current_data(self) -> tuple():
        lat = None
        lon = None
        alt = None
        if "lat" in self.currentData.keys():
            lat = self.currentData["lat"]
        if "lon" in self.currentData.keys():
            lon = self.currentData["lon"]
        if "alt" in self.currentData.keys():
            alt = self.currentData["alt"]
        return lat, lon, alt

if __name__ == '__main__':

   gpsp = GNSSReceiver(0.1)
   gpsp.start()
   while 1:
       time.sleep(0.2)
       print(gpsp.get_current_data())