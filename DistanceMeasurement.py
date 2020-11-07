import argparse
import numpy as np
import struct
import time
from Routing.UDPManager import UDPManager
from Positioning.GNSSReceiver import geodeticToEcef, ecefToEnu
import gpsd
import datetime
import subprocess
import re
import threading

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

ref_Giesbertpark = {
    "lat": 50.96362,
    "lon": 6.96375,
    "alt": 50.0
}

ARP = {
    "20.0.0.2": "b8:27:eb:88:a9:28",
    "20.0.0.3": "b8:27:eb:33:9e:6a"
}


def Station(ref: dict, file: str, iface: str, mac: str):
    gpsd.connect()
    response = gpsd.get_current()
    t_obj = response.get_time()
    t0 = t_obj.hour * 3600 + t_obj.minute * 60 + t_obj.second
    p0 = np.array(ecefToEnu(*geodeticToEcef(response.lat, response.lon, response.alt), ref["lat"], ref["lon"], ref["alt"]))
    print("Starting over with p0 = ", p0, " at t: ", t0)
    if file != "":
        f = open(file, "a")
        f.write('t,d,rssi_min,rssi_avg,rssi_max,nof_packets\n')
        f.close()
    receptions = []
    def getReceived(data: bytearray, addr):
        recvPos = np.array(struct.unpack("dddd", data))
        t_r = recvPos[0]
        d = np.linalg.norm(recvPos[1:] - p0)
        receptions.append((t_r - t0, d))
        fillRSSI()

    def traceRSSI():
        e = subprocess.Popen(f"iw dev {iface} station get {mac}".split(' '), stdout=subprocess.PIPE)
        out, _ = e.communicate()
        regex = 'signal:\s*(\-[0-9]+)'
        rssi = float(re.split(regex, out.decode('utf-8'))[1])
        return rssi

    RSSIList = []
    def fillRSSI():
        RSSIList.append(traceRSSI())

    udp = UDPManager(1801, "20.0.0.255", 1460)
    udp.subscribe(getReceived)
    udp.listen()

    while True:
        time.sleep(1.0)
        rec_cp = receptions.copy()
        rssis = RSSIList.copy()
        receptions.clear()
        RSSIList.clear()
        if len(rec_cp) == 0:
            continue
        dist_mean = np.mean(np.array(rec_cp), axis=0)
        if file != "":
            f = open(file, "a")
            f.write(f'{rec_cp[0][0]},{dist_mean[1]},{min(rssis)},{np.mean(rssis)},{max(rssis)},{len(rssis)}\n')
            f.close()
            print(f'{rec_cp[0][0]}:\t{dist_mean[1]}\t[{min(rssis)},{np.mean(rssis)},{max(rssis)}]\t- {len(rssis)}\n')


def Mobile(ref: dict, t_sampling: float):
    gpsd.connect()
    udp = UDPManager(1801, "20.0.0.255", 1460)

    while True:
        response = gpsd.get_current()
        print(response.time)
        if response.time == "":
            # Safety measure to prevent Exception
            time.sleep(float(t_sampling))
            continue
        t_obj = response.get_time()
        t = t_obj.hour*3600 + t_obj.minute*60 + t_obj.second
        p = np.array(ecefToEnu(*geodeticToEcef(response.lat, response.lon, response.alt), ref["lat"], ref["lon"], ref["alt"]))
        udp.broadcastData(struct.pack("dddd", t, *p))
        time.sleep(float(t_sampling))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Distance Measurement')
    parser.add_argument('-r', dest='role', type=str, help='Specify a role for this agent.', required=True)
    parser.add_argument('-f', dest='file', type=str, help='File to write the results at station.', default="DistanceMeasurement.csv")
    parser.add_argument('-i', dest='interval', type=float, help='Sampling interval.', default=0.01)
    parser.add_argument('-lat', dest='latitude', type=float, help='Latitude', default=51.49150)
    parser.add_argument('-lon', dest='longitude', type=float, help='Longitude', default=7.41340)
    parser.add_argument('-alt', dest='altitude', type=float, help='Altitude', default=60.0)

    args = parser.parse_args()

    referencePoint = ref_Giesbertpark
    if args.role == "STATION":
        Station(referencePoint, args.file, 'wlan0', ARP["20.0.0.2"])
    elif args.role == "MOBILE":
        Mobile(referencePoint, args.interval)
    else:
        raise Exception("No valid role specified")