from enum import Enum


class ClientStatus(Enum):
    CONNECTED = 1
    CONNECTING = 2
    LOGGED_IN = 3
