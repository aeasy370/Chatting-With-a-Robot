import logging
import socket
import json


log = logging.getLogger(f"server.handler")


class RoboComm:
    """a lightweight interface for sending/receiving data from robots/PLCs
    """
    def __init__(self, host: str, port: str, demo_mode: bool = False):
        self.host = host
        self.port = port
        self.demo_mode = demo_mode
        if self.demo_mode:
            self.demo_strings = json.load(open("./demostrings.json", "r"))
        if not self.demo_mode:
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conn.settimeout(5)

            self.conn.connect((self.host, self.port))
    
    def send(self, data: str):
        """takes a string and sends it to the PLC/Robot
        """
        if self.demo_mode:
            self.demo_str = data
            return
        
        # regular operation
        self.conn.sendall(bytes(data))
    
    def receive(self) -> bytes:
        """attempts to receive data from the robot, returns the received data in bytes form
        """
        # receive 32 bytes at a time as in the example code we were given
        if self.demo_mode:
            try:
                return self.demo_strings[self.demo_str]
            except KeyError:
                return "Invalid request"
        
        buffer = b""
        while True:
            data = self.conn.recv(32)
            if len(data) != 32:
                # connection closed
                break

            buffer += data
        
        return buffer
