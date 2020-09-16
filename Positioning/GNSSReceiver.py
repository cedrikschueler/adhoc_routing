import gpsd
import time
import numpy as np

A = 6378137.0 # WGS-84 Earth semimajor axis (m)
B = 6356752.314245 # Derived Earth semiminor axis (m)
F = (A - B)/A # Ellipsoid Flatness
F_INV = 1.0/F # Inverse Flattening

A_SQ = A**2
B_SQ = B**2
E_SQ = F * (2 - F) # Square of Eccentricity

class GNSSReceiver():

    def __init__(self, gpsReferencePoint: dict):
        self.gpsReferencePoint = (gpsReferencePoint["lat"], gpsReferencePoint["lon"], gpsReferencePoint["alt"])
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
        return np.array(ecefToEnu(*geodeticToEcef(*self.getCurrentPosition_Sat()), *self.gpsReferencePoint))


# Conversion from GPS (WGS84) to Local Tangent Plane
# Credits: https://gist.github.com/govert/1b373696c9a27ff4c72a

def degreesToRadians(ang: float) -> float:
    return np.pi/180.0 * ang

def radiansToDegrees(ang: float) -> float:
    return 180.0/ np.pi * ang

def geodeticToEcef(lat: float, lon: float, h: float) -> np.array:
    _lambda = degreesToRadians(lat)
    _phi = degreesToRadians(lon)
    s = np.sin(_lambda)
    N = A / np.sqrt(1 - E_SQ * s ** 2)

    sin_lambda = np.sin(_lambda)
    cos_lambda = np.cos(_lambda)
    cos_phi = np.cos(_phi)
    sin_phi = np.sin(_phi)

    x = (h + N) * cos_lambda * cos_phi
    y = (h + N) * cos_lambda * sin_phi
    z = (h + (1 - E_SQ) * N) * sin_lambda

    return np.array([x, y, z])

def ecefToEnu(x: float, y: float, z: float, lat0: float, lon0: float, h0: float):
    _lambda = degreesToRadians(lat0)
    _phi = degreesToRadians(lon0)
    s = np.sin(_lambda)
    N = A / np.sqrt(1 - E_SQ * s ** 2)

    sin_lambda = np.sin(_lambda)
    cos_lambda = np.cos(_lambda)
    cos_phi = np.cos(_phi)
    sin_phi = np.sin(_phi)

    x0 = (h0 + N) * cos_lambda * cos_phi
    y0 = (h0 + N) * cos_lambda * sin_phi
    z0 = (h0 + (1 - E_SQ) * N) * sin_lambda

    xd = x - x0
    yd = y - y0
    zd = z - z0

    # This is the matrix multiplication
    xEast = -sin_phi * xd + cos_phi * yd
    yNorth = -cos_phi * sin_lambda * xd - sin_lambda * sin_phi * yd + cos_lambda * zd
    zUp = cos_lambda * cos_phi * xd + cos_lambda * sin_phi * yd + sin_lambda * zd

    return np.array([xEast, yNorth, zUp])



if __name__ == '__main__':
    gpsReferencePoint = {
        "lat": 50.941220,
        "lon": 6.957029,
        "alt": 40.0
    }
    gpsp = GNSSReceiver(gpsReferencePoint)
    while 1:
        time.sleep(1)
        print(gpsp.getCurrentPosition())
