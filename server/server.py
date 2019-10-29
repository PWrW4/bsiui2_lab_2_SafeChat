import socket
import threading
import os


class MasterServer:
    def __init__(self, master_server_ip, master_server_port, buffer_size):
        self.buffer_size = buffer_size
        self.master_server_ip = master_server_ip
        self.master_server_port = master_server_port
        self.next_id = 0
        self.connections = {}
        self.addresses = {}
        threading.Thread(target=self.master_server_loop, args=()).start()

    def client_loop(self, client_id, connection, address):
        # print(connection)
        # print(address)
        while True:
            data = connection.recv(self.buffer_size)
            if not data:
                break
            print("received data from ", client_id, ":", data.decode(encoding='utf-8'))
            connection.send(data)  # echo
        connection.close()

    def master_server_loop(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.master_server_ip, self.master_server_port))
        s.listen(self.buffer_size)
        print("Server Started")
        while True:
            conn, address = s.accept()
            self.addresses.update({self.next_id: address})
            self.connections.update({self.next_id: conn})
            print('Connection address:', self.next_id, ' : ', address)
            threading.Thread(target=self.client_loop, args=(self.next_id,conn, address)).start()
            self.next_id = self.next_id + 1
