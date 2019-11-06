import socket
import threading

import helpers.message as msg
import helpers.crypto_rsa as enc
from models.client_client import Client


class ClientApp:
    def __init__(self, master_server_ip: str, master_server_port: int, buffer_size: int):
        self.buffer_size = buffer_size
        self.master_server_ip = master_server_ip
        self.master_server_port = master_server_port
        self.client_port = 0
        self.rsa_server = None
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected_clients = []
        self.nick = ""

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

        # encrypting everything from here

        connection.send(rsa.encrypt(msg.create_message(action="OK")))
        data = rsa.decrypt(connection.recv(self.buffer_size))

        received_json = msg.message_to_json(data)
        if received_json['action'] != "CT":
            print("token error - token not found")
            connection.send(msg.create_message(action='ERROR', arg1="bad connection token"))
            connection.close()

        print(received_json)

        partner_user_nickname = received_json['nick']

        u_msg = self.rsa_server.encrypt(msg.create_message(action="UU", arg1=[received_json['nick']]))
        self.server.send(u_msg)

        data = self.rsa_server.decrypt(self.server.recv(self.buffer_size))
        data_json = msg.message_to_json(data)
        ulist = data_json['ulist']
        your_ct = (((ulist[0])[received_json['nick']])[2])

        print(data_json)
        # print(received_json['token'], your_ct)

        if received_json['token'] != your_ct:
            print("token error - tokens not equals", received_json['token'], your_ct)
            connection.send(msg.create_message(action='ERROR', arg1="bad connection token"))
            connection.close()

        connection.send(rsa.encrypt(msg.create_message(action="OK")))
        # dalej wymiana wiadomosci

        self.connected_clients.append(Client(connection=connection, address=address, rsa=rsa, login=partner_user_nickname))

        while True:
            data = rsa.decrypt(connection.recv(self.buffer_size))
            data_json = msg.message_to_json(data)
            if data_json['action'] != "M":
                print("no M recived from client: ", partner_user_nickname)
                connection.close()
            else:
                print("recived msg from ", partner_user_nickname, " : ", data_json["message"])

    def client_to_client(self, connection, address, partner_user_nickname):
        print("C2: ", address)
        connection.connect((address[0], address[1]))
        connection.send(msg.create_message(action="HELLO"))
        public_key, private_key = enc.CryptoRSA.new_key()
        client_public_key = connection.recv(self.buffer_size)

        # encrypting everything from here

        rsa = enc.CryptoRSA(client_public_key, private_key)
        connection.send(public_key)
        data = rsa.decrypt(connection.recv(self.buffer_size))
        data_json = msg.message_to_json(data)
        if data_json['action'] != "OK":
            print("no ok status after key exchange")
            connection.close()

        u_msg = self.rsa_server.encrypt(msg.create_message(action="UU", arg1=[partner_user_nickname]))
        self.server.send(u_msg)

        data = self.rsa_server.decrypt(self.server.recv(self.buffer_size))
        data_json = msg.message_to_json(data)

        print(data_json)

        ulist = data_json['ulist']
        your_ct = (((ulist[0])[partner_user_nickname])[2])

        print("My CT to user: ", partner_user_nickname, " : ", your_ct)

        connection.send(rsa.encrypt(msg.create_message(action="CT", arg1=self.nick, arg2=your_ct)))

        data = rsa.decrypt(connection.recv(self.buffer_size))
        data_json = msg.message_to_json(data)
        if data_json['action'] != "OK":
            print("no ok status after connection token")
            connection.close()

        self.connected_clients.append(Client(connection=connection, address=address, rsa=rsa, login=partner_user_nickname))

        while True:
            data = rsa.decrypt(connection.recv(self.buffer_size))
            data_json = msg.message_to_json(data)
            if data_json['action'] != "M":
                print("no M recived from client: ", partner_user_nickname)
                connection.close()
            else:
                print("recived msg from ", partner_user_nickname, " : ", data_json["message"])

    def client_server(self):
        print("client connecting")
        self.server.connect((self.master_server_ip, self.master_server_port))
        self.server.send(msg.create_message(action="HELLO"))
        public_key, private_key = enc.CryptoRSA.new_key()
        server_public_key = self.server.recv(self.buffer_size)
        self.rsa_server = enc.CryptoRSA(server_public_key, private_key)
        self.server.send(self.rsa_server.encrypt(public_key))
        data = self.rsa_server.decrypt(self.server.recv(self.buffer_size))
        data_json = msg.message_to_json(data)
        if data_json['action'] != "OK":
            print("no ok status after key exchange")
            self.server.close()

        action = ''
        while action != "L" and action != "R":
            action = (input("Login(L) or Register(R)")).upper()

        self.nick = input("Login: ")
        password = input("Password: ")

        login_register_msg = self.rsa_server.encrypt(
            msg.create_message(action=action, arg1=self.nick, arg2=password, arg3=self.client_port))
        self.server.send(login_register_msg)

        data = self.rsa_server.decrypt(self.server.recv(self.buffer_size))
        data_json = msg.message_to_json(data)
        if data_json['action'] != "OK":
            print("no ok status after login/register")
            self.server.close()

        threading.Thread(target=self.client_console, args=()).start()

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

    def update_contacts(self, friends, contacts):
        u_msg = self.rsa_server.encrypt(msg.create_message(action="UU", arg1=friends))
        self.server.send(u_msg)

        data = self.rsa_server.decrypt(self.server.recv(self.buffer_size))
        data_json = msg.message_to_json(data)
        ulist = data_json['ulist']

        for i in range(len(ulist)):
            contacts.update(ulist[i])

    def client_console(self):

        print("Now you can connect to other clients (write $help for more instruction)")
        command_list = ["$quit", "$exit", "$help", "$online", "$friends", "$add_friend", "$remove_friend, $connect", "$disconnect", "$send", "$clist"]
        friends = []
        contacts = {}
        command = ""
        while command != "$exit" and command != "$quit":
            command = input()
            if command == "$exit" or command == "$quit":
                print("The end is near")
                self.server.close()
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
                self.update_contacts(friends, contacts)
                for nick in contacts.keys():
                    print(nick)
            elif command == "$connect":
                self.update_contacts(friends, contacts)
                user = input("Connect to: ")
                if user in contacts.keys():
                    address = (contacts[user][0], contacts[user][1])
                    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    threading.Thread(target=self.client_to_client, args=(connection, address, user)).start()
                else:
                    print("Wrong user")
            elif command == "$disconnect":
                self.update_contacts(friends, contacts)
                user = input("Disconnect from: ")
                to_delete = None
                for ul in self.connected_clients:
                    if ul.login == user:
                        ul.connection.close()
                        to_delete = ul
                        print("closed connection to client: ", user)
                if to_delete is not None:
                    to_delete.connection.send(to_delete.rsa.encrypt(msg.create_message(action='OUT')))
                    to_delete.connection.close()
                    self.connected_clients.remove(to_delete)
                else:
                    print("Connection with user not found")
            elif command == "$send":
                self.update_contacts(friends, contacts)
                user = input("Message to: ")
                message = input("Message: ")
                to_send = None
                for ul in self.connected_clients:
                    if ul.login == user:
                        to_send = ul
                if to_send is not None:
                    to_send.connection.send(to_send.rsa.encrypt(msg.create_message("M", message)))
                    print("Msg sent to user: ", user)
                else:
                    print("Connection with user not found")
            elif command == "$clist":
                self.update_contacts(friends, contacts)
                print("Connections")
                for ul in self.connected_clients:
                    print(ul.login)
                print("Connections - end")