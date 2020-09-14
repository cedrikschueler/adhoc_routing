from Routing.Parrod import Parrod
from Traffic.TrafficGenerator import TrafficGenerator, TrafficReceiver
import time

TRANSMISSION_RANGE = 230.0

def Experiment(timeLimit: float=120.0, waitTimeBeforeStart=0.0, trafficDelay=0.0):
    routingProtocol = None
    trafficInstance = None

    """
    Parametrize Routing Protocol
    """
    config = dict()
    config["mhChirpInterval"] = 0.5
    config["neighborReliabilityTimeout"] = 2.5
    config["qFctAlpha"] = 0.4
    config["qFctGamma"] = 0.9
    config["maxHops"] = 32
    config["historySize"]  =5
    config["rescheduleRoutesOnTimeout"] = True
    config["predictionMethod"] = "slope"
    config["ifname"] = "wlp2s0"
    config["ipAddress"] = "192.168.178.27"


    config["bcPort"] = 1801
    config["bufferSize"] = 1460

    config["gnssUpdateInterval"] = 1.0

    """
    Parametrize Traffic
    """
    traffic = {
        "CBR": 2.0,
        "MTU": 1460,
        "Sender": "192.168.178.27",
        "Destination": "192.168.178.24",
        "Port": 1901,
        "Filename": "eval.csv"
    }

    if config["ipAddress"] == traffic["Sender"]:
        trafficInstance = TrafficGenerator(traffic["CBR"], traffic["Destination"], MTU_used_byte=traffic["MTU"], port=traffic["Port"])
    elif config["ipAddress"] == traffic["Destination"]:
        trafficInstance = TrafficReceiver(traffic["Sender"], port=traffic["Port"], bufferSize=traffic["MTU"], filename=traffic["Filename"])

    routingProtocol = Parrod(config, TRANSMISSION_RANGE)

    # After everything is set up, wait to start the experiment
    time.sleep(waitTimeBeforeStart)

    # Start routing instance and traffic instance if there is one
    routingProtocol.start()
    if trafficInstance is not None:
        # Wait with traffic instance for given delay
        time.sleep(trafficDelay)
        trafficInstance.start()

    # Let the experiment run before terminating it
    time.sleep(timeLimit)

    # Terminate instances
    if trafficInstance is not None:
        trafficInstance.terminate()
    routingProtocol.terminate()


if __name__ == "__main__":
    Experiment(timeLimit=300, waitTimeBeforeStart=10.0, trafficDelay=5.0)


