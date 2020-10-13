import time
import subprocess
import ipaddress as ip

def intToIpv4(inp: int) -> str:
    return ip.IPv4Address(inp).__str__()

class RoutingTable:
    Routes = dict()
    def __init__(self, ifname):
        self.ifname = ifname
        self.t0 = time.time()

    def purge(self):
        '''
        Iterate and remove all routes that timed out
        :return:
        '''
        for destination in list(self.Routes.keys()):
            if self.Routes[destination]["ExpiryTime"] < time.time():
                print(f'{(time.time() - self.t0):.3f}: [RT] Delete Route to {intToIpv4(destination)} via {intToIpv4(self.Routes[destination]["Gateway"])} due to Expiration Time')
                self.__del_route(intToIpv4(destination), intToIpv4(self.Routes[destination]["Gateway"]))
                del self.Routes[destination]

    def findBestMatchingRoute(self, origin):
        '''
        Find the best matching route for given origin
        :param origin: IPv4 address (dotted decimal notation)
        :return: Next gateway if available, else None
        '''
        if origin in list(self.Routes.keys()):
            return self.Routes[origin]
        else:
            return None

    def removeRoute(self, e):
        '''
        Add a route to database and remove from Linux' routing table
        :param e: Route parameters (dict)
        :return:
        '''
        if e["Destination"] in self.Routes.keys():
            self.__del_route(intToIpv4(e["Destination"]), intToIpv4(e["Gateway"]))
            del self.Routes[e["Destination"]]
        else:
            raise Exception("Route not available!")

    def addRoute(self, e):
        '''
        Add a route to database and write to Linux' routing table
        :param e: Route parameters (dict)
        :return:
        '''
        dst = e["Destination"]
        if dst in self.Routes.keys():
            # This is meant to only update the expiry time
            self.Routes[dst]["ExpiryTime"] = e["ExpiryTime"] + time.time()
        else:
            e["ExpiryTime"] += time.time()
            self.Routes[e["Destination"]] = e
            self.__add_route(intToIpv4(e["Destination"]), intToIpv4(e["Gateway"]))
            print(f'{(time.time() - self.t0):.3f}: [RT] Add Route to {intToIpv4(e["Destination"])} via {intToIpv4(e["Gateway"])}')

    def __add_route(self, dest, gw):
        '''
        Access to Linux' routing table (root privileges required)
        :param dest: Destination IPv4Address
        :param gw: Gateway IPv4Address
        :return:
        '''
        echo = subprocess.Popen(["ip", "route", "replace", dest, "via", gw, "dev", self.ifname, "onlink"], stdout=subprocess.PIPE)
        return 0

    def __del_route(self, dest, gw):
        '''
        Access to Linux' routing table (root privileges required)
        :param dest: Destination IPv4Address
        :param gw: Gateway IPv4Address
        :return:
        '''
        echo = subprocess.Popen(["ip", "route", "delete", dest, "via", gw, "dev", self.ifname], stdout=subprocess.PIPE)
        return 0

    def invalidateRoutingTable(self, coordinatorAddress: str, node: int=99):
        '''
        Invalides the routing table initially by setting the default gateway to a non-existing node
        :param node: Node ID in subnet that is *not* existing. Default: 99 -> 20.0.0.99
        :return:
        '''
        ip = f'20.0.0.{node}'
        echo = subprocess.Popen(f'ip route replace {coordinatorAddress} via {coordinatorAddress} dev {self.ifname} onlink'.split(' '), stdout=subprocess.PIPE)
        echo = subprocess.Popen(f'ip route replace 20.0.0.0/24 via {ip} dev {self.ifname} onlink'.split(' '), stdout=subprocess.PIPE)
        print(f'{(time.time() - self.t0):.3f}: [RT] Invalidate Routing Table via {ip}')


if __name__ == "__main__":
    rt = RoutingTable("wlp2s0")
    route = {
        "Destination": 3232281187,
        "Gateway": 3232281187,
        "ExpiryTime": time.time() + 500,
        "Metric": 0.42
    }
    print("Before:\n")
    subprocess.call(["route"])
    rt.addRoute(route)
    print("After:\n")
    subprocess.call(["route"])
    time.sleep(5)
    rt.removeRoute(route)
    print("End:\n")
    subprocess.call(["route"])


