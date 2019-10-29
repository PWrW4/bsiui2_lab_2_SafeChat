import os
from server.server import MasterServer
from dotenv import load_dotenv

load_dotenv()

ip = str(os.getenv("TCP_IP"))
port = int(os.getenv("TCP_PORT"))
buffer_size = int(os.getenv("BUFFER_SIZE"))

print("IP: ", ip, "PORT: ", port, "BUFFER_SIZE: ", buffer_size)

ms = MasterServer(master_server_ip=ip, master_server_port=port, buffer_size=buffer_size)
