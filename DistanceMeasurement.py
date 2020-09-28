import argparse
import numpy as np
import struct
import time
from Routing.UDPManager import UDPManager
from Positioning.GNSSReceiver import GNSSReceiver

def Station(ref: dict, file: str):
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
            f.write(f'{time.time()},{d}\n')
            f.close()



    udp = UDPManager(1801, "20.0.0.255", 1460)
    udp.subscribe(getReceived)
    udp.listen()


def Mobile(ref: dict, t_sampling: float):
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

    referencePoint = {
        "lon": float(args.longitude),
        "lat": float(args.latitude),
        "alt": float(args.altitude)
    }

    if args.role == "STATION":
        Station(referencePoint, args.file)
    elif args.role == "MOBILE":
        Mobile(referencePoint, args.interval)
    else:
        raise Exception("No valid role specified")