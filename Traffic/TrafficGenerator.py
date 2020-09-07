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
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)   # todo: Maybe remove this for production?
        self.socket.settimeout(0.1) #todo what does this do?

        # Create meaningless data for desired MTU size
        self.data = bytearray([0 for x in range(0, MTU_used_bit)])

    def run(self):
        try:
            while True:
                self.socket.sendto(self.data, (self.destination, self.port))
                time.sleep(self.updateInterval)
        except StopIteration:
            pass

class TrafficReceiver(threading.Thread):

    def __init__(self, sender: str, port: int, bufferSize: int):
        threading.Thread.__init__(self)
        self.port = port
        self.bufferSize = bufferSize
        self.sender = sender

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(("", self.port))

    def run(self):
        try:
            while True:
                data, addr = self.socket.recvfrom(self.bufferSize)
                if addr[0] == self.sender:
                    print("received message with ", len(data), " Bytes from ", addr[0])
        except StopIteration:
            pass

if __name__ == "__main__":

    tr = TrafficReceiver('192.168.178.24', 1801, 1460)
    tr.start()
    exit()

    tg = TrafficGenerator(2.0, "<broadcast>", MTU_used_bit=1460, port=1801)
    tg.start()
    time.sleep(60)
    tg.raise_exception()
    tg.join()
    exit()