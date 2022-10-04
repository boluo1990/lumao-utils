from web3 import Web3
from cryptography.fernet import Fernet

class Luencryption:
    def __init__(self, encrypt_key) -> None:
        self.fernet = Fernet(encrypt_key)

    @staticmethod
    def to_bytes(string):
        return Web3.toBytes(text=string)

    @staticmethod
    def to_string(bytes):
        return Web3.toText(bytes)

    def encrypt(self, to_encrypt_string):
        if isinstance(to_encrypt_string, str):
            if to_encrypt_string == '':
                return ''
            to_encrypt_bytes = self.to_bytes(to_encrypt_string)
            encrypted_bytes = self.fernet.encrypt(to_encrypt_bytes)
            return self.to_string(encrypted_bytes)
        else:
            print(f"传参错误, 参数类型必须为string, 实际为: {type(to_encrypt_string)}")

    def decrypt(self, to_decrypt_string):
        if isinstance(to_decrypt_string, str):
            if to_decrypt_string == '':
                return ''
            to_decrypt_bytes = self.to_bytes(to_decrypt_string)
            decrypted_bytes = self.fernet.decrypt(to_decrypt_bytes)
            return self.to_string(decrypted_bytes)
        else:
            print(f"传参错误, 参数类型必须为string, 实际为: {type(to_decrypt_bytes)}")