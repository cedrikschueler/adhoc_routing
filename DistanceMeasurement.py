import argparse
import numpy as np
import struct
import time
from Routing.UDPManager import UDPManager
from Positioning.GNSSReceiver import GNSSReceiver

def Mobile(ref: dict, file: str):
    t0 = time.time()
    if file != "":
        f = open(file, "a")
        f.write('t,d\n')
        f.close()
    gnss = GNSSReceiver(ref)
    def getReceived(data: bytearray):
        recvPos = np.array(struct.unpack("ddd", data))
        pos = gnss.getCurrentPosition()
        d = np.linalg.norm(recvPos - pos)
        if file != "":
            f = open(file, "a")
            f.write(f'{time.time() -t0},{d}\n')
            f.close()



    udp = UDPManager(1801, "20.0.0.255", 1460)
    udp.subscribe(getReceived)
    udp.listen()


def Station(ref: dict, t_sampling: float):
    gnss = GNSSReceiver(ref)
    udp = UDPManager(1801, "20.0.0.255", 1460)

    while True:
        pos = gnss.getCurrentPosition()
        udp.broadcastData(struct.pack("ddd", *pos))
        time.sleep(t_sampling)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Distance Measurement')
    parser.add_argument('-r', dest='role', type=str, help='Specify a role for this agent.', required=True)
    parser.add_argument('-f', dest='file', type=str, help='File to write the results at station.', default="DistanceMeasurement.csv")
    parser.add_argument('-i', dest='interval', type=float, help='Sampling interval.', default=1.0)
    parser.add_argument('-lat', dest='latitude', type=float, help='Latitude', default=51.49150)
    parser.add_argument('-lon', dest='longitude', type=float, help='Longitude', default=7.41340)
    parser.add_argument('-alt', dest='altitude', type=float, help='Altitude', default=60.0)

    args = parser.parse_args()

    ref_OHParkpplatz = {
        "lat": 51.49051416,
        "lon": 7.41436899,
        "alt": 106.6
    }

    ref_KoelnerDom = {
        "lat": 51.49150,
        "lon": 7.41340,
        "alt": 60.0
    }

    ref_Sportplatz = {
        "lat": 51.31901,
        "lon": 7.99801,
        "alt": 280.0
    }

    referencePoint = ref_OHParkpplatz
    if args.role == "STATION":
        Station(referencePoint, args.interval)
    elif args.role == "MOBILE":
        Mobile(referencePoint, args.file)
    else:
        raise Exception("No valid role specified")