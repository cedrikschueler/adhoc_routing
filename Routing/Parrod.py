from Positioning import GNSSReceiver
from Routing import UDPManager
import numpy as np
import time
from collections import OrderedDict
import threading
import sched

class Parrod():

    def __init__(self, config: dict, transmissionRange_m: float):
        self.txRange_m = transmissionRange_m


        self.mhChirpInterval_s = config["mhChirpInterval"]
        self.neighborReliabilityTimeout = config["neighborReliabilityTimeout"]
        self.qFctAlpha = config["qFctAlpha"]
        self.qFctGamma = config["qFctGamma"]
        self.maxHops = config["maxHops"]
        self.historySize = config["historySize"]
        self.rescheduleRoutesOnTimeout = config["rescheduleRoutesOnTimeout"]
        self.destinationToUpdateSchedule = sched.scheduler(time.time, time.sleep)
        self.predictionMethod = config["predictionMethod"]
        self.ipAddress = config["ipAddress"]

        self.bcPort = config["bcPort"]
        self.bufferSize = config["bufferSize"]
        self.udp = UDPManager(self.bcPort, self.bufferSize)
        self.subscribe(self.handleMessageWhenUp)

        self.gnssUpdateInterval = config["gnssUpdateInterval"]
        self.mobility = GNSSReceiver(self.gnssUpdateInterval)

    def start(self):
        self.mobility.start()
        self.udp.start()

    def stop(self):
        self.mobility.terminate()
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

    def qFunction(self, hop: str, target: str) -> float:
        discounts = []
        discounts.append(self.qFctGamma)
        discounts.append(self.Gamma_Pos(hop))
        discounts.append(self.Vi[hop]["Gamma_Mob"])

        return (1 - self.qFctAlpha)*self.Gateways[target][hop]["Q"] + \
               self.qFctAlpha*self.combineDiscounts(discounts)* \
               self.Gateways[target][hop]["V"]

    def getMaxValueFor(self, target: str) -> float:
        res = -1000.0
        if target in self.Gateways.keys():
            for act in self.Gateways.keys():
                if (time.time() - self.Gateways[target][act]["lastSeen"] <= self.neighborReliabilityTimeout) and self.Gamma_Pos(act) > 0:
                    res = np.max(res, self.qFUnction(act, target))
        return res

    def getNextHopFor(self, target: str) -> str:
        a = None
        res = -1000.0

        if target in self.Gateways.keys():
            for act in self.Gateways.keys():
                # todo is the following if statement right here or in Omnet?
                if (time.time() - self.Gateways[target][act]["lastSeen"] <= self.neighborReliabilityTimeout) and self.Gamma_Pos(act) > 0:
                    if self.qFunction(act, target) > res:
                        res = self.qFunction(act, target)
                        a = act
                else:
                    # delete act->second
                    self.Gateways[target].erase(act)
        return a if a != None else "0.0.0.0"

    def Gamma_Pos(self, neighbor: str, origin: str) -> float:
        t_elapsed_since_last_hello: float = time.time() - self.Vi[neighbor]["lastSeen"]

        vj = self.Vi[neighbor]["velo"]
        pj = self.Vi[neighbor]["coord"] + vj*t_elapsed_since_last_hello

        pi = self.mobility.getCurrentPosition()
        vi = self.mobility.getCurrentVelocity()

        deltaP = pj - pi
        deltaV = vj - vi

        px = deltaP[0]
        vx = deltaV[0]
        py = deltaP[1]
        vy = deltaV[1]
        pz = deltaP[2]
        vz = deltaV[2]

        a = vx*+2 + vy**2 + vz**2
        b = 2*(px*vx + py*vy + pz*vz)
        c = px**2 + py**2 + pz**2 - self.txRange_m**2

        t1 = (-b + np.sqrt(b**2 - 4*a*c))/(2*a)
        t2 = (-b - np.sqrt(b**2 - 4*a*c))/(2*a)

        t = 0.0 if (t2 >= 0.0 or (t2 < 0.0 and t1 < 0.0)) else t1

        if origin != "0.0.0.0" and self.rescheduleRoutesOnTimeout and t2 >= 0.0:
            self.destinationToUpdateSchedule.enter(t2, 1, lambda: self.refreshRoutingTable(origin))
        elif origin != "0.0.0.0" and self.rescheduleRoutesOnTimeout and t2 <= 0.0 and t1 > 0.0 and t1 < 1.0:
            self.destinationToUpdateSchedule.enterabs(time.time() + t1, 1, lambda: self.refreshRoutingTable(origin))

        return np.min(1.0, np.sqrt(np.max(t, 0.0)/self.mhChirpInterval_s))

    '''
    Chirp functions
    '''
    def handleMessageWhenUp(self, msg, addr=""):
        ...

    def postliminaryChecksPassed(self, origin: str, gateway: str) -> bool:
        ...

    def updateGamma_Mob(self) -> None:
        exclusive = 0
        merged = 0

        currentSetOfNeighbors = []

        for it in self.Vi.keys():
            if time.time() - self.Vi[it]["lastSeen"] <= self.neighborReliabilityTimeout:
                currentSetOfNeighbors.append(it)

        for o in self.lastSetOfNeighbors.keys():
            if o in currentSetOfNeighbors:
                exclusive += 1
            merged += 1

        for n in currentSetOfNeighbors.keys():
            if n in self.lastSetOfNeighbors:
                exclusive += 1
                merged += 1

        self.lastSetOfNeighbors = currentSetOfNeighbors
        self.m_Gamma_Mob = np.sqrt(1 - float(exclusive)/float(merged)) if merged != 0 else 0.0

    def handleIncomingMultiHopChirp(self):
        ...

    def refreshRoutingTable(self, origin):
        ...

    def purgeNeighbors(self):
        ...

    def sendMultiHopChirp(self):
        ...

    '''
    Flight methods
    Not implemented. Use Mobility Prediction package instead
    '''
