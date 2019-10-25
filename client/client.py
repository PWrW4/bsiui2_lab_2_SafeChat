import socket

TCP_IP = '127.0.0.1'
TCP_PORT = 6666
BUFFER_SIZE = 1
MESSAGE = "hello server\n"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
s.send(MESSAGE.encode())
while True:
    data = s.recv(1)
    if data:
        print("received data:", data.decode('utf-8'))
    data = ''

s.close()

