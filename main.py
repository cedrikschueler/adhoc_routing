from Routing.Parrod import Parrod
from Traffic.TrafficGenerator import TrafficGenerator, TrafficReceiver
import time
import subprocess
import argparse

TRANSMISSION_RANGE = 80.0

def Experiment(timeLimit: float=120.0, waitTimeBeforeStart=0.0, trafficDelay=0.0, name: str = ""):
    routingProtocol = None
    trafficInstance = None

    """
    Parametrize Routing Protocol
    """
    config = dict()
    config["experimentName"] = name

    # Parrod config
    config["mhChirpInterval"] = 0.5
    config["neighborReliabilityTimeout"] = 2.5
    config["qFctAlpha"] = 0.4
    config["qFctGamma"] = 0.9
    config["maxHops"] = 32
    config["historySize"] = 5
    config["rescheduleRoutesOnTimeout"] = True

    ## Mobility Prediction
    config["predictionMethod"] = "slope"
    config["waypointProvider"] = ""

    # Network settings
    config["ifname"] = "wlan0"
    config["ipAddress"] = "20.0.0.7"

    # UDP settings
    config["broadcastAddress"] = "20.0.0.255"
    config["bcPort"] = 1801
    config["bufferSize"] = 1460

    # GNSS Configuration
    config["gnssUpdateInterval"] = 1.0
    config["gpsReferencePoint"] = {
        "lat": 51.49051416,
        "lon": 7.41436899,
        "alt": 106.6
    }

    """
    Parametrize Traffic
    """
    traffic = {
        "CBR": 2.0,
        "MTU": 1460,
        "Sender": "20.0.0.3",
        "Destination": "20.0.0.7",
        "Port": 1901,
        "Filename": f'{config["experimentName"]}_eval.csv'
    }

    routingProtocol = Parrod(config, TRANSMISSION_RANGE)

    if config["ipAddress"] == traffic["Sender"]:
        subprocess.Popen(f'iperf3 -c {traffic["Sender"]} -b 2m -l {traffic["MTU"]} -u -t {timeLimit} -p {traffic["Port"]}'.split(' '), stdout=subprocess.PIPE)
    elif config["ipAddress"] == traffic["Destination"]:
        #subprocess.Popen(f'iperf3 -s -p {traffic["Port"]} -J --logfile {config["experimentName"]}.json'.split(' '), stdout=subprocess.PIPE)
        pass
        # Open server manually!

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
    parser = argparse.ArgumentParser(description='Parrod')
    parser.add_argument('-n', dest='name', type=str, help='Specify a role for this agent.', required=True)
    args = parser.parse_args()
    Experiment(timeLimit=180, waitTimeBeforeStart=10.0, trafficDelay=5.0, name=args.name)


