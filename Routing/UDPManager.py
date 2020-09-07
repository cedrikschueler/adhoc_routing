import socket
import threading
import time

ENCODING = "utf-8"
class UDPManager(threading.Thread):

    def __init__(self, address, port: int) -> None:
        threading.Thread.__init__(self)
        self.address = address
        self.port = port

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def listen(self) -> None:
        self.socket.bind((self.address,  self.port))
        self.start()

    def run(self):
        try:
            while 1:
                data = self.socket.recv(1024)   #todo buffer size
                print("received message: %s" % data.decode(ENCODING))
        except StopIteration:
            pass

    def broadcastData(self, data: str, length: int):
        self.socket.sendto(data.encode(ENCODING), (self.address, self.port))

if __name__ == "__main__":
    udp_mgr = UDPManager("127.0.0.1", 1801)
    udp_mgr.listen()
    while 1:
        time.sleep(1)
        udp_mgr.broadcastData("Lorem ipsum solor amet", 16)