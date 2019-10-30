import socket
import threading

import helpers.encryption as enc
import helpers.message as msg


class ServerApp:
    def __init__(self, master_server_ip, master_server_port, buffer_size):
        self.buffer_size = buffer_size
        self.master_server_ip = master_server_ip
        self.master_server_port = master_server_port
        self.next_id = 0
        self.connections = {}
        self.addresses = {}
        threading.Thread(target=self.master_server_loop, args=()).start()

    def client_loop(self, client_id, connection, address):
        data = connection.recv(self.buffer_size)
        if not data:
            connection.send(msg.create_message(action='ERROR', arg1="no data"))
            connection.close()
        received_json = msg.message_to_json(data)
        if received_json['action'] != "HELLO":
            connection.send(msg.create_message(action='ERROR', arg1="wrong first message"))
            connection.close()
        public_key, private_key = enc.new_key()
        connection.send(public_key)
        client_public_key = connection.recv(self.buffer_size)
        connection.send(msg.create_message(action="OK"))

        data = connection.recv(self.buffer_size)
        received_json = msg.message_to_json(data)

        connection.send(msg.create_message(action="OK"))

        while True:
            data = connection.recv(self.buffer_size)
            if not data:
                break
            data = msg.message_to_json(data)
            if data["action"] == "UU":
                u_msg = msg.create_message(action="UU", arg1=self.addresses)
                connection.send(u_msg)
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
            threading.Thread(target=self.client_loop, args=(self.next_id, conn, address)).start()
            self.next_id = self.next_id + 1
