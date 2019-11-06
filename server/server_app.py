import socket
import threading

import helpers.crypto_rsa as enc
import helpers.message as msg
from argon2 import PasswordHasher
import argon2
from Crypto.Hash import SHA256
import pickle
from models.server_client import Client
from models.server_client_status import ClientStatus
from models.server_client_authorization_data import ClientAuthorizeData


class ServerApp:
    def __init__(self,
                 master_server_ip: str,
                 master_server_port: int,
                 buffer_size: int,
                 username_salt: str,
                 token_salt: str
                 ):
        self.username_salt = username_salt
        self.token_salt = token_salt
        self.user_file_data_name = 'server_users.sch'
        self.buffer_size = buffer_size
        self.master_server_ip = master_server_ip
        self.master_server_port = master_server_port
        self.next_id = 0
        self.clients = {}
        self.hashes = self.load_hashes()
        self.ph = PasswordHasher()
        threading.Thread(target=self.master_server_loop, args=()).start()

    def create_hash(self, data):
        data = data + self.username_salt
        return SHA256.new(data=data.encode()).hexdigest()

    def if_username_free(self, username):
        username_hash = self.create_hash(username)
        for h in self.hashes:
            if h.username == username_hash:
                return False
        return True

    def if_credentials_correct(self, username, password):
        username_hash = self.create_hash(username)
        for h in self.hashes:
            if h.username == username_hash:
                try:
                    return self.ph.verify(h.password, password)
                except argon2.exceptions.VerifyMismatchError:
                    return False

    def create_uu_user_object(self, client, friend_user):
        return {friend_user.login: [friend_user.address[0],
                                    friend_user.listen_port,
                                    self.create_secret_token(client.login, friend_user.login)
                                    ]
                }

    def create_uu_array(self, client, json_request):
        json_array = []
        request_array = json_request["ulist"]

        for k in self.clients.keys():
            if self.clients[k].status == ClientStatus.LOGGED_IN:
                if self.clients[k].login in request_array:
                    json_array.append(self.create_uu_user_object(client, self.clients[k]))

        return json_array

    def create_secret_token(self, user1, user2):
        sorted_users = [user1, user2, self.token_salt]
        return self.create_hash(sorted_users[0] + sorted_users[1] + sorted_users[2])

    def load_hashes(self):
        try:
            file = open(self.user_file_data_name, 'rb')
            hashes = pickle.load(file)
            print("DB loaded")
            file.close()
        except FileNotFoundError:
            hashes = []
            pickle.dump(hashes, open(self.user_file_data_name, "wb+"))
            print("DB file created")
        return hashes

    def save_hashes(self):
        pickle.dump(self.hashes, open(self.user_file_data_name, "wb+"))
        print("DB saved")

    def client_loop(self, client_id: int, connection, address):
        print("Client Loop started: ", address)
        data = connection.recv(self.buffer_size)
        if not data:
            connection.send(msg.create_message(action='ERROR', arg1="no data"))
            connection.send(msg.create_message(action='OUT'))
            connection.close()
            del self.clients[client_id]
            return
        received_json = msg.message_to_json(data)
        if received_json['action'] != "HELLO":
            connection.send(msg.create_message(action='ERROR', arg1="wrong first message"))
            connection.send(msg.create_message(action='OUT'))
            connection.close()
            del self.clients[client_id]
            return

        print("Received HELLO: ", address)

        public_key, private_key = enc.CryptoRSA.new_key()

        print("Created server key: ", address)

        connection.send(public_key)

        print("Sent server public key: ", address)

        client_public_key = enc.CryptoRSA.decrypt_with_key(private_key, connection.recv(self.buffer_size))
        rsa = enc.CryptoRSA(client_public_key, private_key)

        print("Recived client public key: ", address)
        connection.send(rsa.encrypt(msg.create_message(action="OK")))
        print("Sent OK to client after receiving public key : ", address)

        print("Client Connected : ", address)
        self.clients[client_id].status = ClientStatus.CONNECTED

        data = rsa.decrypt(connection.recv(self.buffer_size))
        received_json = msg.message_to_json(data)

        if received_json["action"] == 'R':
            print("Client Registering : ", address)
            if self.if_username_free(received_json["login"]):
                client_authorized_data = ClientAuthorizeData(username=self.create_hash(received_json["login"]),
                                                             password=self.ph.hash(received_json["password"]))
                self.hashes.append(client_authorized_data)
                self.save_hashes()

                self.clients[client_id].status = ClientStatus.LOGGED_IN
                self.clients[client_id].login = received_json["login"]
                self.clients[client_id].listen_port = received_json["port"]

                print("Client Registered in : ", address)
            else:
                print("Username exist in database : ", address)
                connection.send(msg.create_message(action='ERROR', arg1="username taken"))
                connection.send(msg.create_message(action='OUT'))
                connection.close()
                del self.clients[client_id]
                return

        elif received_json["action"] == 'L':
            print("Client Logging in : ", address)
            if self.if_credentials_correct(received_json["login"], received_json["password"]):
                self.clients[client_id].status = ClientStatus.LOGGED_IN
                self.clients[client_id].login = received_json["login"]
                self.clients[client_id].listen_port = received_json["port"]
                print("Client Logged in : ", address)
            else:
                print("Wrong credentials at logging in, disconnecting : ", address)
                connection.send(msg.create_message(action='ERROR', arg1="username or password incorrect"))
                connection.send(msg.create_message(action='OUT'))
                connection.close()
                del self.clients[client_id]
                return

        else:
            print("Wrong action from client (expected R/L) : ", address)
            connection.send(msg.create_message(action='ERROR', arg1="wrong action"))
            connection.send(msg.create_message(action='OUT'))
            connection.close()
            del self.clients[client_id]
            return

        connection.send(rsa.encrypt(msg.create_message(action="OK")))
        print("Respond OK after L/R action: ", address)

        while True:
            data = rsa.decrypt(connection.recv(self.buffer_size))
            if not data:
                break
            data = msg.message_to_json(data)
            if data["action"] == "UU":
                u_msg = rsa.encrypt(msg.create_message(action="UU",
                                                       arg1=self.create_uu_array(self.clients[client_id],
                                                                                 data)
                                                       ))
                connection.send(u_msg)
            else:
                print("Wrong action from client (expected UU) : ", address)
                connection.send(msg.create_message(action='ERROR', arg1="wrong action after login"))
                connection.send(msg.create_message(action='OUT'))
                connection.close()
                del self.clients[client_id]
                return
        connection.close()

    def master_server_loop(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.master_server_ip, self.master_server_port))
        s.listen(self.buffer_size)
        print("Server Started")
        while True:
            connection, address = s.accept()
            self.clients.update({self.next_id: Client(client_id=self.next_id, address=address, connection=connection)})
            print('Incoming Connection: id: ', self.next_id, ' address: ', address)
            threading.Thread(target=self.client_loop, args=(self.next_id, connection, address)).start()
            self.next_id = self.next_id + 1
