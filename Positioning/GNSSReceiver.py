import multiprocessing
import gpsd
import time


class GNSSReceiver(multiprocessing.Process):

    def __init__(self):
        multiprocessing.Process.__init__(self)
        gpsd.connect()
        self.currentData = gpsd.get_current().lat, gpsd.get_current().lon, gpsd.get_current().alt

    def getCurrentPosition_Sat(self) -> tuple():
        raw = gpsd.get_current()
        return raw.lat, raw.lon, raw.alt

    def getCurrentPosition(self) -> tuple:
        # todo convert to cartesian, Meanwhile use satelite system:
        return self.getCurrentPosition_Sat()

if __name__ == '__main__':

    gpsp = GNSSReceiver()
    while 1:
        time.sleep(0.5)
        print(gpsp.getCurrentPosition_Sat())