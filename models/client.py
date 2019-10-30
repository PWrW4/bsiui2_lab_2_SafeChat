class Client:
    def __init__(self, client_id, address):
        self.client_id = client_id
        self.address = address
        self.login = None
        self.password = None
        self.status = None
        self.public_key = None
        self.private_key = None
