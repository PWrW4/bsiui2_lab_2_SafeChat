import socket
import threading

import helpers.message as msg
import helpers.crypto_rsa as enc


class ClientApp:
    def __init__(self, master_server_ip: str, master_server_port: int, buffer_size: int):
        self.buffer_size = buffer_size
        self.master_server_ip = master_server_ip
        self.master_server_port = master_server_port
        self.client_port = 0
        threading.Thread(target=self.client_server, args=()).start()
        threading.Thread(target=self.client_listening, args=()).start()

    def client_from_client(self, connection, address):
        data = connection.recv(self.buffer_size)
        if not data:
            connection.send(msg.create_message(action='ERROR', arg1="no data"))
            connection.close()
        received_json = msg.message_to_json(data)

    def client_to_client(self, connection, address):
        data = connection.recv(self.buffer_size)
        if not data:
            connection.send(msg.create_message(action='ERROR', arg1="no data"))
            connection.close()
        received_json = msg.message_to_json(data)

    def client_server(self):
        print("client connecting")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.master_server_ip, self.master_server_port))
        s.send(msg.create_message(action="HELLO"))
        public_key, private_key = enc.CryptoRSA.new_key()
        server_public_key = s.recv(self.buffer_size)
        rsa = enc.CryptoRSA(server_public_key, private_key)
        s.send(rsa.encrypt(public_key))
        data = rsa.decrypt(s.recv(self.buffer_size))
        data_json = msg.message_to_json(data)
        if data_json['action'] != "OK":
            print("no ok status after key exchange")
            s.close()

        action = ''
        while action != "L" and action != "R":
            action = input("Login(L) or Register(R)")

        login = input("Login: ")
        password = input("Password: ")

        login_register_msg = rsa.encrypt(msg.create_message(action=action, arg1=login, arg2=password))
        s.send(login_register_msg)

        data = rsa.decrypt(s.recv(self.buffer_size))
        data_json = msg.message_to_json(data)
        if data_json['action'] != "OK":
            print("no ok status after key exchange")
            s.close()

        u_msg = rsa.encrypt(msg.create_message(action="UU", arg1={}))
        s.send(u_msg)

        data = rsa.decrypt(s.recv(self.buffer_size))
        data_json = msg.message_to_json(data)

        print(data_json)
        s.close()

    def client_listening(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.master_server_ip, 0))
        s.listen(self.buffer_size)

        print("Client listening on port: ", s.getsockname()[1])

        while True:
            conn, address = s.accept()
            print('Client connected address: ', address)
            threading.Thread(target=self.client_from_client, args=(conn, address)).start()
