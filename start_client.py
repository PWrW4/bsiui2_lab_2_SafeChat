import os
from client.client import Client
from dotenv import load_dotenv
load_dotenv()

c = Client(master_server_ip=os.getenv("TCP_IP"), master_server_port=os.getenv("TCP_PORT"), buffer_size=os.getenv("BUFFER_SIZE "))
