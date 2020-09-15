import gpsd
import time
import numpy as np


class GNSSReceiver():

    def __init__(self):
        gpsd.connect()
        self.found_initial_fix = False
        print("Waiting for GNSS fix")
        while not self.found_initial_fix:
            if gpsd.get_current().mode > 2:
                self.found_initial_fix = True
            else:
                time.sleep(1) # Try again every second

    def getCurrentPosition_Sat(self) -> tuple():
        '''
        Get current Position in Satellite coordinates (WGS84)
        :return:
        '''
        raw = gpsd.get_current()
        return raw.lat, raw.lon, raw.alt

    def getCurrentPosition(self) -> tuple:
        '''
        Get current position in Cartesian coordinates
        :return: (x, y, z)
        '''
        return np.array(self.WGS84toXYZ(*self.getCurrentPosition_Sat()))


    def WGS84toXYZ(self, lon: float, lat: float, alt: float) -> tuple:
        '''
        Converts WGS84 coordinates to Cartesian coordinates
        Credits: https://stackoverflow.com/questions/41159336/how-to-convert-a-spherical-velocity-coordinates-into-cartesian/41161714#41161714


        :param lon: Longitude
        :param lat: Latitude
        :param alt: Altitude
        :return: (x, y, z)
        '''
        _earth_a=6378137.00000   # [m] WGS84 equator radius
        _earth_b=6356752.31414   # [m] WGS84 epolar radius
        _earth_e=8.1819190842622e-2 #  WGS84 eccentricity

        a = lon
        b = lat
        h = alt
        c = np.cos(b)
        s = np.sin(b)

        l = _earth_a/np.sqrt(1.0-(_earth_e**2 * s**2))
        x = (l+h)*c*np.cos(a)
        y = (l+h)*c*np.sin(a)
        z = (((1.0-_earth_e**2)*l)+h)*s

        return x, y, z

if __name__ == '__main__':

    gpsp = GNSSReceiver()
    while 1:
        time.sleep(1)
        print(gpsp.getCurrentPosition())
