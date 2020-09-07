import socket
import threading
import time

ENCODING = "utf-8"
class UDPManager(threading.Thread):

    def __init__(self, port: int) -> None:
        threading.Thread.__init__(self)
        self.address = ""
        self.port = port

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

    def listen(self) -> None:
        self.socket.bind((self.address,  self.port))
        self.start()

    def run(self):
        try:
            while True:
                data = self.socket.recv(1024)   #todo buffer size
                print("received message: %s" % data.decode(ENCODING))
        except StopIteration:
            pass

    def broadcastData(self, data: str):
        self.socket.sendto(data.encode(ENCODING), ('<broadcast>', self.port))

if __name__ == "__main__":
    udp_mgr = UDPManager(1801)
    udp_mgr.listen()
    time.sleep(60)
    exit()
    while 1:
        time.sleep(1)
        udp_mgr.broadcastData("Lorem ipsum solor amet")