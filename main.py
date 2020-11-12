from Routing.PARRoT import PARRoT
from Traffic.TrafficGenerator import TrafficGenerator, TrafficReceiver
import time
import subprocess
import argparse

TRANSMISSION_RANGE = 25.0

ref_KoelnerDom = {
    "lat": 51.49150,
    "lon": 7.41340,
    "alt": 60.0
}

def Experiment(timeLimit: float=120.0, waitTimeBeforeStart=0.0, trafficDelay=0.0, verbose: bool = False, name: str = ""):
    routingProtocol = None
    trafficInstance = None

    """
    Parameterize Routing Protocol
    """
    config = dict()
    config["experimentName"] = name
    config["verbose"] = verbose
    # Parrod config
    config["mhChirpInterval"] = 1.0
    config["neighborReliabilityTimeout"] = 2.0
    config["qFctAlpha"] = 0.5
    config["qFctGamma"] = 0.8
    config["maxHops"] = 32
    config["historySize"] = 5
    config["rescheduleRoutesOnTimeout"] = False

    ## Mobility Prediction
    config["predictionMethod"] = "slope"
    config["waypointProvider"] = ""

    # Network settings
    config["ifname"] = "wlan0"
    config["ipAddress"] = "20.0.0.1"
    config["coordinatorAddress"] = "20.0.0.7"

    # UDP settings
    config["broadcastAddress"] = "20.0.0.255"
    config["bcPort"] = 1801
    config["bufferSize"] = 1460

    # GNSS Configuration
    config["gnssUpdateInterval"] = 1.0
    config["gpsReferencePoint"] = ref_KoelnerDom

    '''
    Traffic Generator is disabled!
    ------------------------------
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
    '''
    routingProtocol = PARRoT(config, TRANSMISSION_RANGE)

    '''
    Traffic Generator is disabled!
    ------------------------------
    if config["ipAddress"] == traffic["Sender"]:
        subprocess.Popen(f'iperf3 -c {traffic["Sender"]} -b 2m -l {traffic["MTU"]} -u -t {timeLimit} -p {traffic["Port"]}'.split(' '), stdout=subprocess.PIPE)
    elif config["ipAddress"] == traffic["Destination"]:
        #subprocess.Popen(f'iperf3 -s -p {traffic["Port"]} -J --logfile {config["experimentName"]}.json'.split(' '), stdout=subprocess.PIPE)
        pass
        # Open server manually!
    '''
    # After everything is set up, wait to start the experiment
    time.sleep(waitTimeBeforeStart)

    # Start routing instance and traffic instance if there is one
    routingProtocol.start()
    '''
    Traffic Generator is disabled!
    ------------------------------
    if trafficInstance is not None:
        # Wait with traffic instance for given delay
        time.sleep(trafficDelay)
        trafficInstance.start()
'   '''
    # Let the experiment run before terminating it
    time.sleep(timeLimit)

    # Terminate instances
    '''
    Traffic Generator is disabled!
    ------------------------------
    if trafficInstance is not None:
        trafficInstance.terminate()
    '''
    routingProtocol.terminate()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='PARRoT')
    parser.add_argument('-n', dest='name', type=str, help='Specify a name for this experiment.', required=True)
    parser.add_argument('-v', dest='verbose', type=bool, help='Print outputs', default=True)
    args = parser.parse_args()
    Experiment(timeLimit=900, waitTimeBeforeStart=10.0, trafficDelay=0.0, verbose=args.verbose, name=args.name)


