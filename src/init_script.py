from client.client import Client
from server.server import MasterServer

TCP_IP = '127.0.0.1'
TCP_PORT = 2138
BUFFER_SIZE = 1024

ms = MasterServer(master_server_ip=TCP_IP, master_server_port=TCP_PORT, buffer_size=BUFFER_SIZE)
c = Client(master_server_ip=TCP_IP, master_server_port=TCP_PORT, buffer_size=BUFFER_SIZE)
