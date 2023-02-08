import socket

TCP_IP = 'localhost'
TCP_PORT = 9001
BUFFER_SIZE = 1024

class Client():

    def __init__(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((TCP_IP, TCP_PORT))
        self.sock = s
        print("new thread " + TCP_IP +":" +str(TCP_PORT))

    def put(self,inputFile):
        with open(inputFile, 'rb') as file_to_send:
            for data in file_to_send:
                self.sock.sendall(data)
        print('send Successful')
        self.sock.close()
        print('Close successful')
        return

    def receive(self):
        with open("received_1_file.txt",'wb') as f:
            while True:
                data = self.sock.recv(BUFFER_SIZE)
                if not data:
                    break
                f.write(data)
        f.close()
        print('send Successful')
        self.sock.close()
        print('Close successful')


while True:
    client_input = input("Send or recieve file: ")
    
    if client_input == "send":
        c1 = Client()
        input1 =("enter filename: ")
        c1.put(input1)

    if client_input == "quit":
        break;
    
    
"""
def read():
    with open('received_file.txt', 'wb') as f:
        print('file opened')
        while True:
            #print('receiving data...')
            data = s.recv(BUFFER_SIZE)
            print('data=%s', (data))
            if not data:
                f.close()
                print('file close()')
                break
            # write data to a file
            f.write(data)


read()
    """