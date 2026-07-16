from Crypto.Cipher import AES
import hashlib
import base64


class AESOperation(object):
    def encrypt_string(self, password, input_string):
        # convert password string to bytes
        password = password.encode()
        # because AES is a block cipher,
        # the key has to be a standard length of either 16, 24 or 32 bytes
        # so here need to use sha256 to generate 32 bytes hash value
        key = hashlib.sha256(password).digest()
        # IV(initialization vector) also has to be 16 bytes(string length 16)
        cipher = AES.new(key, AES.MODE_CBC, 'This is an IV456'.encode("utf8"))
        # because AES is a block cipher, 126 bits cipher, 16 bytes,
        # the input that we put into tha algorithm has to be in 16 byte chunks as well
        # length of input_string needs to be times of 16
        padded_string = self.message_padding(input_string)
        encrypted = cipher.encrypt(padded_string.encode("utf8"))
        return encrypted

    def decrypt_string(self, password, input_string):
        password = password.encode()
        key = hashlib.sha256(password).digest()
        cipher = AES.new(key, AES.MODE_CBC, 'This is an IV456'.encode("utf8"))
        converted_bytes = base64.b64decode(input_string)
        decrypted = cipher.decrypt(self.bytes_padding(converted_bytes)).rstrip().decode()
        return decrypted

    def message_padding(self, message):
        while len(message) % 16 != 0:
            message += ' '
        return message

    def bytes_padding(self, message):
        while len(message) % 16 != 0:
            message += b'0'
        return message
