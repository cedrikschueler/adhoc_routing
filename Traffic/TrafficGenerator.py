import threading
import socket
import time

class TrafficGenerator(threading.Thread):

    def __init__(self, targetCBR_MBits: float, destination: str, MTU_used_bit: float, port: int):
        threading.Thread.__init__(self)
        self.updateInterval = (MTU_used_bit*8)/(targetCBR_MBits*1e6)
        self.destination = destination
        self.port = port

        # Setup socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.settimeout(0.1) #todo what does this do?

        # Create meaningless data for desired MTU size
        self.data = bytearray([0 for x in range(0,MTU_used_bit)])

    def run(self):
        while True:
            self.socket.sendto(self.data, (self.destination, self.port))
            time.sleep(self.updateInterval)
