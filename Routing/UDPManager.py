import socket
import multiprocessing
import time

ENCODING = "utf-8"

class UDPManager(multiprocessing.Process):

    def __init__(self, port: int, buffersize=10000) -> None:
        multiprocessing.Process.__init__(self)
        self.address = ""
        self.port = port
        self.bufferSize = buffersize

        self.subscriptions = []
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def subscribe(self, callable):
        '''
        Appends a callable to list of subscriptors
        :param callable: Compatible function to call
        :return:
        '''
        self.subscriptions.append(callable)

    def listen(self) -> None:
        '''
        Binds the socket to (address, port) and starts the runtime
        :return:
        '''
        self.socket.bind((self.address,  self.port))
        self.start()

    def run(self):
        '''
        Runtime method.
        The socket listens to udp port and notifies subscriptors if a message is received
        :return:
        '''
        try:
            while True:
                data, _ = self.socket.recvfrom(self.bufferSize)
                if len(self.subscriptions) != 0:
                    for c in self.subscriptions:
                        c(data)
        except StopIteration:
            pass

    def broadcastData(self, data: bytearray):
        '''
        Sends a broadcast on bound port
        :param data: Bytearray to send
        :return:
        '''
        self.socket.sendto(data, ('<broadcast>', self.port))

if __name__ == "__main__":
    udp_mgr = UDPManager(1801)
    udp_mgr.listen()
    time.sleep(60)
    exit()
    while 1:
        time.sleep(1)
        udp_mgr.broadcastData("Lorem ipsum dolor sit amet")