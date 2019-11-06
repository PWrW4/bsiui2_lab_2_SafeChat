import os
from server.server_app import ServerApp
from dotenv import load_dotenv

load_dotenv()

ip = str(os.getenv("TCP_IP"))
port = int(os.getenv("TCP_PORT"))
buffer_size = int(os.getenv("BUFFER_SIZE"))
username_salt = (str(os.getenv("USERNAME_SALT")))
token_salt = (str(os.getenv("TOKEN_SALT")))

print("IP: ", ip, "PORT: ", port, "BUFFER_SIZE: ", buffer_size)

ms = ServerApp(master_server_ip=ip,
               master_server_port=port,
               buffer_size=buffer_size,
               username_salt=username_salt,
               token_salt=token_salt
               )
