import logging
import socket


log = logging.getLogger(f"server.handler")


class RoboComm:
    """a lightweight interface for sending/receiving data from robots/PLCs
    """
    def __init__(self, host: str, port: str):
        self.host = host
        self.port = port
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.settimeout(5)

        self.conn.connect((self.host, self.port))
    
    def send(self, data: str):
        """takes a string and sends it to the PLC/Robot
        """
        self.conn.sendall(bytes(data))
    
    def receive(self) -> bytes:
        """attempts to receive data from the robot, returns the received data in bytes form
        """
        # receive 32 bytes at a time as in the example code we were given
        buffer = b""
        while True:
            data = self.conn.recv(32)
            if len(data) != 32:
                # connection closed
                break

            buffer += data
        
        return buffer
