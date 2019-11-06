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
        print("C1: ", address)
        data = connection.recv(self.buffer_size)
        if not data:
            connection.send(msg.create_message(action='ERROR', arg1="no data"))
            connection.close()
        received_json = msg.message_to_json(data)
        if received_json['action'] != "HELLO":
            connection.send(msg.create_message(action='ERROR', arg1="wrong first message"))
            connection.close()
        public_key, private_key = enc.CryptoRSA.new_key()
        connection.send(public_key)
        client_public_key = connection.recv(self.buffer_size)
        rsa = enc.CryptoRSA(client_public_key, private_key)
        connection.send(rsa.encrypt(msg.create_message(action="OK")))
        data = rsa.decrypt(connection.recv(self.buffer_size))

        received_json = msg.message_to_json(data) # to powinien być CT
        if received_json['action'] != "CT":
            print("its not connection token")
            connection.close()

        connection.send(rsa.encrypt(msg.create_message(action="OK")))
        # dalej wymiana wiadomosci

    def client_to_client(self, connection, address):
        print("C2: ", address)
        connection.send(msg.create_message(action="HELLO"))
        public_key, private_key = enc.CryptoRSA.new_key()
        client_public_key = connection.recv(self.buffer_size)
        rsa = enc.CryptoRSA(client_public_key, private_key)
        connection.send(public_key)
        data = rsa.decrypt(connection.recv(self.buffer_size))
        data_json = msg.message_to_json(data)
        if data_json['action'] != "OK":
            print("no ok status after key exchange")
            connection.close()

        connection.send(rsa.encrypt(msg.create_message(action="CT", arg1="superSecretToken"))) # Tu powinno być wyslanie CT

        data = rsa.decrypt(connection.recv(self.buffer_size))
        data_json = msg.message_to_json(data)
        if data_json['action'] != "OK":
            print("no ok status after connection token")
            connection.close()

        # dalej wymiana wiadomosci

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
            action = (input("Login(L) or Register(R)")).upper()

        login = input("Login: ")
        password = input("Password: ")

        login_register_msg = rsa.encrypt(msg.create_message(action=action, arg1=login, arg2=password, arg3=self.client_port))
        s.send(login_register_msg)

        data = rsa.decrypt(s.recv(self.buffer_size))
        data_json = msg.message_to_json(data)
        if data_json['action'] != "OK":
            print("no ok status after login/register")
            s.close()

        threading.Thread(target=self.client_console, args=(s, rsa)).start()

    def client_listening(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.master_server_ip, 0))
        s.listen(self.buffer_size)

        print("Client listening on port: ", s.getsockname()[1])
        self.client_port = s.getsockname()[1]

        while True:
            conn, address = s.accept()
            print('Client connected address: ', address)
            threading.Thread(target=self.client_from_client, args=(conn, address)).start()

    def client_console(self, server, rsa_server):

        def update_contacts():
            u_msg = rsa_server.encrypt(msg.create_message(action="UU", arg1=friends))
            server.send(u_msg)

            data = rsa_server.decrypt(server.recv(self.buffer_size))
            # data = b'{"action":"UU","ulist":[{"adrian":["127.0.0.1",64079,"superSecretToken"]},{"marcin":["127.0.0.1",1338,"superSecretToken"]},{"tomek":["127.0.0.1",1339,"superSecretToken"]}]}'
            data_json = msg.message_to_json(data)
            ulist = data_json['ulist']

            for i in range(len(ulist)):
                contacts.update(ulist[i])

        print("Now you can connect to other clients (write $help for more instruction)")
        command_list = ["$quit", "$exit", "$help", "$online", "$friends", "$add_friend", "$remove_friend, $connect"]
        friends = []
        contacts = {}
        command = ""
        while command != "$exit" and command != "$quit":
            command = input()
            if command == "$exit" or command == "$quit":
                print("The end is near")
                server.close()
            elif command == "$help":
                print(command_list)
            elif command == "$friends":
                print("Your friend list: " + str(friends))
            elif command == "$add_friend":
                friends.append(input("Your friend nick: "))
                print("New friend added to list")
            elif command == "$remove_friend":
                friends.remove(input("Your friend nick: "))
                print("Your friend has been removed from friend list")
            elif command == "$online":
                update_contacts()
                print(contacts)
            elif command == "$connect":
                update_contacts()
                user = input("Connect to: ")
                if user in contacts.keys():
                    CT = contacts[user][2]
                    address = (contacts[user][0], contacts[user][1])
                    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    connection.connect((contacts[user][0], contacts[user][1]))
                    threading.Thread(target=self.client_to_client, args=(connection, address)).start()
                    command = "$exit"
                else:
                    print("Wrong user")

            else:
                print("Write $help for help :)")
