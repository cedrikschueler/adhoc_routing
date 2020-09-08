from Routing.Parrod import Parrod
import time

def Experiment():
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

    config["gnssUpdateInterval"] = 0.2

    parrod = Parrod(config, 230.0)
    parrod.start()
    time.sleep(120)
    parrod.stop()


if __name__ == "__main__":
    Experiment()


