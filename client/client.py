import socket
import helpers.message as msg
import helpers.encryption as enc


class Client:
    def __init__(self, master_server_ip, master_server_port, buffer_size):
        self.buffer_size = buffer_size
        self.master_server_ip = master_server_ip
        self.master_server_port = master_server_port
        print("client connecting")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.master_server_ip, self.master_server_port))
        s.send(msg.create_message(action="HELLO"))
        public_key, private_key = enc.new_key()
        server_public_key = s.recv(self.buffer_size)
        s.send(public_key)
        data = s.recv(self.buffer_size)
        data_json = msg.measage_to_json(data)
        if data_json['action'] != "OK":
            print("no ok status after key exchange")
            s.close()

        action = ''
        while action != "L" and "R":
            action = input("Login(L) or Register(R)")

        login = input("Login: ")
        password = input("Password: ")

        login_register_msg = msg.create_message(action=action, arg1=login, arg2=password)
        s.send(login_register_msg)

        if data:
            print("client received data:", data.decode('utf-8'))
        else:
            print("no data")
        s.close()
