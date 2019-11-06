from models.server_client_status import ClientStatus


class Client:
    def __init__(self, client_id, address, connection):
        self.client_id = client_id
        self.address = address
        self.connection = connection
        self.status = ClientStatus.CONNECTING
        self.login = None
        self.listen_port = None
