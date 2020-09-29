import socket
import threading
import time

ENCODING = "utf-8"

class UDPManager(threading.Thread):

    def __init__(self, port: int, broadcastAddress:str, buffersize=10000) -> None:
        threading.Thread.__init__(self)
        self.broadcastAddress = broadcastAddress
        self.port = port
        self.bufferSize = buffersize

        self.running = False
        self.subscriptions = []
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
        self.socket.bind(("",  self.port))
        self.running = True
        self.start()

    def run(self):
        '''
        Runtime method.
        The socket listens to udp port and notifies subscriptors if a message is received
        :return:
        '''
        try:
            while self.running:
                data, _ = self.socket.recvfrom(self.bufferSize)
                if len(self.subscriptions) != 0:
                    for c in self.subscriptions:
                        c(data)
        except StopIteration:
            pass

    def terminate(self):
        '''
        Sets the running flag to false and joins the Thread
        :return:
        '''
        self.running = False
        self.join()

    def broadcastData(self, data: bytearray):
        '''
        Sends a broadcast on bound port
        :param data: Bytearray to send
        :return:
        '''
        self.socket.sendto(data, (self.broadcastAddress, self.port))

if __name__ == "__main__":
    udp_mgr = UDPManager(1801)
    udp_mgr.listen()
    time.sleep(60)
    exit()
    while 1:
        time.sleep(1)
        print("Sending")
        udp_mgr.broadcastData("Lorem ipsum dolor sit amet".encode("utf-8"))