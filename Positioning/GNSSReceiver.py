import multiprocessing
import gpsd
import time


class GNSSReceiver(multiprocessing.Process):

    def __init__(self):
        multiprocessing.Process.__init__(self)
        gpsd.connect()
        self.found_initial_fix = False
        print("Waiting for GNSS fix")
        while not self.found_initial_fix:
            if gpsd.get_current().mode > 2:
                self.found_initial_fix = True
            else:
                time.sleep(1) # Try again every second

    def getCurrentPosition_Sat(self) -> tuple():
        raw = gpsd.get_current()
        return raw.lat, raw.lon, raw.alt

    def getCurrentVelocity(self):
        raw = gpsd.get_current().movement()
        return raw["speed"], raw["track"], raw["climb"]

    def getCurrentPosition(self) -> tuple:
        # todo convert to cartesian, Meanwhile use satelite system:
        return self.getCurrentPosition_Sat()

if __name__ == '__main__':

    gpsp = GNSSReceiver()
    while 1:
        time.sleep(1)
        print(gpsp.getCurrentPosition())
        print(gpsp.getCurrentVelocity())
