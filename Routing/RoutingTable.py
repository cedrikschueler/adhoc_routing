import time
import socket
import struct
import fcntl
import pyroute2 as pr2
import subprocess

# find const values
# grep IFF_UP -rl /usr/include/
IFF_UP = 0x1
IFF_RUNNING = 0x40
IFNAMSIZ = 16
SIOCSIFADDR = 0x8916
SIOCSIFNETMASK = 0x891c
SIOCGIFFLAGS = 0x8913
SIOCSIFFLAGS = 0x8914
SIOCADDRT = 0x890B
SIOCDELRT = 0x890C

RTF_UP = 0x0001
RTF_GATEWAY = 0x0002
RTF_HOST = 0x0004

AF_INET = socket.AF_INET

class RoutingTable:
#https://www.programcreek.com/python/?code=alexsunday%2Fpyvpn%2Fpyvpn-master%2Fsrc%2Futil.py

    Routes = dict()
    def __init__(self):
        self.ifname = "wlp2s0"

    def purge(self):
        for destination in self.Routes:
            for gateway in self.Routes[destination]:
                if self.Routes[destination][gateway]["ExpiryTime"] < time.time():
                    self.__del_route(destination, gateway)
                    del self.Routes[destination][gateway]


    def findBestMatchingRoute(self, origin):
        if origin in self.Routes.keys():
            return self.Routes[origin]
        else:
            return None


    def removeRoute(self, e):
        if e["Destination"] in self.Routes.keys():
            self.__del_route(e["Destination"], e["Gateway"])
            del self.Routes[e["Destination"]][e["Gateway"]]
        else:
            raise Exception("Route not available!")

    def addRoute(self, e):
        dst = e["Destination"]
        if dst in self.Routes.keys():
            raise Exception("Destination is already registered!")
        else:
            self.Routes[e["Destination"]] = e
            self.__add_route(e["Destination"], e["Gateway"])

    def __add_route(self, dest, gw):
        # sudo strace route add -net 192.168.0.0/24 gw 192.168.10.1
        # ioctl(3, SIOCADDRT, ifr)
        # /usr/include/net/route.h
        echo = subprocess.Popen(["ip", "route", "replace", dest, "via", gw, "dev", "wlp2s0"], stdout=subprocess.PIPE)
        return 0
        pad = ('\x00' * 8).encode("utf-8")
        inet_aton = socket.inet_aton
        sockaddr_in_fmt = 'hH4s8s'
        rtentry_fmt = 'L16s16s16sH38s'
        dst = struct.pack(sockaddr_in_fmt, AF_INET, 0, inet_aton(dest), pad)
        next_gw = struct.pack(sockaddr_in_fmt, AF_INET, 0, inet_aton(gw), pad)
        netmask = struct.pack(sockaddr_in_fmt, AF_INET, 0, inet_aton(mask), pad)
        rt_flags = RTF_UP | RTF_GATEWAY
        rtentry = struct.pack(rtentry_fmt,
                              0, dst, next_gw, netmask, rt_flags, ('\x00' * 38).encode("utf-8"))
        sock = socket.socket(AF_INET, socket.SOCK_DGRAM, 0)
        fcntl.fcntl(sock.fileno(), SIOCADDRT, rtentry)
        return 0

    def __del_route(self, dest, gw):
        echo = subprocess.Popen(["ip", "route", "delete", dest, "via", gw, "dev", "wlp2s0"], stdout=subprocess.PIPE)
        return 0
        # sudo strace route add -net 192.168.0.0/24 gw 192.168.10.1
        # ioctl(3, SIOCADDRT, ifr)
        # /usr/include/net/route.h
        pad = ('\x00' * 8).encode("utf-8")
        inet_aton = socket.inet_aton
        sockaddr_in_fmt = 'hH4s8s'
        rtentry_fmt = 'L16s16s16sH38s'
        dst = struct.pack(sockaddr_in_fmt, AF_INET, 0, inet_aton(dest), pad)
        next_gw = struct.pack(sockaddr_in_fmt, AF_INET, 0, inet_aton(gw), pad)
        netmask = struct.pack(sockaddr_in_fmt, AF_INET, 0, inet_aton(mask), pad)
        rt_flags = RTF_UP if int(mask) == 0 else RTF_UP | RTF_HOST
        rtentry = struct.pack(rtentry_fmt,
                              0, dst, next_gw, netmask, rt_flags, ('\x00' * 38).encode("utf-8"))
        sock = socket.socket(AF_INET, socket.SOCK_DGRAM, 0)
        fcntl.fcntl(sock.fileno(), SIOCDELRT, rtentry)
        return 0


if __name__ == "__main__":
    pass

