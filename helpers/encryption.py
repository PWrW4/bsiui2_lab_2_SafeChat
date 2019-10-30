from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP


def new_key(length=1024, passphrase=None):
    key = RSA.generate(length)
    pub_key = key.publickey().exportKey('PEM', passphrase)
    priv_key = key.exportKey('PEM', passphrase)
    return pub_key, priv_key


def decrypt(priv_key, msg):
    decryptor = PKCS1_OAEP.new(RSA.importKey(priv_key))
    if type(msg) == str:
        msg = decryptor.decrypt(msg).decode()
    if type(msg) == bytes:
        msg = decryptor.decrypt(msg)

    return msg


def encrypt(pub_key, msg):
    encryptor = PKCS1_OAEP.new(RSA.importKey(pub_key))
    if type(msg) == str:
        msg = encryptor.encrypt(msg.encode())
    if type(msg) == bytes:
        msg = encryptor.encrypt(msg)
    return msg
