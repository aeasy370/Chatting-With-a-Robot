import socket

TCP_IP = 'localhost'
TCP_PORT = 9001
BUFFER_SIZE = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))

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

print('Successfully get the file')
print('connection closed')