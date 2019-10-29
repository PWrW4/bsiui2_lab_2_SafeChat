from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP


def new_key(length=1024, passphrase=None):
    key = RSA.generate(length)
    pub_key = key.publickey().exportKey('PEM', passphrase)
    priv_key = key.exportKey('PEM', passphrase)
    return pub_key, priv_key


def decrypt(priv_key, msg):
    decryptor = PKCS1_OAEP.new(RSA.importKey(priv_key))
    msg = decryptor.decrypt(msg).decode()
    return msg


def encrypt(pub_key, msg):
    encryptor = PKCS1_OAEP.new(RSA.importKey(pub_key))
    msg = encryptor.encrypt(msg.encode())
    return msg
