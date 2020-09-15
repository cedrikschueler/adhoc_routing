import multiprocessing
import socket
import time
import struct
import sys
import numpy as np

class TrafficGenerator(multiprocessing.Process):
    sequenceNumber = 0

    def __init__(self, targetCBR_MBits: float, destination: str, MTU_used_byte: float, port: int):
        multiprocessing.Process.__init__(self)
        self.MTU_used_byte = MTU_used_byte
        self.updateInterval = (MTU_used_byte * 8) / (targetCBR_MBits * 1e6)
        self.destination = destination
        self.port = port

        # Setup socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if self.destination == "<broadcast>":
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)



    def getData(self) -> bytearray:
        # Create meaningless data for desired MTU size
        sequenceNumber_b = struct.pack("Qd", self.sequenceNumber, time.time())

        if self.sequenceNumber == sys.maxsize:
            self.sequenceNumber = 0
        else:
            self.sequenceNumber += 1

        return sequenceNumber_b + bytearray([0 for x in range(0, self.MTU_used_byte - len(sequenceNumber_b))])

    def run(self):
        '''
        Runtime method. Sends data via UDP socket with desired constant bit rate
        :return:
        '''
        try:
            while True:
                self.socket.sendto(self.getData(), (self.destination, self.port))
                # todo Add something for evaluation here
                time.sleep(self.updateInterval)
        except StopIteration:
            pass

class TrafficReceiver(multiprocessing.Process):

    def __init__(self, sender: str, port: int, bufferSize: int, filename:str = "eval.csv"):
        multiprocessing.Process.__init__(self)
        self.port = port
        self.bufferSize = bufferSize
        self.sender = sender
        self.filename = filename

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(("", self.port))

        self.receivedPackets = []
        self.senderSquNr = 0
        with open(self.filename, "a+") as f:
            f.write(f'TIME,PDR,DELAY\n')
            f.close()

    def saveInterval(self, receivedPackets) -> None:
        '''
        Calculates PDR and average delay and saves to file
        :param receivedPackets:
        :return:
        '''
        if receivedPackets:
            t = np.floor(receivedPackets[0][0]) # Take first timestamp as mark in result file
            pdr = (receivedPackets[-1][1] - self.senderSquNr)/len(receivedPackets)  #Difference of received packets/total received packets, todo: Precise enough?
            self.senderSquNr = receivedPackets[-1][1]   # Set sequenceNumber to latest value
            avg_delay = np.mean([p[2] for p in receivedPackets])

            with open(self.filename, "a+") as f:
                f.write(f'{t},{pdr},{avg_delay}\n')
                f.close()

    def run(self):
        '''
        Runtime method. Listens to UDP socket
        :return:
        '''
        try:
            t0 = time.time()
            while True:
                data, addr = self.socket.recvfrom(self.bufferSize)
                if addr[0] == self.sender or self.sender == "":
                    t1 = time.time()
                    _squNr, _t0 = struct.unpack("Qd", data[:16])    # Unpack non-padding elements
                    self.receivedPackets.append((t1, _squNr, t1-t0, addr[0]))
                    if t1 - t0 > 1.0:
                        self.saveInterval(self.receivedPackets.copy())
                        self.receivedPackets = []
                        t0 = t1

        except StopIteration:
            pass

if __name__ == "__main__":

    tr = TrafficReceiver('192.168.178.24', port=1801, bufferSize=1460)
    tr.start()
    time.sleep(60)
    tr.terminate()
    exit()

    tg = TrafficGenerator(2.0, "<broadcast>", MTU_used_byte=1460, port=1801)
    tg.start()
    time.sleep(60)
    tg.terminate()
    exit()