import socket


class Client:
    def __init__(self, master_server_ip, master_server_port, buffer_size):
        self.buffer_size = buffer_size
        self.master_server_ip = master_server_ip
        self.master_server_port = master_server_port
        self.message = input('Message: ')

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.master_server_ip, self.master_server_port))
        s.send(self.message.encode('utf-8'))
        data = s.recv(self.buffer_size)
        if data:
            print("received data:", data.decode('utf-8'))
        else:
            print("no data")
        s.close()


