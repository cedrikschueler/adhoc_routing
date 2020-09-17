from Positioning.GNSSReceiver import GNSSReceiver
from Routing.UDPManager import UDPManager
from Routing.RoutingTable import RoutingTable
from Messages.MultiHopChirp import MultiHopChirp
from Prediction.Predictors import SlopePredictor, NaivePredictor, BATMobilePredictor, InterpolatedBatman
from Positioning.WaypointProvider import WaypointProvider
import numpy as np
import time
import sched
import ipaddress as ip

WP_REACHED_M = 25.0
V_MAX_KMH = 50.0
PREDICTOR_STEPSIZE = 0.1

class Parrod():

    __squNr: int = 0
    Vi: dict = dict()
    Gateways: dict = dict()
    lastSetOfNeighbors:list = []
    m_Gamma_Mob: float = 0.0
    histCoord: list = []

    def __init__(self, config: dict, transmissionRange_m: float):
        self.txRange_m = transmissionRange_m

        self.mhChirp = MultiHopChirp()
        self.mhChirpInterval_s = config["mhChirpInterval"]
        self.neighborReliabilityTimeout = config["neighborReliabilityTimeout"]
        self.mhChirpReminder = sched.scheduler(time.time, time.sleep)


        self.qFctAlpha = config["qFctAlpha"]
        self.qFctGamma = config["qFctGamma"]
        self.maxHops = config["maxHops"]
        self.historySize = config["historySize"]
        self.rescheduleRoutesOnTimeout = config["rescheduleRoutesOnTimeout"]
        self.destinationToUpdateSchedule = sched.scheduler(time.time, time.sleep)
        self.predictionMethod = config["predictionMethod"]
        self.waypointProvider = config["waypointProvider"]
        self.ipAddress = int(ip.IPv4Address(config["ipAddress"]))

        self.rt = RoutingTable(config["ifname"])

        self.bcPort = config["bcPort"]
        self.bufferSize = config["bufferSize"]
        self.udp = UDPManager(self.bcPort, options["broadcastAddress"], self.bufferSize)
        self.udp.subscribe(self.handleMessageWhenUp)

        self.gnssUpdateInterval = config["gnssUpdateInterval"]
        self.mobility = GNSSReceiver(config["gpsReferencePoint"], config["experimentName"])

    def start(self):
        print("Starting services")
        self.udp.listen()
        self.mhChirpReminder.enter(self.mhChirpInterval_s, 1, lambda: self.sendMultiHopChirp())
        self.mhChirpReminder.run()

    def terminate(self):
        self.udp.terminate()
    '''
    Brain functions
    '''
    def combineDiscounts(self, gamma: [float]) -> float:
        mode = "multiply"
        if mode == "multiply":
            return np.prod(gamma)
        elif mode == "geometric":
            return np.prod(gamma)**(1.0/len(gamma))
        elif mode == "harmonic":
            assert(all(g > 0.0 for g in gamma))
            return len(gamma)/np.sum([1.0/g for g in gamma])
        elif mode == "arithmetic":
            return np.mean(gamma)
        else:
            raise Exception("No valid combination mode!")

    def qFunction(self, hop: int, target: int) -> float:
        discounts = []
        discounts.append(self.qFctGamma)
        discounts.append(min(1.0, np.sqrt(max(self.Gamma_Pos(hop), 0.0) / self.mhChirpInterval_s)))
        discounts.append(self.Vi[hop]["Gamma_Mob"])

        return (1 - self.qFctAlpha)*self.Gateways[target][hop]["Q"] + \
               self.qFctAlpha*self.combineDiscounts(discounts)* \
               self.Gateways[target][hop]["V"]

    def getMaxValueFor(self, target: int) -> float:
        res = -1000.0
        if target in self.Gateways.keys():
            for act in self.Gateways[target].keys():
                deltaT = time.time() - self.Gateways[target][act]["lastSeen"]
                if (deltaT <= min(self.neighborReliabilityTimeout, self.Gamma_Pos(act))):
                    res = max(res, self.qFunction(act, target))
        return res

    def getNextHopFor(self, target: int) -> int:
        a = None
        res = -1000.0

        if target in list(self.Gateways.keys()):
            for act in list(self.Gateways[target].keys()):
                deltaT = time.time() - self.Gateways[target][act]["lastSeen"]
                if (deltaT <= min(self.neighborReliabilityTimeout, self.Gamma_Pos(act))):
                    if self.qFunction(act, target) > res:
                        res = self.qFunction(act, target)
                        a = act
                else:
                    # delete act->second
                    del self.Gateways[target][act]
        return a if a != None else 0

    def Gamma_Pos(self, neighbor: int, origin: int = 0) -> float:
        t_elapsed_since_last_hello: float = time.time() - self.Vi[neighbor]["lastSeen"]

        vj = self.Vi[neighbor]["velo"]
        pj = self.Vi[neighbor]["coord"] + vj*t_elapsed_since_last_hello

        pi = self.mobility.getCurrentPosition()
        vi = (self.forecastPosition() - pi)/(self.neighborReliabilityTimeout if self.neighborReliabilityTimeout != 0 else 1.0)

        deltaP = pj - pi
        deltaV = vj - vi

        px = deltaP[0]
        vx = deltaV[0]
        py = deltaP[1]
        vy = deltaV[1]
        pz = deltaP[2]
        vz = deltaV[2]

        a = vx**2 + vy**2 + vz**2
        b = 2*(px*vx + py*vy + pz*vz)
        c = px**2 + py**2 + pz**2 - self.txRange_m**2

        t: float = 0.0
        if a == 0:
            t = 1.0 if c <= 0.0 else 0.0
        else:
            t1 = (-b + np.sqrt(b**2 - 4*a*c))/(2*a)
            t2 = (-b - np.sqrt(b**2 - 4*a*c))/(2*a)
            t = 0.0 if (t2 >= 0.0 or (t2 < 0.0 and t1 < 0.0)) else t1

        if origin != 0 and self.rescheduleRoutesOnTimeout and t2 >= 0.0:
            self.destinationToUpdateSchedule.enter(t2, 1, lambda: self.refreshRoutingTable(origin))
        elif origin != 0 and self.rescheduleRoutesOnTimeout and t2 <= 0.0 and t1 > 0.0 and t1 < 1.0:
            self.destinationToUpdateSchedule.enter(t1, 1, lambda: self.refreshRoutingTable(origin))
        self.destinationToUpdateSchedule.run()

        return t

    '''
    Chirp functions
    '''
    def handleMessageWhenUp(self, msg):
        if (len(msg) == self.mhChirp.length()):
            msgData = self.mhChirp.deserialize(msg)
            remainingHops = self.handleIncomingMultiHopChirp(msgData)
            if remainingHops > 0 and self.postliminaryChecksPassed(msgData["Origin"], msgData["Hop"]):
                msgData["Value"] = self.getMaxValueFor(msgData["Origin"])
                msgData["CreationTime"] = time.time()
                msgData["Hop"] = self.ipAddress

                # Get location
                forecast = self.forecastPosition()
                p = self.mobility.getCurrentPosition()
                v = (forecast - p)/(self.neighborReliabilityTimeout if self.neighborReliabilityTimeout != 0 else 1.0)

                msgData["X"] = p[0]
                msgData["Y"] = p[1]
                msgData["Z"] = p[2]
                msgData["Vx"] = v[0]
                msgData["Vy"] = v[1]
                msgData["Vz"] = v[2]

                msgData["GammaMob"] = self.m_Gamma_Mob
                msgData["HopCount"] = remainingHops

                self.udp.broadcastData(self.mhChirp.serialize(msgData))


    def postliminaryChecksPassed(self, origin: int, gateway: int) -> bool:
        if len(self.Vi) == 0:
            return False
        elif len(self.Vi) == 1:
            return not (self.Vi[list(self.Vi.keys())[0]] == origin or self.Vi[list(self.Vi.keys())[0]] == gateway)
        elif self.rt.findBestMatchingRoute(origin) != None and self.rt.findBestMatchingRoute(origin)["Gateway"] != gateway:
            return False
        else:
            return True

    def updateGamma_Mob(self) -> None:
        exclusive = 0
        merged = 0

        currentSetOfNeighbors = []

        for it in list(self.Vi.keys()):
            if time.time() - self.Vi[it]["lastSeen"] <= self.neighborReliabilityTimeout:
                currentSetOfNeighbors.append(it)

        for o in self.lastSetOfNeighbors:
            if o in currentSetOfNeighbors:
                exclusive += 1
            merged += 1

        for n in currentSetOfNeighbors:
            if n in self.lastSetOfNeighbors:
                exclusive += 1
                merged += 1

        self.lastSetOfNeighbors = currentSetOfNeighbors
        self.m_Gamma_Mob = np.sqrt(1 - float(exclusive)/float(merged)) if merged != 0 else 0.0

    def handleIncomingMultiHopChirp(self, chirp: dict) -> int:
        origin = chirp["Origin"]
        gateway = chirp["Hop"]

        if gateway == self.ipAddress:
            # Return 0 if this message is an own message (This case is handled by OMNeT++ in the simulation)
            return 0

        val = chirp["Value"]

        x = chirp["X"]
        y = chirp["Y"]
        z = chirp["Z"]
        vx = chirp["Vx"]
        vy = chirp["Vy"]
        vz = chirp["Vz"]

        gamma_mob = chirp["GammaMob"]
        squNr = chirp["SquNr"]

        hopCount = chirp["HopCount"]

        knownNeighbor = gateway in self.Vi.keys()
        if knownNeighbor and origin != self.ipAddress and self.Vi[gateway]["squNr"] <= squNr:
            self.Vi[gateway]["lastSeen"] = time.time()
            self.Vi[gateway]["coord"] = np.array([x, y, z])
            self.Vi[gateway]["velo"] = np.array([vx, vy, vz])
            self.Vi[gateway]["futurePosition"] = np.array([x, y, z])
            self.Vi[gateway]["Gamma_Mob"] = gamma_mob
            self.Vi[gateway]["Gamma_Pos"] = self.Gamma_Pos(gateway, 0)
            self.Vi[gateway]["squNr"] = squNr
        else:
            self.Vi[gateway] = dict()
            self.Vi[gateway]["lastSeen"] = time.time()
            self.Vi[gateway]["coord"] = np.array([x, y, z])
            self.Vi[gateway]["velo"] = np.array([vx, vy, vz])
            self.Vi[gateway]["futurePosition"] = np.array([x, y, z])
            self.Vi[gateway]["Gamma_Mob"] = gamma_mob
            self.Vi[gateway]["squNr"] = squNr
            #if (origin == gateway) {
            #   nj->second->regRec();
            #}
            self.Vi[gateway]["Gamma_Pos"] = self.Gamma_Pos(gateway, 0)

        if origin == self.ipAddress:
            #if (maxHops - hopCount == 1) {
            #// Only count direct echo
            #Vi.at(gateway)->regEcho(squNr);
            #}
            return 0
        elif knownNeighbor and self.Vi[gateway]["squNr"] > squNr:
            return 0

        if origin not in self.Gateways.keys():
            self.Gateways[origin] = dict()
            self.Gateways[origin][gateway] = dict()
            self.Gateways[origin][gateway]["lastSeen"] = time.time()
            self.Gateways[origin][gateway]["Q"] = 0.0
            self.Gateways[origin][gateway]["squNr"] = squNr
            self.Gateways[origin][gateway]["V"] = val
            self.Gateways[origin][gateway]["Q"] = self.qFunction(gateway, origin)
        else:
            if gateway not in self.Gateways[origin].keys():
                self.Gateways[origin][gateway] = dict()
                self.Gateways[origin][gateway]["lastSeen"] = time.time()
                self.Gateways[origin][gateway]["Q"] = 0.0
                self.Gateways[origin][gateway]["squNr"] = squNr
                self.Gateways[origin][gateway]["V"] = val
                self.Gateways[origin][gateway]["Q"] = self.qFunction(gateway, origin)
            else:
                if squNr > self.Gateways[origin][gateway]["squNr"] or (squNr == self.Gateways[origin][gateway]["squNr"] and val > self.Gateways[origin][gateway]["V"]):
                    self.Gateways[origin][gateway]["lastSeen"] = time.time()
                    self.Gateways[origin][gateway]["squNr"] = squNr
                    self.Gateways[origin][gateway]["V"] = val
                    self.Gateways[origin][gateway]["Q"] = self.qFunction(gateway, origin)
                else:
                    return 0

        self.refreshRoutingTable(origin)
        return hopCount - 1

    def refreshRoutingTable(self, origin: int) -> None:
        self.rt.purge()
        self.purgeNeighbors()

        route = self.rt.findBestMatchingRoute(origin)
        bestHop = self.getNextHopFor(origin)

        if route == None and bestHop == 0:
            return
        else:
            if route is not None and route["Gateway"] == bestHop:
                return
            if route is not None:
                self.rt.removeRoute(route)
            if bestHop == 0:
                return
            else:
                e = dict()
                e["Destination"] = origin
                e["Gateway"] = bestHop
                e["ExpiryTime"] = time.time() + min(self.neighborReliabilityTimeout, self.Vi[bestHop]["Gamma_Pos"])
                e["Metric"] = self.Gateways[origin][bestHop]["Q"]

                self.rt.addRoute(e)

    def purgeNeighbors(self):
        for target in list(self.Gateways.keys()):
            for act in list(self.Gateways[target]):
                deltaT = time.time() - self.Gateways[target][act]["lastSeen"]
                if deltaT > min(self.neighborReliabilityTimeout, self.Gamma_Pos(act)):
                    del self.Gateways[target][act]

        for n in list(self.Vi.keys()):
            useful: bool = False
            for t in list(self.Gateways.keys()):
                useful = useful or n in self.Gateways[t].keys()
            if not useful:
                del self.Vi[n]

    def sendMultiHopChirp(self):
        chirp = dict()
        chirp["Origin"] = self.ipAddress
        chirp["CreationTime"] = time.time()
        chirp["Hop"] = self.ipAddress
        chirp["SquNr"] = self.getNextSquNr()

        # Get location
        forecast = self.forecastPosition()
        p = self.mobility.getCurrentPosition()
        v = (forecast - p) / (self.neighborReliabilityTimeout if self.neighborReliabilityTimeout != 0 else 1.0)

        self.trackPosition(np.array([time.time(), p[0], p[1], p[2]]))

        chirp["X"] = p[0]
        chirp["Y"] = p[1]
        chirp["Z"] = p[2]
        chirp["Vx"] = v[0]
        chirp["Vy"] = v[1]
        chirp["Vz"] = v[2]

        self.updateGamma_Mob()
        chirp["GammaMob"] = self.m_Gamma_Mob
        chirp["Value"] = 1.0
        chirp["HopCount"] = self.maxHops

        self.udp.broadcastData(self.mhChirp.serialize(chirp))
        self.mhChirpReminder.enter(self.mhChirpInterval_s, 1, lambda: self.sendMultiHopChirp())

    def getNextSquNr(self) -> int:
        if not self.__squNr < 2**16 - 1:
            self.__squNr = 0
        self.__squNr += 1
        return self.__squNr

    '''
    Flight methods
    '''
    def trackPosition(self, p: tuple):
        self.histCoord.append(np.array(p))
        if len(self.histCoord) > self.historySize:
            self.histCoord.pop(0)

    def forecastPosition(self):
        if len(self.histCoord) == 0:
            return self.mobility.getCurrentPosition()
        else:
            if self.predictionMethod == "slope":
                pred = SlopePredictor(int(self.neighborReliabilityTimeout/self.mhChirpInterval_s), self.gnssUpdateInterval)
            elif self.predictionMethod == "naive":
                pred = NaivePredictor(int(self.neighborReliabilityTimeout/self.mhChirpInterval_s))
            elif self.predictionMethod == "batman":
                pred = BATMobilePredictor(int(self.neighborReliabilityTimeout/self.mhChirpInterval_s), self.gnssUpdateInterval, WP_REACHED_M, V_MAX_KMH) # todo: what if gnssUpdateInterval and mhChirp differ?
            elif self.predictionMethod == "intbat":
                pred = InterpolatedBatman(int(self.neighborReliabilityTimeout/self.mhChirpInterval_s), self.gnssUpdateInterval, WP_REACHED_M, V_MAX_KMH, PREDICTOR_STEPSIZE)
            else:
                valid = ["batman", "intbat", "naive", "slope"]
                raise Exception(f"No valid prediction method chosen!\nSelect from: {valid}")

            if self.waypointProvider is not "":
                wpp = WaypointProvider()
                wp = wpp.getWP()
            else:
                wp = []

            pred.fit(self.histCoord, plannedWaypoints=wp)
            return np.array(pred.predict())
