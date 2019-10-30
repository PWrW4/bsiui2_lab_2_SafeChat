from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP


def new_key(length: int = 2048, passphrase: str = None):
    key = RSA.generate(length)
    pub_key = key.publickey().exportKey('PEM', passphrase)
    priv_key = key.exportKey('PEM', passphrase)
    return pub_key, priv_key


def decrypt(priv_key: bytes, msg: bytes):
    decryptor = PKCS1_OAEP.new(RSA.importKey(priv_key))
    list_of_package = [msg[i:i + 256] for i in range(0, len(msg), 256)]  # dzielenie po 256 bajtów
    for x in range(len(list_of_package)):
        list_of_package[x] = decryptor.decrypt(list_of_package[x])
    msg = b''.join(list_of_package)
    return msg.decode()


def encrypt(pub_key: bytes, msg):
    encryptor = PKCS1_OAEP.new(RSA.importKey(pub_key))
    if type(msg) == str:
        msg = msg.encode()
    list_of_package = [msg[i:i + 100] for i in range(0, len(msg), 100)]  # dzielenie po 100 bajtów
    for x in range(len(list_of_package)):  # szyfrowanie kazdej paczki 100 bajtów
        list_of_package[x] = encryptor.encrypt(list_of_package[x])
    msg = b''.join(list_of_package)  # laczenie w jeden ciag bitow kazdej zaszyfrowanej paczki
    return msg